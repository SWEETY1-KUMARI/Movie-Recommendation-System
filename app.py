import streamlit as st
import pickle
import requests
from requests.exceptions import ConnectionError, Timeout, RequestException
import time

# Load the movies data
movies = pickle.load(open('movies.pkl', 'rb'))
movies_list = movies['title'].values

# Load the similarity data
similarity = pickle.load(open('similarity.pkl', 'rb'))

OMDB_API_KEY = "74b8bc2c"
DEFAULT_POSTER = "https://via.placeholder.com/500x750.png?text=No+Poster+Available"

def fetch_poster(movie_title, retries=3, backoff_factor=0.3):
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={OMDB_API_KEY}"
    for i in range(retries):
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            poster_url = data.get('Poster', DEFAULT_POSTER)
            if poster_url == "N/A":
                poster_url = DEFAULT_POSTER
            return poster_url
        except (ConnectionError, Timeout) as e:
            st.error("Network error occurred. Please check your connection and try again.")
            time.sleep(backoff_factor * (2 ** i))
        except RequestException as e:
            st.error(f"An error occurred: {e}")
            return DEFAULT_POSTER
    return DEFAULT_POSTER

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movie_posters = []
    for i in movie_list:
        movie_title = movies.iloc[i[0]].title
        recommended_movie_posters.append(fetch_poster(movie_title))
        recommended_movies.append(movie_title)
    return recommended_movies, recommended_movie_posters

st.title('Movie Recommender System')

selected_movie = st.selectbox('Choose a movie', movies_list)

if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    cols = st.columns(5)
    for idx, col in enumerate(cols):
        col.text(recommended_movie_names[idx])
        col.image(recommended_movie_posters[idx])
