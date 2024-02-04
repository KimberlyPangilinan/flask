from flask import Flask, request, jsonify,Blueprint
from db import db
import numpy as np
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
    
@journal_bp.route('/issues', methods=['GET'])
def get_issues():
    param = request.args.get('journal_id')

    try:
        db.ping(reconnect=True)
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            if param is None:
                return jsonify({"message": "journal_id parameter is required"})
            else:
                cursor.execute('SELECT * FROM issues WHERE journal_id = %s', (param,))
                issues = cursor.fetchall()

                # Group issues by year
                issuesPerYear = {}
                for issue in issues:
                    publication_year = issue.get('year')
                    if publication_year:
                        if publication_year not in issuesPerYear:
                            issuesPerYear[publication_year] = []
                        issuesPerYear[publication_year].append(issue)

                # jsonify the grouped issues
                return jsonify({"issuesPerYear": issuesPerYear})
    except Exception as e:
        return jsonify({"error": str(e)})
    
@journal_bp.route(f'/issues/<int:issue_id>', methods=['GET'])
def get_issue(issue_id):

    try:
        db.ping(reconnect=True)
        with db.cursor() as cursor:
            if issue_id is None:
                return jsonify({"message": "issue_id parameter is required"})
            else:
                cursor.execute('SELECT * FROM issues WHERE journal_id = %s', (issue_id,))
                issue = cursor.fetchone()

                return jsonify( issue)
    except Exception as e:
        return jsonify({"error": str(e)})