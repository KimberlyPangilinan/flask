import os
from flask import Flask, request, jsonify
from flask_cors import CORS 
# import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
import nltk
import pymysql
import numpy as np
import datetime
import numpy as np
import pickle
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model
from dotenv import load_dotenv
from db_operations import SQL_MOST_POPULAR_ARTICLES, SQL_AUTHOR_ARTICLE_INTERACTIONS,SQL_AUTHOR_MONTHLY_INTERACTIONS,SQL_JOURNAL_MONTHLY_ENGAGEMENT, SQL_JOURNAL_TOTAL_ENGAGEMENT,SQL_MOST_DOWNLOADED_ARTICLES,SQL_MOST_POPULAR_ARTICLES_GAVEL,SQL_MOST_POPULAR_ARTICLES_LAMP,SQL_MOST_POPULAR_ARTICLES_STAR,SQL_MOST_VIEWED_ARTICLES, execute_query

load_dotenv()

app = Flask(__name__)
app.json.sort_keys = False
CORS(app) 

db = pymysql.connect(
    host=os.getenv('DATABASE_HOST'),
    user=os.getenv('DATABASE_USER'),
    password=os.getenv('DATABASE_PASSWORD'),
    db=os.getenv('DATABASE_DB'),
    connect_timeout=8800,
    cursorclass=pymysql.cursors.DictCursor
)


sql_query= """
SELECT 
    article.article_id, 
    article.title, 
    article.author,
    article.date, 
    article.date_added,
    article.abstract, 
    journal.journal, 
    article.keyword, 
    files.file_name, 
    COUNT(DISTINCT CASE WHEN logs.type = 'read' THEN 1 END) AS total_reads,
    COUNT(DISTINCT CASE WHEN logs.type = 'download' THEN 1 END) AS total_downloads,
    GROUP_CONCAT(DISTINCT CONCAT(contributor.firstname, ' ', contributor.lastname, '->', contributor.orcid) SEPARATOR ', ') AS contributors
FROM 
    article 
LEFT JOIN 
    journal ON article.journal_id = journal.journal_id 
LEFT JOIN 
    logs ON article.article_id = logs.article_id 
LEFT JOIN 
    files ON article.article_id = files.article_id
LEFT JOIN 
    contributor ON article.article_id = contributor.article_id
GROUP BY
    article.article_id;


           """
db.ping(reconnect=True)
cursor = db.cursor()
cursor.execute(sql_query)
data = cursor.fetchall()


id = [row['article_id'] for row in data]
overviews = [row['abstract'] for row in data]
titles = [row['title'] for row in data] 

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
    combined_similarity = 0.4 * overviews_similarity_matrix + 0.6 * titles_similarity_matrix
    
    if article_id in article_id_to_index:
        index = article_id_to_index[article_id]
        similar_articles = combined_similarity[index]
        similar_articles = sorted(enumerate(similar_articles), key=lambda x: x[1], reverse=True)
        recommended_articles = []
        
        for i in similar_articles:
            if i[1] < 0.25:
                break
            # recommended_article_title = titles_orig[i[0]]
            # article_description = overviews_orig[i[0]]
            # recommended_articles.append({'title': recommended_article_title, 'article_id': id[i[0]], 'score': i[1]})
            
            recommended_article = {key: data[i[0]][key] for key in data[i[0]]}
            recommended_article['score'] = i[1]
            recommended_articles.append(recommended_article)


        return recommended_articles
    else:
        return ["Article ID not found in the mapping."]

def get_originality_score(input_title, input_abstract):
    
    # Combine the input title and abstract into a single string if needed
    input_text = f"{input_title} {input_abstract}"
   
    input_title = input_title.lower().split(" ")
    input_title = [''.join([letter for letter in word if letter.isalnum()]) for word in input_title]
    input_title = [word for word in input_title if word not in stop_words]
    input_title = ' '.join(input_title)


    input_abstract = input_abstract.lower().split(" ")
    input_abstract = [''.join([letter for letter in word if letter.isalnum()]) for word in input_abstract]
    input_abstract = [word for word in input_abstract if word not in stop_words]
    input_abstract = ' '.join(input_abstract)
    
    overviews.append(input_abstract)
    titles.append(input_title)

    title_vectorizer = CountVectorizer().fit(titles)
    overview_vectorizer = CountVectorizer().fit(overviews)
    vectorizer = CountVectorizer().fit(overviews + titles)
    vectorizer_overviews = overview_vectorizer.transform([overviews[-1]])
    cosine_sim_overviews = cosine_similarity(vectorizer_overviews, overview_vectorizer.transform(overviews[:-1]))

    
    vectorizer_titles = title_vectorizer.transform([titles[-1]])
    cosine_sim_titles = cosine_similarity(vectorizer_titles, title_vectorizer.transform(titles[:-1]))

    combined_similarity = (cosine_sim_overviews + cosine_sim_titles)/2
    similar_articles = sorted(enumerate(combined_similarity[0]), key=lambda x: x[1], reverse=True)
    
    similar_overviews= sorted(enumerate(cosine_sim_overviews[0]), key=lambda x: x[1], reverse=True)
    similar_titles = sorted(enumerate(cosine_sim_titles[0]), key=lambda x: x[1], reverse=True)
    
    
    recommended_articles = []

    for (i,j,k) in zip(similar_titles, similar_overviews,similar_articles):
        if j[1] < 0.50 and i[1] < 0.50:
            break
 
        index = k[0]
        if index < len(titles) and index < len(overviews):
            recommended_article = {
                'title': data[index]['title'],
                'abstract': data[index]['abstract'],
                'article_id': data[index]['article_id'],
                'score': {
                    'title': i[1],
                    'overview': j[1],
                    'total':k[1]
                }
                
            }
            recommended_articles.append(recommended_article)
    
    if overviews:
        overviews.pop()
    if titles:
        titles.pop()
    return recommended_articles

def load_tokenizer(path):
    '''
        load tokenizer for abstract processing
    '''

    with open(path, 'rb') as handle:
        tokenizer = pickle.load(handle)
        
    return tokenizer

def load_label_encoder(path):
    '''
        loading label encoder for journal name processing
    '''

    with open(path, 'rb') as handle:
        label_encoder = pickle.load(handle)

    return label_encoder

def preprocess_abstract(abstract, tokenizer, label=None):
    '''
        Function to preprocess abstract before classification 

        arguments:
            abstract = raw abstract in string
            tokenizer = tokenizer used by model for training
            label = label of abstract (for testing purposes only)

        The output is an array of integer ID for each word with a maximum length of 50.
        Words are lowercased, alphanumeric characters are retained, and stopwords are removed.
        If the number of words is less than 50, the remaining spaces will be filled with zeros.
        If the number of words is greater than 50, the excess words will be truncated.

    '''
    
    ## Text Preprocessing
    abstract = abstract.lower().split(" ")
    abstract = [''.join([letter for letter in word if letter.isalnum()]) for word in abstract]
    abstract = [word for word in abstract if word not in stop_words]
    abstract = ' '.join(abstract)
    
    ## Assign unique ID to each word in the abstract
    sequences = tokenizer.texts_to_sequences([abstract])

    ## Fill with zeros or truncate the array of word IDs. The maximum length is 50.
    pad_trunc_sequences = pad_sequences(sequences, maxlen=20, padding='post', truncating='post')

    return pad_trunc_sequences, label


def classify(input_data, model, label_encoder):
    '''
        Function to classify processed abstract 
        arguments: 
            input_data = processed abstract
            model = A.I. model
            label_encoder = label_encoder used by model for training

        the output of the function is the journal name
    '''

    ## classify abstract using model
    output = model(input_data)

    ## Get the highest probability of classification
    output = np.argmax(output)
    print(output )

    ## Get the journal name equivalent of the output of classification
    journal = label_encoder.inverse_transform([output])

    ## replace _ with whitespace in the journal name
    journal = ' '.join(journal[0].split('_'))
    
    return [journal, output]

@app.route('/article/checker', methods=['POST'])
def check_originality():
    data = request.get_json()
    title = data['title']
    abstract = data['abstract']
    
    similar_articles = get_originality_score(title, abstract)

    if isinstance(similar_articles, list): 
        if len(similar_articles) > 0:
            return jsonify({
                'flagged': True,
                'highest_simlarity':similar_articles[0]['score']['total'],
                'similar_articles': similar_articles
            })  
        return jsonify({
                'flagged': False,
                'similar_articles': similar_articles
            })  
    return jsonify({'error':'error'})
    
model = load_model('models//classifier_v4//model.h5')

@app.route('/journal', methods=['POST'])
def classify_article():
    data = request.get_json()
    abstract = data['abstract']
   
    ## Load tokenizer and encoder
    tokenizer = load_tokenizer('models//classifier_v4//tokenizer.pickle')
    label_encoder = load_label_encoder('models//classifier_v4//label_encoder.pickle')

    ## Preprocess abstract
    input_data, input_label = preprocess_abstract(abstract,tokenizer)

    ## classify abstract
    result = classify(input_data, model, label_encoder)

    return {
            'journal_classification': f"{result[1]+1}",
            'journal_name': result[0],
            }
        
@app.route('/articles', methods=['POST'])
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
                date_conditions = ' OR '.join(['article.date LIKE %s' for _ in dates])

            title_conditions = ' OR '.join('article.title LIKE %s' for i in input_array)
            keyword_conditions = ' OR '.join('article.keyword LIKE %s' for i in input_array)
            author_condition = ' OR '.join('article.author LIKE %s' for i in input_array)
            id_condition = ' OR '.join('article.article_id LIKE %s' for i in input_array)
            
            query = f'''
                SELECT article.article_id, article.title, article.author, article.date, article.abstract, journal.journal, article.date_added, article.keyword,COUNT(CASE WHEN logs.type = 'read' THEN 1 END) AS total_reads,
                COUNT(CASE WHEN logs.type = 'download' THEN 1 END) AS total_downloads, files.file_name, GROUP_CONCAT(DISTINCT CONCAT(contributor.firstname, ' ', contributor.lastname, '->', contributor.orcid) SEPARATOR ', ') AS contributors
                FROM 
                article 
                  LEFT JOIN 
                journal ON article.journal_id = journal.journal_id 
                LEFT JOIN 
                logs ON article.article_id = logs.article_id 
                LEFT JOIN 
                files ON article.article_id = files.article_id
                LEFT JOIN 
                    contributor ON article.article_id = contributor.article_id
            
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

@app.route('/articles/logs/read', methods=['POST'])
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
                article.article_id,
                article.title,
                article.author,
                article.date,
                article.date_added,
                article.abstract,
                journal.journal,
                article.keyword,
                files.file_name,
                SUM(
                    CASE WHEN LOGS.type = 'read' THEN 1 ELSE 0
                END
            ) AS total_reads,
            SUM(
                CASE WHEN LOGS.type = 'download' THEN 1 ELSE 0
            END
            ) AS total_downloads,
            c.contributors
            FROM
                article
            LEFT JOIN journal ON article.journal_id = journal.journal_id
            LEFT JOIN LOGS ON article.article_id = LOGS.article_id
            LEFT JOIN files ON article.article_id = files.article_id
            LEFT JOIN(
                SELECT article_id,
                    GROUP_CONCAT(
                        DISTINCT CONCAT(firstname,' ',lastname,'->',orcid) SEPARATOR ', ') AS contributors
                FROM
                    contributor
                GROUP BY
                    article_id
            ) AS c
            ON
                article.article_id = c.article_id
            WHERE
                article.article_id = %s
            GROUP BY
                journal.journal_id,
                journal.journal,
                article.article_id
            ORDER BY
                total_downloads
            DESC
            LIMIT 10;
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
 
@app.route('/articles/logs/download',methods=['POST'])
def insert_downloads():
        data = request.get_json()
        article_id = data['article_id']
        author_id = data.get('author_id', '')
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            cursor.execute('INSERT INTO logs (article_id, author_id,type) VALUES (%s, %s, "download")', (article_id, author_id))
            db.commit()
            
        return jsonify({'message': f"{article_id} is successfully inserted to downloads log of user {author_id}"})

@app.route('/articles/recommendations/<int:author_id>', methods=['GET'])
def get_reco_based_on_history(author_id):
    try:
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            cursor.execute("""
                           SELECT 
                                article.article_id, article.title, article.author, article.date, article.abstract, journal.journal, article.keyword,
                                MAX(logs.date) AS last_read,  
                                COUNT(logs.article_id) AS user_interactions, GROUP_CONCAT(DISTINCT CONCAT(contributor.firstname, ' ', contributor.lastname, '->', contributor.orcid) SEPARATOR ', ') AS contributors

                            FROM article 
                                LEFT JOIN logs ON article.article_id = logs.article_id
                                LEFT JOIN journal ON article.journal_id = journal.journal_id
                                LEFT JOIN contributor ON article.article_id = contributor.article_id
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

@app.route('/articles/recommendations', methods=['POST'])
def get_reco_based_on_popularity():
    db.ping(reconnect=True)
    data = request.get_json()
    period = data.get('period', '') 
    category = data.get('category', 'total_interactions') 
  
    with db.cursor() as cursor:
        if period == 'monthly':
            cursor.execute("""
                   SELECT article.article_id, article.title, article.author, article.date, article.abstract, journal.journal, article.keyword,
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
         				FROM contributor GROUP BY article_id) AS c ON article.article_id = c.article_id
                WHERE DATE_FORMAT(logs.date, '%Y-%m') = DATE_FORMAT(CURRENT_DATE(), '%Y-%m')
                GROUP BY article.article_id
                ORDER BY {} DESC
                LIMIT 5;
            """.format(category))

        elif period == '':
            cursor.execute("""
                   SELECT article.article_id, article.title, article.author, article.date, article.abstract, journal.journal, article.keyword,
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
         				FROM contributor GROUP BY article_id) AS c ON article.article_id = c.article_id
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



if __name__ == '__main__':
  app.run(port=5000)