from flask import Flask, request, jsonify,Blueprint
from db import db

journal_bp = Blueprint('journal',__name__)

@journal_bp.route('/', methods=['GET'])
def get_journal():
    param = request.args.get('id')

    try:
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            if param is None:
                cursor.execute('SELECT * FROM journal')
                return jsonify({"journal": cursor.fetchall()})
            else:
                cursor.execute('SELECT * FROM journal WHERE journal_id = %s', (param,))
                return jsonify({"journalDetails": cursor.fetchone()})
    except Exception as e:
        return jsonify({"error": str(e)})