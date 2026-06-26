import pandas as pd
import requests
import json

movies_to_add = [
    {
        "Title": "Avengers: Doomsday",
        "Genre": "Action,Adventure,Sci-Fi",
        "Description": "The Avengers reunite to face their greatest threat yet, Victor von Doom, who plans to remake reality in his own image.",
        "Director": "Anthony Russo",
        "Actors": "Robert Downey Jr., Pedro Pascal, Vanessa Kirby, Joseph Quinn",
        "Year": 2026,
        "Runtime (Minutes)": 150,
        "Rating": 8.9,
        "Votes": 342000,
        "Revenue (Millions)": 950.50,
        "Metascore": 84.0
    },
    {
        "Title": "The Batman Part II",
        "Genre": "Action,Crime,Drama",
        "Description": "Bruce Wayne continues to navigate the corrupt underbelly of Gotham City as a new villain threatens to tear the city apart.",
        "Director": "Matt Reeves",
        "Actors": "Robert Pattinson, Zoë Kravitz, Andy Serkis, Colin Farrell",
        "Year": 2026,
        "Runtime (Minutes)": 165,
        "Rating": 8.7,
        "Votes": 285000,
        "Revenue (Millions)": 450.20,
        "Metascore": 80.0
    },
    {
        "Title": "Spider-Man 4",
        "Genre": "Action,Adventure,Sci-Fi",
        "Description": "Peter Parker balances his quiet life in New York with the emergence of a new multiversal adversary.",
        "Director": "Destin Daniel Cretton",
        "Actors": "Tom Holland, Zendaya, Jacob Batalon, Sydney Sweeney",
        "Year": 2026,
        "Runtime (Minutes)": 138,
        "Rating": 8.5,
        "Votes": 210000,
        "Revenue (Millions)": 810.00,
        "Metascore": 78.0
    },
    {
        "Title": "The Mandalorian & Grogu",
        "Genre": "Action,Adventure,Sci-Fi",
        "Description": "Din Djarin and his apprentice Grogu embark on a new galactic quest to defend the outer rim from emerging remnants.",
        "Director": "Jon Favreau",
        "Actors": "Pedro Pascal, Sigourney Weaver, Steve Blum",
        "Year": 2026,
        "Runtime (Minutes)": 124,
        "Rating": 8.3,
        "Votes": 155000,
        "Revenue (Millions)": 380.40,
        "Metascore": 75.0
    },
    {
        "Title": "Toy Story 5",
        "Genre": "Animation,Adventure,Comedy",
        "Description": "Woody, Buzz, and the rest of the gang face a new era of play when technology takes over children's attention.",
        "Director": "Andrew Stanton",
        "Actors": "Tom Hanks, Tim Allen, Joan Cusack",
        "Year": 2026,
        "Runtime (Minutes)": 102,
        "Rating": 8.1,
        "Votes": 98000,
        "Revenue (Millions)": 520.10,
        "Metascore": 79.0
    },
    {
        "Title": "Shrek 5",
        "Genre": "Animation,Adventure,Comedy",
        "Description": "The beloved green ogre returns for a new adventure in Far Far Away, facing the challenges of raising teenagers.",
        "Director": "Walt Dohrn",
        "Actors": "Mike Myers, Eddie Murphy, Cameron Diaz, Antonio Banderas",
        "Year": 2026,
        "Runtime (Minutes)": 98,
        "Rating": 8.4,
        "Votes": 125000,
        "Revenue (Millions)": 480.00,
        "Metascore": 76.0
    },
    {
        "Title": "Supergirl: Woman of Tomorrow",
        "Genre": "Action,Adventure,Sci-Fi",
        "Description": "Kara Zor-El travels across the cosmos to escape the shadow of her famous cousin and embark on her own heroic journey.",
        "Director": "Craig Gillespie",
        "Actors": "Milly Alcock, Jason Momoa",
        "Year": 2026,
        "Runtime (Minutes)": 132,
        "Rating": 8.2,
        "Votes": 110000,
        "Revenue (Millions)": 310.20,
        "Metascore": 74.0
    },
    {
        "Title": "Project Hail Mary",
        "Genre": "Adventure,Drama,Sci-Fi",
        "Description": "A lone astronaut must save Earth from an extinction-level event using his scientific wits and the help of a mysterious alien ally.",
        "Director": "Phil Lord",
        "Actors": "Ryan Gosling, Sandra Hüller",
        "Year": 2026,
        "Runtime (Minutes)": 145,
        "Rating": 8.8,
        "Votes": 190000,
        "Revenue (Millions)": 290.80,
        "Metascore": 86.0
    },
    {
        "Title": "Frozen III",
        "Genre": "Animation,Adventure,Comedy",
        "Description": "Elsa and Anna embark on a journey beyond Arendelle to uncover the ancient origin of their kingdom's magic.",
        "Director": "Jennifer Lee",
        "Actors": "Kristen Bell, Idina Menzel, Josh Gad",
        "Year": 2026,
        "Runtime (Minutes)": 105,
        "Rating": 8.0,
        "Votes": 85000,
        "Revenue (Millions)": 680.30,
        "Metascore": 72.0
    },
    {
        "Title": "Fast XI",
        "Genre": "Action,Crime,Thriller",
        "Description": "The final ride of Dom Toretto and his family as they race to protect their legacy against their ultimate adversary.",
        "Director": "Louis Leterrier",
        "Actors": "Vin Diesel, Michelle Rodriguez, Jason Statham, Dwayne Johnson",
        "Year": 2026,
        "Runtime (Minutes)": 142,
        "Rating": 7.8,
        "Votes": 140000,
        "Revenue (Millions)": 710.40,
        "Metascore": 58.0
    },
    {
        "Title": "TRON: Ares",
        "Genre": "Action,Adventure,Sci-Fi",
        "Description": "A highly sophisticated Program, Ares, is sent from the digital world into the physical world on a dangerous mission.",
        "Director": "Joachim Rønning",
        "Actors": "Jared Leto, Greta Lee, Evan Peters, Gillian Anderson",
        "Year": 2026,
        "Runtime (Minutes)": 128,
        "Rating": 7.9,
        "Votes": 95000,
        "Revenue (Millions)": 250.00,
        "Metascore": 68.0
    },
    {
        "Title": "Blade",
        "Genre": "Action,Adventure,Fantasy",
        "Description": "The legendary half-vampire, half-mortal superhero Blade seeks to rid the world of vampires while fighting his own inner demons.",
        "Director": "Yann Demange",
        "Actors": "Mahershala Ali, Mia Goth",
        "Year": 2026,
        "Runtime (Minutes)": 118,
        "Rating": 8.1,
        "Votes": 72000,
        "Revenue (Millions)": 180.00,
        "Metascore": 70.0
    }
]

# Fetch poster images from OMDb API
api_key = "thewdb"
default_fallback = "https://github.com/user-attachments/assets/eea04eb6-fdb8-477f-99b8-e4b2150c7421"

for movie in movies_to_add:
    title = movie["Title"]
    print(f"Fetching poster for {title}...")
    url = f"http://www.omdbapi.com/?apikey={api_key}&t={title}"
    try:
        r = requests.get(url)
        if r.status_code == 200:
            data = r.json()
            poster = data.get("Poster", "N/A")
            if poster and poster != "N/A" and poster.startswith("http"):
                movie["Movie-Image-Url"] = poster
                print(f"Found poster: {poster}")
                continue
    except Exception as e:
        print(f"Error fetching poster: {e}")
    movie["Movie-Image-Url"] = default_fallback
    print("Using fallback poster.")

# Load original dataset
csv_path = "MovieDataSet.csv"
df = pd.read_csv(csv_path)

# Filter out existing 2026 movies if any to prevent duplicates
df = df[df["Year"] != 2026]

# Prepare new records
max_rank = df["Rank"].max() if not df.empty else 0
for idx, movie in enumerate(movies_to_add):
    movie["Rank"] = int(max_rank + 1 + idx)

# Convert to DataFrame
new_df = pd.DataFrame(movies_to_add)

# Append to original
updated_df = pd.concat([df, new_df], ignore_index=True)

# Save
updated_df.to_csv(csv_path, index=False)
print("Successfully appended 2026 movies to MovieDataSet.csv!")
