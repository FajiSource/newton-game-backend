from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_cors import CORS
db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "e3b9c4f1d8c2a77a0e948df2b2f31cf0e034d5231af3c4df9a58bbca19d7c3f1"
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = False
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_DOMAIN"] = None
    app.config["PERMANENT_SESSION_LIFETIME"] = 86400

    db.init_app(app)
    from .view import view
    from .auth import auth
    from .leaderboards import leaderboard

    app.register_blueprint(view, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(leaderboard, url_prefix="/")

    from .models import User, Note, Point

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import jsonify
        return jsonify({
            "status": 401,
            "message": "Authentication required"
        }), 401

    return app

def create_database(app):
    if not path.exists("back_end/" + DB_NAME):
        with app.app_context():
            db.create_all()
        print("Create Database!")