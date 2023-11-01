from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS from flask_cors
# import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
import nltk
import pymysql
import numpy as np

app = Flask(__name__)
CORS(app) 

db = pymysql.connect(
    host='mysql5049.site4now.net',
    user='aa0682_movies',
    password='Password1234.',
    db='db_aa0682_movies',
    connect_timeout=8800,
    cursorclass=pymysql.cursors.DictCursor
)

db.ping(reconnect=True)
cursor = db.cursor()
cursor.execute('SELECT * FROM article')
data = cursor.fetchall()


id = [row['article_id'] for row in data]
overviews_orig = [row['abstract'] for row in data]
overviews = [row['abstract'] for row in data]
titles = [row['title'] for row in data] 
titles_orig = [row['title'] for row in data] 


# Preprocess the movie overviews
nltk.download("stopwords")
stop_words = set(stopwords.words("english"))

for n, name in enumerate(overviews):
    temp = name.lower().split(" ")
    temp = [''.join([letter for letter in word if letter.isalnum()]) for word in temp]
    temp = [word for word in temp if word not in stop_words]
    temp = ' '.join(temp)
    overviews[n] = temp
    
for n, title in enumerate(titles):
    temp = title.lower().split(" ")
    temp = [''.join([letter for letter in word if letter.isalnum()]) for word in temp]
    temp = [word for word in temp if word not in stop_words]
    temp = ' '.join(temp)
    titles[n] = temp
# Calculate cosine similarity
    from sklearn.feature_extraction.text import CountVectorizer

    # Calculate cosine similarity for overviews
    vectorizer_overviews = CountVectorizer().fit_transform(overviews)
    cosine_sim_overviews = cosine_similarity(vectorizer_overviews)

    # Calculate cosine similarity for titles
    vectorizer_titles = CountVectorizer().fit_transform(titles)
    cosine_sim_titles = cosine_similarity(vectorizer_titles)

# Function to get article recommendations
def get_article_recommendations( article_id, overviews_similarity_matrix, titles_similarity_matrix):
    # Combine the similarity matrices for overviews and titles, you can adjust the weights as needed
    combined_similarity = 0.4 * overviews_similarity_matrix + 0.6 * titles_similarity_matrix

    similar_articles = list(enumerate(combined_similarity[article_id]))
    similar_articles = sorted(similar_articles, key=lambda x: x[1], reverse=True)
    recommended_articles = []
    
    # Calculate a recommendation score based on similarity (cosine similarity)
    for i in similar_articles:
        if(i[1]< 0.25):
            break
        recommended_article_title = titles_orig[i[0]]
        article_description = overviews_orig[i[0]]
        recommended_articles.append({'title': recommended_article_title, 'article_id': id[i[0]], 'score': i[1]})


    return recommended_articles

# @app.route('/movies/<string:movieTitle>', methods=['GET'])
# def get_movies_by_title(movieTitle):
#     try:
#         with db.cursor() as cursor:
#             cursor.execute('SELECT * FROM movies WHERE names LIKE %s', (f"%{movieTitle}%",))  
#             data = cursor.fetchall()
#             # movies = [{'movie_id': row['movie_id'], 'title': row['names'], 'description': row['overview'], 'date': row['date_x'], 'genre': row['genre']} for row in data]
#             return jsonify(data)
#     except Exception as e:
#         # Handle the exception
#         return jsonify({'error': 'An error occurred while fetching movie data.'}), 500


@app.route('/movies', methods=['POST','GET'])
def recommend_mysql_articles():
    if request.method == 'POST':
        data = request.get_json()
        article_id = data['article_id']-1
        # movie_id = data['movie_id']
        
       
        #     cursor.execute('SELECT * FROM movies WHERE movie_id = %s', (movie_id))
        #     data = cursor.fetchall()
            
        #     if not data:
        #         return jsonify({'message': 'Movie not found.'}), 404
            
            # movies = {'movie_id': data[0]['movie_id'], 'title': data[0]['names'], 'description': data[0]['overview'], 'date': data[0]['date_x'], 'genre': data[0]['genre'] }

        try:
            db.ping(reconnect=True)
            with db.cursor() as cursor:
                cursor.execute('INSERT INTO read_history (article_id, author_id) VALUES (%s, %s)', (article_id, 1))
                db.commit()
        except pymysql.Error as e:
            # Log the error or return a more detailed error response
            return jsonify({'message': 'Error inserting read history.', 'error_details': str(e)}), 500

        recommendations = get_article_recommendations(article_id, cosine_sim_overviews, cosine_sim_titles)

        if recommendations:
            return jsonify(
                {   'message': 'Successfully saved to read history.',
                    # 'movie': movies,
                    'data': recommendations
                })
        else:
            return jsonify({'message': 'No recommendations found.', 'data': recommendations})

    if request.method == 'GET':
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            # Execute an SQL query to fetch the list of movies
            cursor.execute('SELECT * FROM article limit 100')
            
            # Fetch all the movie records
            data = cursor.fetchall()

        # movies = [{'movie_id':row['movie_id'],'title': row['names'], 'description': row['overview'],  'date': row['date_x'],  'genre': row['genre']} for row in data]

        return jsonify(data)
            
# @app.route('/movies/forYou', methods=['GET'])
# def recommendBasedHistory():     
#      try:
#         db.ping(reconnect=True) 
#         with db.cursor() as cursor:
#             cursor.execute('SELECT * FROM watchedMovies')
#             data = cursor.fetchall()[::-1]
#             movie_ids = [row['movie_id'] for row in data]
#             movie_ids = np.unique(movie_ids)
#             # print(data[0]['movie_id'],"ddata")
#             temp=[]
#             results=[]
#             for i in range(len(movie_ids)):
#                  recommendations = get_movie_recommendations(i, cosine_sim)[1:]
#                  if len(recommendations) < 1: continue
#                  temp.append(recommendations)
#                  if len(temp) > 5: break
   
#             print('-----',temp,'---------------')
            
#             for movie_group in temp:
#                 for movie in movie_group:
#                     # Access movie information
                    
#                     movie_id = movie['movie_id']
#                     results.append(movie_id)
#             results = np.unique(results)
#             print(results)

              
                
#         return jsonify(temp)
#      except pymysql.Error as e:
#                 return jsonify({'message': 'Error inserting watched movie.', 'error_details': str(e)}), 500
        
        
       
        
          

'''
data = query_data
recommendations = []
for item in data:
    id = item.id
    recco = get_movie_recc(id)
    recommendations.append(recco)
    
'''

if __name__ == '__main__':
  app.run(port=5000)