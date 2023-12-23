from flask import Flask, request, jsonify, Blueprint
from db import db
import pymysql
from controllers.functions import get_article_recommendations, cosine_sim_overviews,cosine_sim_titles
from flask_cors import CORS 

articles_bp = Blueprint('articles',__name__)
CORS(articles_bp) 
@articles_bp.route('/', methods=['POST'])
def get_articles_by_title():

    data = request.get_json()
    dates = data.get('dates',[])
    journal = data.get('journal','')
    input = data.get('input','')
 
    try:
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            sort_param = request.args.get('sort', default=None)
            if sort_param == 'title':
                sort = "ORDER BY title ASC"
            elif sort_param == 'publication-date':
                sort = "ORDER BY date ASC"
            elif sort_param == 'recently-added':
                sort = "ORDER BY article.date_added DESC"
            elif sort_param == 'popular':
                sort = "ORDER BY (total_reads + total_downloads) DESC"
                    
            else:
                sort = ""
            input_array = [i.lower().strip() for i in input.split(",")]
            if not dates or dates == []:
                date_conditions = '1=1'  
            else:
                date_conditions = ' OR '.join(['article.publication_date LIKE %s' for _ in dates])

            title_conditions = ' OR '.join('article.title LIKE %s' for i in input_array)
            keyword_conditions = ' OR '.join('article.keyword LIKE %s' for i in input_array)
            author_condition = ' OR '.join('article.author LIKE %s' for i in input_array)
            id_condition = ' OR '.join('article.article_id LIKE %s' for i in input_array)
            
            query = f'''
                SELECT article.*, journal.journal,COUNT(CASE WHEN logs.type = 'read' THEN 1 END) AS total_reads,
                COUNT(CASE WHEN logs.type = 'download' THEN 1 END) AS total_downloads, article_files.file_name, GROUP_CONCAT(DISTINCT CONCAT(contributors.firstname, ' ', contributors.lastname, '->', contributors.orcid) SEPARATOR ', ') AS contributors
                FROM 
                article 
                  LEFT JOIN 
                journal ON article.journal_id = journal.journal_id 
                LEFT JOIN 
                logs ON article.article_id = logs.article_id 
                LEFT JOIN 
                article_files ON article.article_id = article_files.article_id
                LEFT JOIN 
                    contributors ON article.article_id = contributors.article_id
            
                WHERE  {date_conditions}
                AND article.journal_id LIKE %s
                AND
                (
                    {title_conditions}
                    OR {keyword_conditions}
                    OR {author_condition}
                    OR {id_condition}
                   
                )
                GROUP BY
                article.article_id ;
            '''
            input_params = [f"%{input}%" for input in input_array]
            params = [f"%{date}%" for date in dates] + [f"%{journal}%"] + input_params + input_params + input_params + input_params
       
            print(params)
            cursor.execute(f"{query}{sort}", params)
            result = cursor.fetchall()
            if len(result)==0:
                return jsonify({"message": f"No results found for {input} . Try to use comma to separate keywords"})
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

@articles_bp.route('/logs/read', methods=['POST'])
def recommend_and_add_to_history():
    data = request.get_json()
    article_id = data['article_id']
    author_id = data.get('author_id', '')
     
    if not article_id:
        return jsonify({'message': 'Article_id must be provided.'}), 400

    try:
        db.ping(reconnect=True)
        cursor = db.cursor()
        cursor.execute("""
          SELECT
    article.*,
    article_files.file_name,
    c.contributors,
    c.contributors_A,
    c.contributors_B
FROM
    article
LEFT JOIN journal ON article.journal_id = journal.journal_id
LEFT JOIN article_files ON article.article_id = article_files.article_id
LEFT JOIN (
    SELECT
        article_id,
        GROUP_CONCAT(
            DISTINCT CONCAT(lastname, ', ', SUBSTRING(firstname, 1, 1), '.', orcid) SEPARATOR ' ; '
        ) AS contributors,
        GROUP_CONCAT(
            DISTINCT CONCAT(lastname, ', ', firstname) SEPARATOR ' ; '
        ) AS contributors_A,
        GROUP_CONCAT(
            DISTINCT CONCAT(lastname, ', ', SUBSTRING(firstname, 1, 1), '.') SEPARATOR ' ; '
        ) AS contributors_B
    FROM
        contributors
    GROUP BY
        article_id
) AS c ON article.article_id = c.article_id
WHERE
    article.article_id = %s
GROUP BY
    article.article_id,  
    journal.journal_id,
    journal.journal;

        """, (article_id,))
        data = cursor.fetchall()
        print(data,"data")
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            cursor.execute('INSERT INTO logs (article_id, author_id) VALUES (%s, %s)', (article_id, author_id))
            db.commit()
    except pymysql.Error as e:
        return jsonify({'message': 'Error inserting read history.', 'error_details': str(e)}), 500

    recommendations = get_article_recommendations(article_id, cosine_sim_overviews, cosine_sim_titles)

    if isinstance(recommendations, list):  # Check if recommendations is a list
        return jsonify({
            'message': f"{article_id} is successfully inserted to read logs of user {author_id}",
            'recommendations': recommendations[1:],
            'selected_article': data
        })
    
    else:
        return jsonify({'error': recommendations})
 
@articles_bp.route('/logs/download',methods=['POST'])
def insert_downloads():
        data = request.get_json()
        article_id = data['article_id']
        author_id = data.get('author_id', '')
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            cursor.execute('INSERT INTO logs (article_id, author_id,type) VALUES (%s, %s, "download")', (article_id, author_id))
            db.commit()
            
        return jsonify({'message': f"{article_id} is successfully inserted to downloads log of user {author_id}"})



