from flask import Flask, request, jsonify,Blueprint
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model
from controllers.functions import  get_originality_score,load_tokenizer,load_label_encoder,preprocess_abstract,classify
from db import db
from flask_cors import CORS 

check_bp = Blueprint('check',__name__)
CORS(check_bp)
@check_bp.route('/duplication', methods=['POST'])
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

@check_bp.route('/journal', methods=['POST'])
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
