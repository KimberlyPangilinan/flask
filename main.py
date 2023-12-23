from flask import Flask,session
from flask_cors import CORS 
from routes.articles import articles_bp
from routes.recommendations import recommendations_bp
from routes.check import check_bp
from datetime import timedelta
app = Flask(__name__)

app.json.sort_keys = False
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=5)
app.config["SESSION_TYPE"] = "filesystem"

# app.config['MAIL_USE_TLS'] =  os.getenv("MAIL_USE_TLS")
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = True
CORS(app)


# Register blueprints
app.register_blueprint(articles_bp, url_prefix='/articles')
app.register_blueprint(recommendations_bp, url_prefix='/recommendations')
app.register_blueprint(check_bp, url_prefix='/check')


if __name__ == '__main__':
  app.run(port=5000)