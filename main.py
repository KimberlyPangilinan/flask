import os
import pymysql
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS 
from routes.articles import articles_bp
from routes.recommendations import recommendations_bp
from routes.check import check_bp
from datetime import timedelta
import numpy as np
from controllers.functions import get_article_recommendations, cosine_sim_overviews,cosine_sim_titles

from flask import Flask, request, jsonify

load_dotenv()
app = Flask(__name__)

CORS(app)

db = pymysql.connect(
    host=os.getenv('DATABASE_HOST'),
    user=os.getenv('DATABASE_USER'),
    password=os.getenv('DATABASE_PASSWORD'),
    db=os.getenv('DATABASE_DB'),
    connect_timeout=8800,
    cursorclass=pymysql.cursors.DictCursor
)
print(db,"db")
# Register blueprints
app.register_blueprint(articles_bp, url_prefix='/api/articles')
app.register_blueprint(recommendations_bp, url_prefix='/api/recommendations')
app.register_blueprint(check_bp, url_prefix='/api/check')

@app.route('/api/popularity', methods=['POST'])
def get_reco_based_on_popularity():
    
    data = request.get_json()
    period = data.get('period', '') 
    category = data.get('category', 'total_reads') 
    
    db.ping(reconnect=True)
    with db.cursor() as cursor:
        if period == 'monthly':
            cursor.execute("""
                   SELECT article.article_id, article.title, article.author, article.publication_date, article.abstract, journal.journal, article.keyword,
                    COUNT(logs.article_id) AS total_interactions,
                    COUNT(CASE WHEN logs.type = 'read' THEN 1 END) AS total_reads,
                    COUNT(CASE WHEN logs.type = 'download' THEN 1 END) AS total_downloads,
					c.contributors

                FROM article 
                    LEFT JOIN logs ON article.article_id = logs.article_id
                    LEFT JOIN journal ON article.journal_id = journal.journal_id
                    LEFT JOIN(
                        SELECT 
                        	article_id, GROUP_CONCAT(DISTINCT CONCAT(firstname,' ',lastname,'->',orcid) SEPARATOR ', ') AS contributors
         				FROM contributors GROUP BY article_id) AS c ON article.article_id = c.article_id
                WHERE DATE_FORMAT(logs.date, '%Y-%m') = DATE_FORMAT(CURRENT_DATE(), '%Y-%m')
                GROUP BY article.article_id
                ORDER BY {} DESC
                LIMIT 5;
            """.format(category))
            data = cursor.fetchall()

        elif period == '':
            cursor.execute("""
                   SELECT article.article_id, article.title, article.author, article.publication_date, article.abstract, journal.journal, article.keyword,
                    COUNT(logs.article_id) AS total_interactions,
                    COUNT(CASE WHEN logs.type = 'read' THEN 1 END) AS total_reads,
                    COUNT(CASE WHEN logs.type = 'download' THEN 1 END) AS total_downloads,
					c.contributors

                FROM article 
                    LEFT JOIN logs ON article.article_id = logs.article_id
                    LEFT JOIN journal ON article.journal_id = journal.journal_id
                    LEFT JOIN(
                        SELECT 
                        	article_id, GROUP_CONCAT(DISTINCT CONCAT(firstname,' ',lastname,'->',orcid) SEPARATOR ', ') AS contributors
         				FROM contributors GROUP BY article_id) AS c ON article.article_id = c.article_id
                GROUP BY article.article_id
                ORDER BY {} DESC
                LIMIT 5;
            """.format(category))
            data = cursor.fetchall()
        else:
           data=[]


    return  {
                "message": f"Successfully fetched  most popular recommendations",
                "recommendations": data
            }


@app.route('/history/<int:author_id>', methods=['GET'])
def get_reco_based_on_history(author_id):
    try:
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            cursor.execute("""
                           SELECT 
                                article.article_id, article.title, article.author, article.publication_date, article.abstract, journal.journal, article.keyword,
                                MAX(logs.date) AS last_read,  
                                COUNT(logs.article_id) AS user_interactions, GROUP_CONCAT(DISTINCT CONCAT(contributors.firstname, ' ', contributors.lastname, '->', contributors.orcid) SEPARATOR ', ') AS contributors

                            FROM article 
                                LEFT JOIN logs ON article.article_id = logs.article_id
                                LEFT JOIN journal ON article.journal_id = journal.journal_id
                                LEFT JOIN contributors ON article.article_id = contributors.article_id
                            WHERE logs.author_id = %s
                            GROUP BY article.article_id
                            ORDER BY last_read DESC
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
            # to remove redundant ids and ids in history
            for article_group in temp:
                for article in article_group:
                    if article['article_id'] not in article_ids and not any(article['article_id'] == res['article_id'] for res in results):
                        results.append(article)
            
            results = sorted(results,  key=lambda x: x["score"], reverse= True)[:10]
            if len(data)== 0:
                return jsonify({'message':f"No history and personalized recommendations for user id {author_id}"})

            return jsonify({'message':f"Successfully fetched the history and personalized recommendations for user id {author_id}",
                            'history':data,
                            'recommendations': results})

    except pymysql.Error as e:
        return jsonify({'message': f"Error fetching recommendations for user id {author_id} ", 'error_details': str(e)}), 500


if __name__ == '__main__':
  app.run(port=5000)