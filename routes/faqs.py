from flask import Flask, request, jsonify,Blueprint
from db import db

faqs_bp = Blueprint('faqs',__name__)

@faqs_bp.route('/', methods=['GET'])
def get_faqs():
    category = request.args.get('category',"general_questions")
    limit = request.args.get('limit')
    
    
    try:
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            if limit is None:
                cursor.execute('SELECT * FROM faqs where category = %s ',(category,))
               
            else:
                cursor.execute('SELECT * FROM faqs where category = %s LIMIT %s',(category, limit))
            return jsonify({"faqs": cursor.fetchall()})
  
    except Exception as e:
        return jsonify({"error": str(e)})