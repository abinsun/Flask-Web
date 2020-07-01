from flask import Flask
from os import path
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import pymysql
pymysql.install_as_MySQLdb()
bootstrap=Bootstrap()
db=SQLAlchemy()
login_manager=LoginManager()
login_manager.session_protection='strong'
login_manager.login_view='auth.login'

def create_app():
    app= Flask(__name__)
    app.config.from_pyfile('config')
    app.config['SQLALCHEMY_DATABASE_URI']="mysql://root:@127.0.0.1:3306/python"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True

    db.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)

    from .auth import auth as auth_blue
    from .main import main as main_blue

    app.register_blueprint(auth_blue)
    app.register_blueprint(main_blue)

    return app





