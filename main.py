from flask import Flask, request, jsonify
from flask_cors import CORS 
from flask_mysqldb import MySQL

mysql =MySQL()

app = Flask(__name__)
CORS(app) 

app.config['MYSQL_HOST'] = 'mysql5049.site4now.net'
app.config['MYSQL_USER'] = 'aa0682_movies'
app.config['MYSQL_PASSWORD'] = 'Password1234.'
app.config['MYSQL_DB'] = 'db_aa0682_movies'
 
mysql = MySQL(app)
# mysql.init_app(app)
# db = pymysql.connect(
#     host='mysql5049.site4now.net',
#     user='aa0682_movies',
#     password='Password1234.',
#     db='db_aa0682_movies',
#     cursorclass=pymysql.cursors.DictCursor  
# )
# # Load and preprocess the data


# movie_overviews_orig = [row['overview'] for row in data]
# movie_id = [row['movie_id'] for row in data]
# movie_overviews = [row['overview'] for row in data]
# movie_titles = [row['names'] for row in data] 


# # Preprocess the movie overviews
# nltk.download("stopwords")
# stop_words = set(stopwords.words("english"))

# for n, name in enumerate(movie_overviews):
#     temp = name.lower().split(" ")
#     temp = [''.join([letter for letter in word if letter.isalnum()]) for word in temp]
#     temp = [word for word in temp if word not in stop_words]
#     temp = ' '.join(temp)
#     movie_overviews[n] = temp

# # Calculate cosine similarity
#     from sklearn.feature_extraction.text import CountVectorizer

#     vectorizer = CountVectorizer().fit_transform(movie_overviews)
#     cosine_sim = cosine_similarity(vectorizer)

# # Function to get movie recommendations
# def get_movie_recommendations( movie_title, similarity_matrix):
#     if type(movie_title) == str:
#         movie_idx = movie_titles.index(movie_title)
        
#     else: 
#         movie_idx = movie_title
#         print(movie_title)
#     similar_movies = list(enumerate(similarity_matrix[movie_idx]))
#     similar_movies = sorted(similar_movies, key=lambda x: x[1], reverse=True)
#     recommended_movies = []
    
#     # Calculate a recommendation score based on similarity (cosine similarity)
#     for i in similar_movies:
#         if(i[1]< 0.18):
#             break
#         recommended_movie_title = movie_titles[i[0]]
#         movie_description = movie_overviews_orig[i[0]]
#         recommended_movies.append({'title': recommended_movie_title, 'description': movie_description,'movie_id': movie_id[i[0]], 'score':i[1]})

#     return recommended_movies

# # @app.route('/movies/<string:movieTitle>', methods=['GET'])
# # def get_movies_by_title(movieTitle):
# #     try:
# #         with db.cursor() as cursor:
# #             # Execute an SQL query to fetch the list of movies matching the provided title
# #             cursor.execute('SELECT * FROM movies WHERE names LIKE %s', (f"%{movieTitle}%",))  
            
# #             # Fetch all the movie records
# #             data = cursor.fetchall()

# #             movies = [{'movie_id': row['movie_id'], 'title': row['names'], 'description': row['overview'], 'date': row['date_x'], 'genre': row['genre']} for row in data]

# #             return jsonify(movies)
# #     except Exception as e:
# #         # Handle the exception
# #         return jsonify({'error': 'An error occurred while fetching movie data.'}), 500


# @app.route('/movies', methods=['GET'])
# def recommend_mysql_movies():
#     # if request.method == 'POST':
#     #     data = request.get_json()
#     #     movie_title = data['movie_title']
#     #     movie_id = data['movie_id']
        
       
#     #     #     cursor.execute('SELECT * FROM movies WHERE movie_id = %s', (movie_id))
#     #     #     data = cursor.fetchall()
            
#     #     #     if not data:
#     #     #         return jsonify({'message': 'Movie not found.'}), 404
            
#     #         # movies = {'movie_id': data[0]['movie_id'], 'title': data[0]['names'], 'description': data[0]['overview'], 'date': data[0]['date_x'], 'genre': data[0]['genre'] }

#     #     try:
#     #         with db.cursor() as cursor:
#     #             cursor.execute('INSERT INTO watchedmovies (UserID, movie_id) VALUES (%s, %s)', (1, movie_id))
#     #             db.commit()
#     #     except pymysql.Error as e:
#     #         # Log the error or return a more detailed error response
#     #         return jsonify({'message': 'Error inserting watched movie.', 'error_details': str(e)}), 500

#     #     recommendations = get_movie_recommendations(movie_title, cosine_sim)

#     #     if recommendations:
#     #         return jsonify(
#     #             {   'message': 'Successfully saved to watched history.',
#     #                 # 'movie': movies,
#     #                 'data': recommendations
#     #             })
#     #     else:
#     #         return jsonify({'message': 'No recommendations found.', 'movie': movies, 'data': recommendations})

#     # if request.method == 'GET':
        
#         cursor = mysql.connection.cursor()
#         cursor = conn.cursor(pymysql.cursors.DictCursor)
            

#         cursor.execute('SELECT * FROM movies limit 50')
#         data = cursor.fetchall()
#             # # Execute an SQL query to fetch the list of movies
#             # cursor.execute('SELECT * FROM movies limit 50')
            
#             # # Fetch all the movie records
#             # data = cursor.fetchall()

#         movies = [{'movie_id':row['movie_id'],'title': row['names'], 'description': row['overview'],  'date': row['date_x'],  'genre': row['genre']} for row in data]

#         return jsonify(movies)

 
@app.route('/movies', methods = ['GET'])
def login():

    if request.method == 'GET':
        cursor = mysql.connection.cursor()
        cursor.execute(''' SELECT * FROM movies limit 50''')
        data = cursor.fetchall()
        mysql.connection.commit()
        cursor.close()

        movies = [{'movie_id':row[0],'title': row[1]} for row in data]

        return jsonify(movies)
 
app.run(host='localhost', port=5000)
            
# @app.route('/movies/forYou', methods=['GET'])
# def recommendBasedHistory():     
#      try:
#         with db.cursor() as cursor:
#             cursor.execute('SELECT * FROM watchedMovies ')
#             data = cursor.fetchall()
#             print(data[0]['movie_id'],"ddata")
#             recommendations = get_movie_recommendations(data[0]['movie_id'], cosine_sim)
            
#         return jsonify(recommendations)
#      except pymysql.Error as e:
#                 # Log the error or return a more detailed error response
#                 return jsonify({'message': 'Error inserting watched movie.', 'error_details': str(e)}), 500
        
        
       
        
          

# '''
# data = query_data
# recommendations = []
# for item in data:
#     id = item.id
#     recco = get_movie_recc(id)
#     recommendations.append(recco)
    
# '''

# if __name__ == '__main__':
#   app.run(port=5000)