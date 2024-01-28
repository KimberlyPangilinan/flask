from flask import Flask
from flask_cors import CORS 
from routes.articles import articles_bp
from routes.recommendations import recommendations_bp
from routes.check import check_bp
from routes.journal import journal_bp
from routes.faqs import faqs_bp
from datetime import timedelta
app = Flask(__name__)

app.json.sort_keys = False
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})


# Register blueprints
app.register_blueprint(articles_bp, url_prefix='/api/articles')
app.register_blueprint(recommendations_bp, url_prefix='/api/recommendations')
app.register_blueprint(check_bp, url_prefix='/api/check')
app.register_blueprint(journal_bp, url_prefix='/api/journal')
app.register_blueprint(faqs_bp, url_prefix='/api/faqs')

if __name__ == '__main__':
  app.run(port=5000)