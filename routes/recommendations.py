from flask import Flask, request, jsonify, Blueprint
from db import db
import pymysql
import numpy as np
from controllers.functions import get_article_recommendations, cosine_sim_overviews,cosine_sim_titles

recommendations_bp = Blueprint('recommendations',__name__)

@recommendations_bp.route('/', methods=['POST'])
def get_reco_based_on_popularity():
    db.ping(reconnect=True)
    data = request.get_json()
    period = data.get('period', '') 
    category = data.get('category', 'total_interactions') 
  
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
        else:
            return {"error": "Invalid period parameter. Use 'monthly' or ''."}, 400

        data = cursor.fetchall()

    return  {
                "message": f"Successfully fetched  most popular {period} recommendations based on {category}",
                "recommendations": data
            }


@recommendations_bp.route('/<int:author_id>', methods=['GET'])
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
