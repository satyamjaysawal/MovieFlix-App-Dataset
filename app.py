import os
import json
import uuid
import traceback
from math import ceil
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

load_dotenv()

# Base directory — always resolves correctly on Vercel serverless too
BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="MovieFlix")

# Secret key for session management
secret_key = os.getenv('SECRET_KEY', 'movieflix-super-secret-key-12345')
app.add_middleware(SessionMiddleware, secret_key=secret_key)

# NOTE: Static files are served by Vercel's @vercel/static builder directly.
# Do NOT mount StaticFiles here — it crashes Vercel serverless cold starts.

# Setup Jinja2 templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# Reviews persistence file
REVIEWS_FILE = BASE_DIR / "reviews.json"

# In-memory reviews fallback for read-only filesystems (e.g. Vercel)
_memory_reviews = {}

def load_reviews():
    global _memory_reviews
    if _memory_reviews:
        return _memory_reviews
    try:
        if REVIEWS_FILE.exists():
            with open(REVIEWS_FILE, 'r', encoding='utf-8') as f:
                _memory_reviews = json.load(f)
                return _memory_reviews
    except Exception:
        pass
    return {}

def save_reviews(reviews):
    global _memory_reviews
    _memory_reviews = reviews
    try:
        with open(REVIEWS_FILE, 'w', encoding='utf-8') as f:
            json.dump(reviews, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Note: Reviews stored in memory only (read-only filesystem): {e}")


# Flash message utilities
def flash(request: Request, message: str, category: str = "success"):
    if "flash_messages" not in request.session:
        request.session["flash_messages"] = []
    request.session["flash_messages"].append({"message": message, "category": category})

def get_flashed_messages(request: Request):
    return request.session.pop("flash_messages", [])

# Register flash messages in Jinja global context
templates.env.globals["get_flashed_messages"] = get_flashed_messages

# Load movies dataset using absolute path
_startup_error = None
movies_df = None
try:
    csv_path = BASE_DIR / "MovieDataSet.csv"
    print(f"Loading CSV from: {csv_path} (exists={csv_path.exists()})")
    movies_df = pd.read_csv(str(csv_path))
    default_image_url = "https://github.com/user-attachments/assets/eea04eb6-fdb8-477f-99b8-e4b2150c7421"

    # Prepare dataset fields
    movies_df['Genre'] = movies_df['Genre'].apply(lambda x: [g.strip() for g in x.split(',')] if isinstance(x, str) else [])

    # Handle Movie Poster fallbacks
    if 'Movie-Image-Url' not in movies_df.columns:
        movies_df['Movie-Image-Url'] = default_image_url
    else:
        movies_df['Movie-Image-Url'] = movies_df['Movie-Image-Url'].apply(
            lambda x: x if pd.notna(x) and str(x).strip() else default_image_url
        )

    # Fill other NaN fields
    movies_df['Description'] = movies_df['Description'].fillna('')
    movies_df['Actors'] = movies_df['Actors'].fillna('')
    movies_df['Director'] = movies_df['Director'].fillna('')
    movies_df['Rating'] = movies_df['Rating'].fillna(0.0)
    movies_df['Votes'] = movies_df['Votes'].fillna(0)
    movies_df['Revenue (Millions)'] = movies_df['Revenue (Millions)'].fillna(0.0)
    movies_df['Metascore'] = movies_df['Metascore'].fillna(0)
except Exception as e:
    _startup_error = traceback.format_exc()
    print(f"STARTUP ERROR: {_startup_error}")

default_image_url = "https://github.com/user-attachments/assets/eea04eb6-fdb8-477f-99b8-e4b2150c7421"

# Debug endpoint — shows startup errors on Vercel
@app.get("/debug")
def debug_info():
    files_in_base = [str(p) for p in BASE_DIR.iterdir()] if BASE_DIR.exists() else []
    return HTMLResponse(f"""
    <pre>
BASE_DIR: {BASE_DIR}
BASE_DIR exists: {BASE_DIR.exists()}
CSV exists: {(BASE_DIR / 'MovieDataSet.csv').exists()}
templates exists: {(BASE_DIR / 'templates').exists()}
static exists: {(BASE_DIR / 'static').exists()}
files: {chr(10).join(files_in_base)}
startup_error: {_startup_error or 'None'}
    </pre>
    """)


@app.get("/")
def home(request: Request, page: int = Query(default=1)):
    # Sort all movies by Year desc, then Rating desc
    sorted_movies = movies_df.sort_values(by=['Year', 'Rating'], ascending=[False, False]).to_dict(orient='records')
    
    per_page = 16
    total_movies = len(sorted_movies)
    total_pages = ceil(total_movies / per_page) if total_movies > 0 else 1

    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages

    start = (page - 1) * per_page
    end = start + per_page
    paginated_movies = sorted_movies[start:end]

    pagination = {
        'current_page': page,
        'total_pages': total_pages,
        'prev_page': page - 1 if page > 1 else None,
        'next_page': page + 1 if page < total_pages else None
    }

    movie_reviews = load_reviews()

    return templates.TemplateResponse("home.html", {
        "request": request,
        "latest_movies": paginated_movies,
        "pagination": pagination,
        "movie_reviews": movie_reviews
    })

@app.get("/genres")
def genres_index(request: Request, genres: list[str] = Query(default=[]), page: int = 1):
    all_genres = set()
    for genre_list in movies_df['Genre']:
        all_genres.update(genre_list)

    selected_genres = [g.lower() for g in genres]

    filtered_movies = []
    if selected_genres:
        for _, movie in movies_df.iterrows():
            movie_genres = [g.lower() for g in movie['Genre']]
            if any(sel in movie_genres for sel in selected_genres):
                filtered_movies.append(movie.to_dict())

        # Sort: movies matching more selected genres first
        filtered_movies.sort(
            key=lambda m: len([sel for sel in selected_genres if sel in [g.lower() for g in m['Genre']]]),
            reverse=True
        )

    per_page = 16
    total_movies = len(filtered_movies)
    total_pages = ceil(total_movies / per_page) if total_movies > 0 else 1

    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages

    start = (page - 1) * per_page
    end = start + per_page
    paginated_movies = filtered_movies[start:end]

    pagination = {
        'current_page': page,
        'total_pages': total_pages,
        'prev_page': page - 1 if page > 1 else None,
        'next_page': page + 1 if page < total_pages else None
    }

    movie_reviews = load_reviews()

    return templates.TemplateResponse("genre.html", {
        "request": request,
        "genres": sorted(all_genres),
        "filtered_movies": paginated_movies,
        "selected_genres": selected_genres,
        "pagination": pagination,
        "movie_reviews": movie_reviews
    })

@app.get("/popular_trending")
def popular_trending(request: Request):
    top_rated_df = movies_df.nlargest(12, 'Votes')[[ 'Title', 'Rating', 'Votes', 'Revenue (Millions)', 'Movie-Image-Url', 'Genre', 'Year', 'Director']]
    top_revenue_df = movies_df.nlargest(12, 'Revenue (Millions)')[[ 'Title', 'Rating', 'Votes', 'Revenue (Millions)', 'Movie-Image-Url', 'Genre', 'Year', 'Director']]

    top_rated_movies = top_rated_df.to_dict(orient='records')
    top_revenue_movies = top_revenue_df.to_dict(orient='records')

    movie_reviews = load_reviews()

    return templates.TemplateResponse("popular_trending.html", {
        "request": request,
        "top_rated_movies": top_rated_movies,
        "top_revenue_movies": top_revenue_movies,
        "movie_reviews": movie_reviews
    })

@app.get("/search")
def search(request: Request, query: str = ""):
    query_clean = query.strip().lower()
    search_results = []
    if query_clean:
        for _, movie in movies_df.iterrows():
            title_match = query_clean in str(movie['Title']).lower()
            description_match = query_clean in str(movie['Description']).lower()
            if title_match or description_match:
                search_results.append(movie.to_dict())

    movie_reviews = load_reviews()
    return templates.TemplateResponse("search.html", {
        "request": request,
        "search_results": search_results,
        "movie_reviews": movie_reviews,
        "query": query
    })

@app.post("/submit_review")
def submit_review(
    request: Request,
    movie_title: str = Form(...),
    rating: int = Form(...),
    review: str = Form(...),
    username: str = Form("Anonymous")
):
    referrer = request.headers.get("referer", "/genres")

    reviews = load_reviews()
    review_id = str(uuid.uuid4())

    if movie_title not in reviews:
        reviews[movie_title] = {}
    
    reviews[movie_title][review_id] = {
        'username': username.strip() if username.strip() else "Anonymous",
        'rating': rating,
        'review': review
    }
    
    save_reviews(reviews)
    flash(request, f"Your review for '{movie_title}' has been submitted successfully!", "success")

    return RedirectResponse(url=referrer, status_code=303)

@app.get("/analytics")
def analytics(request: Request):
    # 1. Genre Analysis
    genre_counts = {}
    genre_revenue = {}
    for _, row in movies_df.iterrows():
        genres = row['Genre']
        rev = row['Revenue (Millions)']
        for g in genres:
            genre_counts[g] = genre_counts.get(g, 0) + 1
            if rev > 0:
                if g not in genre_revenue:
                    genre_revenue[g] = []
                genre_revenue[g].append(rev)
    
    genre_labels = sorted(list(genre_counts.keys()))
    genre_movie_counts = [genre_counts[g] for g in genre_labels]
    genre_avg_revenues = [
        round(sum(genre_revenue[g]) / len(genre_revenue[g]), 2) if g in genre_revenue else 0.0 
        for g in genre_labels
    ]

    # 2. Yearly Trends
    yearly_stats = {}
    for _, row in movies_df.iterrows():
        y = int(row['Year'])
        rating = row['Rating']
        rev = row['Revenue (Millions)']
        if y not in yearly_stats:
            yearly_stats[y] = {'rating': [], 'revenue': [], 'count': 0}
        yearly_stats[y]['rating'].append(rating)
        if rev > 0:
            yearly_stats[y]['revenue'].append(rev)
        yearly_stats[y]['count'] += 1

    sorted_years = sorted(yearly_stats.keys())
    yearly_labels = [str(y) for y in sorted_years]
    yearly_ratings = [
        round(sum(yearly_stats[y]['rating']) / len(yearly_stats[y]['rating']), 2) 
        for y in sorted_years
    ]
    yearly_revenues = [
        round(sum(yearly_stats[y]['revenue']) / len(yearly_stats[y]['revenue']), 2) if yearly_stats[y]['revenue'] else 0.0 
        for y in sorted_years
    ]

    # 3. IMDb Rating vs Metascore Scatter
    scatter_data = []
    # Sample a diverse selection of 150 movies with valid Metascore to avoid canvas bloating
    sampled_df = movies_df[movies_df['Metascore'] > 0].head(150)
    for _, row in sampled_df.iterrows():
        scatter_data.append({
            'x': float(row['Rating']),
            'y': int(row['Metascore']),
            'title': str(row['Title'])
        })

    # 4. Top 5 Directors by Average Revenue
    director_rev = {}
    for _, row in movies_df.iterrows():
        d = row['Director']
        rev = row['Revenue (Millions)']
        if d and rev > 0:
            if d not in director_rev:
                director_rev[d] = []
            director_rev[d].append(rev)

    director_avg_rev = {}
    for d, rev_list in director_rev.items():
        director_avg_rev[d] = sum(rev_list) / len(rev_list)

    top_directors = sorted(director_avg_rev.items(), key=lambda x: x[1], reverse=True)[:5]
    director_labels = [x[0] for x in top_directors]
    director_values = [round(x[1], 2) for x in top_directors]

    return templates.TemplateResponse("analytics.html", {
        "request": request,
        "genre_labels": genre_labels,
        "genre_movie_counts": genre_movie_counts,
        "genre_avg_revenues": genre_avg_revenues,
        "yearly_labels": yearly_labels,
        "yearly_ratings": yearly_ratings,
        "yearly_revenues": yearly_revenues,
        "scatter_data": scatter_data,
        "director_labels": director_labels,
        "director_values": director_values
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
