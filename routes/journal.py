from flask import Flask, request, jsonify,Blueprint
from db import db

journal_bp = Blueprint('journal',__name__)
@journal_bp.route('/', methods=['GET'])
def get_journal():
    param = request.args.get('id')

    if param is None:
        return jsonify({"error": "Invalid request. 'id' parameter is missing."}), 400

    db.ping(reconnect=True)
    cursor = db.cursor()
    journal_sql = 'SELECT * FROM journal WHERE journal_id = %s'

    cursor.execute(journal_sql, (param,))
    journal_details = cursor.fetchone()

    return jsonify({"journalDetails": journal_details})
    

