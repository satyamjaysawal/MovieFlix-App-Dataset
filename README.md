

# MovieFlix

MovieFlix is a web application built using Flask that allows users to explore movies, search for titles, and submit reviews. The app allows users to filter movies by genre, view popular and trending movies, and manage their movie reviews.

## Features

- **User Authentication:**
  - Users can register, log in, and log out securely.
  - Passwords are hashed using `Bcrypt` for security.

- **Movie Exploration:**
  - Browse movies by genres.
  - Search movies by title or description.
  - View movie details such as title, rating, director, revenue, and more.
  
- **Movie Reviews:**
  - Users can submit reviews for movies.
  - Users can edit or delete their reviews.
  - Reviews are associated with users and can only be edited or deleted by the reviewer.

- **Trending Movies:**
  - Displays the top-rated movies based on user votes.
  - Displays the top-grossing movies based on revenue.

## Technologies Used

- **Flask** - A lightweight Python web framework used to build the application.
- **Flask-Bcrypt** - For password hashing and validation.
- **Flask-Login** - For user session management.
- **Pandas** - For handling and processing movie data.
- **Bootstrap** - For responsive front-end design.
- **Font Awesome** - For icons.

## Installation

### Prerequisites

- Python 3.x
- `pip` (Python package manager)

### Steps

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/yourusername/movieflix.git
   cd movieflix
   ```

2. Create and activate a virtual environment:

   On Windows:

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

   On macOS/Linux:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Make sure you have the `MovieDataset.csv` file (with movie data) in the same directory as your project, or update the path in the code.

5. Run the Flask application:

   ```bash
   python app.py
   ```

   The application will be available at `http://127.0.0.1:5000/`.

## Usage

1. Visit the homepage and register or log in.
2. Browse movies by selecting genres or use the search functionality.
3. View popular and trending movies based on ratings and revenue.
4. Submit, edit, or delete your movie reviews.

## File Structure

- `app.py`: The main Flask application code.
- `MovieDataset.csv`: The CSV file containing movie data.
- `templates/`: Directory containing HTML templates for the application.
  - `home.html`: Homepage template.
  - `register.html`: Registration page template.
  - `login.html`: Login page template.
  - `genre.html`: Template to view and filter movies by genre.
  - `search.html`: Template to display search results.
  - `popular_trending.html`: Template to display trending movies.
- `static/`: Directory containing static files (CSS, JavaScript, images, etc.).
- `requirements.txt`: The Python dependencies required to run the application.

## Contributing

Feel free to fork this project and submit pull requests. If you encounter any bugs or have ideas for new features, please open an issue.
