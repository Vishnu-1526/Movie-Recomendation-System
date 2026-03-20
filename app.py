from flask import Flask, request, jsonify, render_template
import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
script_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(script_dir, 'dataset.csv')
movies = pd.read_csv(dataset_path)
movies['tags'] = movies['genre'].astype(str) + " " + movies['overview'].astype(str)
new_df = movies[['id', 'title', 'tags']].copy()
new_df['title_lower'] = new_df['title'].str.lower()
cv = CountVectorizer(max_features=10000, stop_words='english')
vec = cv.fit_transform(new_df['tags'].values.astype('U')).toarray()
sim = cosine_similarity(vec)
titledf = new_df[['title', 'title_lower']].drop_duplicates().reset_index(drop=True)
app = Flask(__name__)
@app.route('/')
def home():
    return render_template("index.html")

def recommend(movie_input, top_n=5):
    movie_input_lower = movie_input.lower()
    matches = new_df[new_df['title_lower'].str.contains(movie_input_lower)]
    if matches.empty:
        return {"error": f"Movie '{movie_input}' not found in database."}
    index = matches.index[0]
    distances = sorted(list(enumerate(sim[index])), reverse=True, key=lambda x: x[1])
    recommendations = [new_df.iloc[i[0]].title for i in distances[1:top_n+1]]
    return {"movie": new_df.iloc[index].title, "recommendations": recommendations}

@app.route("/recommend", methods=["GET"])
def recommend_api():
    movie = request.args.get("movie")
    if not movie:
        return jsonify({"error": "Please provide a movie parameter"}), 400
    return jsonify(recommend(movie))


@app.route("/search_titles", methods=["GET"])
def search_titles():
    query = request.args.get("query", "").strip().lower()
    if not query:
        return jsonify({"titles": []})

    matches = titledf[titledf['title_lower'].str.contains(query, na=False)].head(12)
    return jsonify({"titles": matches['title'].tolist()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))