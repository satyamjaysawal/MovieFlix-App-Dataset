import os
from flask import Flask, session, render_template, request, redirect, url_for, flash
import pandas as pd
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from math import ceil
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
from datetime import timedelta 

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['SESSION_TYPE'] = 'filesystem'
app.permanent_session_lifetime = timedelta(minutes=45)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

client = MongoClient(os.getenv('MONGODB_URI'))
db = client['movie_database']
users_collection = db['users']
reviews_collection = db['reviews']

movies_df = pd.read_csv('MovieDataSet.csv')

default_image_url = "https://github.com/user-attachments/assets/eea04eb6-fdb8-477f-99b8-e4b2150c7421"

movies_df['Genre'] = movies_df['Genre'].apply(lambda x: x.split(','))

if 'Movie-Image-Url' not in movies_df.columns:
    movies_df['Movie-Image-Url'] = default_image_url
else:
    movies_df['Movie-Image-Url'] = movies_df['Movie-Image-Url'].apply(
        lambda x: x if pd.notna(x) and x.strip() else default_image_url
    )

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return User(str(user['_id']))
    return None

@app.route('/')
def home():
    if current_user.is_authenticated:
        user = users_collection.find_one({"_id": ObjectId(current_user.id)})
        username = user['username'] if user else None
        return render_template('home.html', username=username)
    else:
        return render_template('home.html', username=None)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if users_collection.find_one({"username": username}):
            flash("Username already exists! Please choose another.", 'danger')
            return redirect(url_for('register'))
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        users_collection.insert_one({"username": username, "password": hashed_password})
        flash("Registration successful! Please log in.", 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users_collection.find_one({"username": username})
        if user and bcrypt.check_password_hash(user['password'], password):
            user_obj = User(str(user['_id']))
            login_user(user_obj)
             # Make the session permanent
            session.permanent = True
            flash("Login successful!", 'login')
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password. Please try again.", 'login')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()  # Manually clear the session
    logout_user()
    flash("You have been logged out.", 'logout')
    return redirect(url_for('home'))

@app.route('/genres', methods=['GET'])
@login_required
def index():
    genres = set()
    for genre_list in movies_df['Genre']:
        genres.update(genre.strip() for genre in genre_list)

    selected_genres = request.args.getlist('genres')
    selected_genres = [genre.lower() for genre in selected_genres]

    filtered_movies = []
    if selected_genres:
        for _, movie in movies_df.iterrows():
            movie_genres = [genre.strip().lower() for genre in movie['Genre']]
            if any(sel in movie_genres for sel in selected_genres):
                filtered_movies.append(movie)

    filtered_movies.sort(key=lambda movie: len([sel for sel in selected_genres if sel in [g.lower() for g in movie['Genre']]]), reverse=True)

    page = request.args.get('page', 1, type=int)
    per_page = 16
    total_movies = len(filtered_movies)
    total_pages = ceil(total_movies / per_page)

    start = (page - 1) * per_page
    end = start + per_page
    paginated_movies = filtered_movies[start:end]

    pagination = {
        'current_page': page,
        'total_pages': total_pages,
        'prev_page': page - 1 if page > 1 else None,
        'next_page': page + 1 if page < total_pages else None
    }

    movie_reviews = {review['movie_title']: review['reviews'] for review in reviews_collection.find()}

    return render_template('genre.html', 
                           genres=sorted(genres), 
                           filtered_movies=paginated_movies, 
                           selected_genres=selected_genres, 
                           pagination=pagination,
                           movie_reviews=movie_reviews)

@app.route('/popular_trending', methods=['GET'])
@login_required
def popular_trending():
    top_rated_movies = movies_df.nlargest(12, 'Votes')[[ 'Title', 'Rating', 'Votes', 'Revenue (Millions)', 'Movie-Image-Url', 'Genre', 'Year', 'Director']]
    top_revenue_movies = movies_df.nlargest(12, 'Revenue (Millions)')[[ 'Title', 'Rating', 'Votes', 'Revenue (Millions)', 'Movie-Image-Url', 'Genre', 'Year', 'Director']]

    return render_template('popular_trending.html', 
                           top_rated_movies=top_rated_movies, 
                           top_revenue_movies=top_revenue_movies)

@app.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('query', '').lower()

    search_results = []
    if query:
        for _, movie in movies_df.iterrows():
            title_match = query in movie['Title'].lower()
            description_match = query in movie['Description'].lower() if pd.notna(movie['Description']) else False
            if title_match or description_match:
                search_results.append(movie.to_dict())

    # Fetch movie reviews
    movie_reviews = {review['movie_title']: review['reviews'] for review in reviews_collection.find()}

    return render_template('search.html', search_results=search_results, movie_reviews=movie_reviews)

@app.route('/submit_review', methods=['POST'])
@login_required
def submit_review():
    movie_title = request.form['movie_title']
    rating = int(request.form['rating'])
    review = request.form['review']

    movie_review = reviews_collection.find_one({"movie_title": movie_title})

    if movie_review:
        if current_user.id in movie_review['reviews']:
            flash(f"You have already reviewed '{movie_title}'. Edit or delete your review instead.", 'warning')
        else:
            movie_review['reviews'][current_user.id] = {'rating': rating, 'review': review}
            reviews_collection.update_one({"movie_title": movie_title}, {"$set": {"reviews": movie_review['reviews']}})
            flash(f"Your review for '{movie_title}' has been submitted successfully!", 'success')
    else:
        reviews_collection.insert_one({
            "movie_title": movie_title,
            "reviews": {
                current_user.id: {'rating': rating, 'review': review}
            }
        })
        flash(f"Your review for '{movie_title}' has been submitted successfully!", 'success')

    return redirect(request.referrer)  # Redirects back to the same page the user came from


@app.route('/edit_review', methods=['POST'])
@login_required
def edit_review():
    movie_title = request.form['movie_title']
    rating = int(request.form['rating'])
    review = request.form['review']

    movie_review = reviews_collection.find_one({"movie_title": movie_title})

    if movie_review and current_user.is_authenticated:
        if current_user.id in movie_review['reviews']:
            movie_review['reviews'][current_user.id]['rating'] = rating
            movie_review['reviews'][current_user.id]['review'] = review
            reviews_collection.update_one({"movie_title": movie_title}, {"$set": {"reviews": movie_review['reviews']}})
            flash(f"Your review for '{movie_title}' has been updated successfully!", 'success')
        else:
            flash("You haven't reviewed this movie yet. Please submit a review first.", 'danger')
    else:
        flash("Could not find the movie or you are not logged in.", 'danger')

    return redirect(request.referrer)

@app.route('/delete_review', methods=['POST'])
@login_required
def delete_review():
    movie_title = request.form['movie_title']

    movie_review = reviews_collection.find_one({"movie_title": movie_title})

    if movie_review and current_user.id in movie_review['reviews']:
        del movie_review['reviews'][current_user.id]
        if movie_review['reviews']:
            reviews_collection.update_one({"movie_title": movie_title}, {"$set": {"reviews": movie_review['reviews']}})
        else:
            reviews_collection.delete_one({"movie_title": movie_title})
        flash(f"Your review for '{movie_title}' has been deleted successfully!", 'success')
    else:
        flash("You haven't reviewed this movie yet.", 'danger')

    return redirect(request.referrer)

if __name__ == '__main__':
    app.run(debug=True)
