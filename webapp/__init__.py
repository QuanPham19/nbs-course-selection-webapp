from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_session import Session
import redis

db = SQLAlchemy()
DB_NAME = "session.db"

def create_app():
    app = Flask(__name__, template_folder='template')
    app.config['SECRET_KEY'] = 'BC2410'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

    # app.config['SECRET_KEY'] = 'BC2410'
    # app.config['SESSION_TYPE'] = 'redis'
    # app.config['SESSION_PERMANENT'] = False
    # app.config['SESSION_USE_SIGNER'] = True
    # app.config['SESSION_KEY_PREFIX'] = 'flask_session:'
    # app.config['SESSION_REDIS'] = redis.StrictRedis(host='localhost', port=6379, db=0)

    db.init_app(app)
    from .view import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .database import SessionData
    with app.app_context():
        db.create_all()

    return app

def create_database(app):
    if not path.exists('webapp/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')