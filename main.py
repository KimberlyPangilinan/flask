from flask import Flask, request, jsonify
from flask_cors import CORS 
# import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
import nltk
import pymysql
import numpy as np

app = Flask(__name__)
app.json.sort_keys = False
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
    
    article_id_to_index = {}  # Create an empty mapping
    for index, article_id in enumerate(id):
        article_id_to_index[article_id] = index
def get_article_recommendations( article_id, overviews_similarity_matrix, titles_similarity_matrix):
    combined_similarity = 0.2 * overviews_similarity_matrix + 0.8 * titles_similarity_matrix
    
    if article_id in article_id_to_index:
        index = article_id_to_index[article_id]
        similar_articles = combined_similarity[index]
        similar_articles = sorted(enumerate(similar_articles), key=lambda x: x[1], reverse=True)
        recommended_articles = []
        
        for i in similar_articles:
            if i[1] < 0.25:
                break
            recommended_article_title = titles_orig[i[0]]
            article_description = overviews_orig[i[0]]
            recommended_articles.append({'title': recommended_article_title, 'article_id': id[i[0]], 'score': i[1]})

        return recommended_articles
    else:
        return ["Article ID not found in the mapping."]


@app.route('/articles', methods=['GET'])
def get_articles():
    db.ping(reconnect=True)
    with db.cursor() as cursor:
        cursor.execute('SELECT * FROM article limit 100')
        data = cursor.fetchall()

    return jsonify(data)
            
@app.route('/articles/search', methods=['GET'])
def get_articles_by_title():
    data = request.get_json()
    dates = data['dates']
    journal = data['journal']
    input = data['input']
    try:
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            input_array = [i.lower().strip() for i in input.split(",")]
            date_conditions = ' OR '.join(['date LIKE %s' for _ in dates])
            title_conditions = ' OR '.join('title LIKE %s' for i in input_array)
            keyword_conditions = ' OR '.join('keyword LIKE %s' for i in input_array)
            author_condition = ' OR '.join('author LIKE %s' for i in input_array)
            
            query = f'''
                SELECT title, date, article_id, keyword, author
                FROM article 
                WHERE ({date_conditions})
                AND journal_id LIKE %s
                AND
                (
                    {title_conditions}
                    OR {keyword_conditions}
                    OR {author_condition}
                   
                );
            '''
            input_params = [f"%{input}%" for input in input_array]
            params = [f"%{date}%" for date in dates] + [f"%{journal}%"] + input_params + input_params + input_params
            print(date_conditions)
            print(params)
            print(journal)
            
            cursor.execute(query, params)
            result = cursor.fetchall()
            
            for i in range(len(result)): ## Adding contains to each result
                result[i]["article_contains"]=[]
            
            article_info = [result[info]["title"]+result[info]["author"]+result[info]["keyword"] for info in range(len(result))]
            
            for input in input_array:
                for n,info in enumerate(article_info):
                    if input in info.lower():
                        result[n]["article_contains"].append(input)
            result = sorted(result,  key=lambda x: len(x["article_contains"]), reverse= True)
            return jsonify({"results": result, "total": len(result)})
    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred while fetching article data.'}), 500

@app.route('/articles/recommendations', methods=['POST'])
def recommend_and_add_to_history():
    data = request.get_json()
    
    if 'article_id' not in data or 'author_id' not in data:
        return jsonify({'message': 'Both article_id and author_id must be provided.'}), 400

    article_id = data['article_id']
    author_id = data['author_id']
    
    try:
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            cursor.execute('INSERT INTO read_history (article_id, author_id) VALUES (%s, %s)', (article_id, author_id))
            db.commit()
    except pymysql.Error as e:
        return jsonify({'message': 'Error inserting read history.', 'error_details': str(e)}), 500

    recommendations = get_article_recommendations(article_id, cosine_sim_overviews, cosine_sim_titles)

    if isinstance(recommendations, list):  # Check if recommendations is a list
        return jsonify({
            'message': 'Successfully saved to read history.',
            'related_articles': recommendations[1:],
            'selected_article': recommendations[:1]
        })
    
    else:
        return jsonify({'error': recommendations})

@app.route('/articles/recommendations/<int:author_id>', methods=['GET'])
def get_reco_based_on_history(author_id):
    try:
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            cursor.execute("""
                           SELECT 
                                article.article_id, article.title, MAX(read_history.last_review) AS latest_review,
                                COUNT(read_history.article_id) AS number_of_reads
                            FROM article LEFT JOIN read_history ON article.article_id = read_history.article_id
                            WHERE read_history.author_id = %s
                            GROUP BY 
                                article.article_id
                            ORDER BY 
                                latest_review DESC
                            LIMIT 5;
                           """,(author_id))
            data = cursor.fetchall()
            article_ids = [row['article_id'] for row in data]
            article_ids = np.unique(article_ids)
            temp = []
            results = []

            for i in range(len(article_ids)):
                recommendations = get_article_recommendations(article_ids[i], cosine_sim_overviews, cosine_sim_titles)[1:]
                if len(recommendations) < 1:
                    continue
                temp.append(recommendations)
                # print(temp)
                # if len(temp) > 3:
                #     break

            for article_group in temp:
                for article in article_group:
                    if article['article_id'] not in article_ids:
                        results.append(article)
            
            results = sorted(results,  key=lambda x: x["score"], reverse= True)[:10]
                    

            return jsonify({'personalized_recommendations': results,'history':data,'user_id': author_id})

    except pymysql.Error as e:
        return jsonify({'message': 'Error fetching recommendations based on read_history', 'error_details': str(e)}), 500

@app.route('/articles/recommendations', methods=['GET'])
def get_reco_based_on_popularity():
    db.ping(reconnect=True)
    data = request.get_json()
    period = data.get('period', 'monthly') 
  
    with db.cursor() as cursor:
        if period == 'monthly':
            cursor.execute("""
                SELECT 
                    article.article_id, 
                    article.title, 
                    COUNT(read_history.article_id) AS number_of_reads
                FROM article 
                LEFT JOIN read_history ON article.article_id = read_history.article_id
                WHERE DATE_FORMAT(read_history.last_review, '%Y-%m') = DATE_FORMAT(CURRENT_DATE(), '%Y-%m')
                GROUP BY article.article_id
                ORDER BY number_of_reads DESC
                LIMIT 5;
            """)
        elif period == 'weekly':
            cursor.execute("""
                SELECT 
                    article.article_id, 
                    article.title, 
                    COUNT(read_history.article_id) AS number_of_reads
                FROM article 
                LEFT JOIN read_history ON article.article_id = read_history.article_id
                WHERE WEEK(read_history.last_review) = WEEK(CURRENT_DATE())
                GROUP BY article.article_id
                ORDER BY number_of_reads DESC
                LIMIT 5;
            """)
        else:
            return {"error": "Invalid period parameter. Use 'monthly' or 'weekly'."}, 400

        data = cursor.fetchall()

    return {"recommendations": data}


if __name__ == '__main__':
  app.run(port=5000)