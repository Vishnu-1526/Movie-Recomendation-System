"""Movie Recommendation System """

import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load dataset (script-relative path)
script_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(script_dir, 'dataset.csv')

if not os.path.exists(dataset_path):
    raise FileNotFoundError(f"dataset.csv not found in {script_dir}")

movies = pd.read_csv(dataset_path)

# Prepare dataset
movies['tags'] = movies['genre'].astype(str) + " " + movies['overview'].astype(str)
new_df = movies[['id', 'title', 'tags']]

# Lowercase titles for easier matching
new_df['title_lower'] = new_df['title'].str.lower()

# Vectorization
cv = CountVectorizer(max_features=10000, stop_words='english')
vec = cv.fit_transform(new_df['tags'].values.astype('U')).toarray()

# Cosine similarity
sim = cosine_similarity(vec)

# Recommendation function
def recommend(movie_input, show_score=False):
    movie_input_lower = movie_input.lower()
    matches = new_df[new_df['title_lower'].str.contains(movie_input_lower)]

    if matches.empty:
        print(f"Movie '{movie_input}' not found in database.")
        return

    # If multiple matches, take the first one
    index = matches.index[0]
    distances = sorted(list(enumerate(sim[index])), reverse=True, key=lambda x: x[1])

    print(f"\nTop 5 recommendations for '{new_df.iloc[index].title}':")
    for i in distances[1:6]:
        title = new_df.iloc[i[0]].title
        if show_score:
            score = distances[distances.index(i)][1]
            print(f"- {title} (Similarity: {score:.2f})")
        else:
            print(f"- {title}")

# Interactive input
if __name__ == "__main__":
    print("Welcome to the Movie Recommendation System!")
    print("You can type part of the movie title. Type 'exit' to quit.")

    while True:
        movie_input = input("\nEnter a movie title: ").strip()
        if movie_input.lower() == 'exit':
            print("Goodbye!")
            break
        recommend(movie_input, show_score=True)  # show_score=True to display similarity