from flask import Flask
from flask_cors import CORS 
from routes.articles import articles_bp
from routes.recommendations import recommendations_bp
from routes.check import check_bp

app = Flask(__name__)
CORS(app) 
app.json.sort_keys = False


# Register blueprints
app.register_blueprint(articles_bp, url_prefix='/articles')
app.register_blueprint(recommendations_bp, url_prefix='/recommendations')
app.register_blueprint(check_bp, url_prefix='/check')


if __name__ == '__main__':
  app.run(port=5000)