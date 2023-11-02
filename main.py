from flask import Flask, request, jsonify
from flask_cors import CORS 
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


# Preprocessing
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

    vectorizer = CountVectorizer().fit(overviews + titles)
    # Calculate cosine similarity for overviews
    vectorizer_overviews = vectorizer.transform(overviews)
    cosine_sim_overviews = cosine_similarity(vectorizer_overviews)

    # Calculate cosine similarity for titles
    vectorizer_titles =  vectorizer.transform(titles)
    cosine_sim_titles = cosine_similarity(vectorizer_titles)

def get_article_recommendations( article_id, overviews_similarity_matrix, titles_similarity_matrix):
    combined_similarity = 0.2 * overviews_similarity_matrix + 0.8 * titles_similarity_matrix

    similar_articles = list(enumerate(combined_similarity[article_id]))
    similar_articles = sorted(similar_articles, key=lambda x: x[1], reverse=True)
    recommended_articles = []
    
    # Calculate a recommendation score based on similarity (cosine similarity)
    for i in similar_articles:
        if(i[1]< 0.30):
            break
        recommended_article_title = titles_orig[i[0]]
        article_description = overviews_orig[i[0]]
        recommended_articles.append({'title': recommended_article_title, 'article_id': id[i[0]], 'score': i[1]})

    return recommended_articles

@app.route('/articles/<string:articleTitle>', methods=['GET'])
def get_articles_by_title(articleTitle):
    try:
        with db.cursor() as cursor:
            cursor.execute('SELECT * FROM article WHERE title LIKE %s', (f"%{articleTitle}%",))  
            data = cursor.fetchall()
            return jsonify(data)
    except Exception as e:
        return jsonify({'error': 'An error occurred while fetching article data.'}), 500


@app.route('/articles', methods=['POST','GET'])
def recommend_mysql_articles():
    if request.method == 'POST':
        data = request.get_json()
        
        if 'article_id' not in data or 'author_id' not in data:
            return jsonify({'message': 'Both article_id and author_id must be provided.'}), 400

        article_id = data['article_id']-1
        author_id = data['author_id']
     
        try:
            db.ping(reconnect=True)
            with db.cursor() as cursor:
                cursor.execute('INSERT INTO read_history (article_id, author_id) VALUES (%s, %s)', (article_id, author_id))
                db.commit()
        except pymysql.Error as e:
            return jsonify({'message': 'Error inserting read history.', 'error_details': str(e)}), 500

        recommendations = get_article_recommendations(article_id, cosine_sim_overviews, cosine_sim_titles)

        if recommendations:
            return jsonify(
                {   'message': 'Successfully saved to read history.',
                    'data': recommendations
                })
        else:
            return jsonify({'message': 'No recommendations found.', 'recommendations': recommendations})

    if request.method == 'GET':
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            cursor.execute('SELECT * FROM article limit 100')
            data = cursor.fetchall()

        return jsonify(data)
            
@app.route('/articles/history/<int:author_id>', methods=['GET'])
def recommendBasedHistory(author_id):
    try:
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            cursor.execute('SELECT * FROM read_history where author_id = %s', (author_id,))
            data = cursor.fetchall()[::-1]
            history = [int(row['article_id']) for row in data]
            article_ids = [row['article_id'] for row in data]
            article_ids = np.unique(article_ids)
            temp = []
            results = []

            for i in range(len(article_ids)):
                recommendations = get_article_recommendations(i, cosine_sim_overviews, cosine_sim_titles)[1:]
                if len(recommendations) < 1:
                    continue
                temp.append(recommendations)
                if len(temp) > 5:
                    break

            for article_group in temp:
                for article in article_group:
                    article_id = article['article_id']
                    results.append({'article_id': article_id, 'title': article['title'], 'score': article['score']})

            return jsonify({'personalized_recommendations': results,'history':history,'user_id': author_id})

    except pymysql.Error as e:
        return jsonify({'message': 'Error fetching recommendations based on read_history', 'error_details': str(e)}), 500


if __name__ == '__main__':
  app.run(port=5000)