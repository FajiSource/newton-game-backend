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
    
    import os
    
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        database_url = "postgresql://newton_sql_user:oAtmS7kqvn3F0jxyBJOuxPjJflJIGJNU@dpg-d4k78aje5dus73f1vls0-a.oregon-postgres.render.com/newton_sql"
    
    if database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+psycopg://', 1)
    
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    
    is_production = (
        'RENDER' in os.environ or 
        os.environ.get('FLASK_ENV') == 'production' or 
        os.environ.get('ENVIRONMENT') == 'production' or
        os.environ.get('PRODUCTION') == 'true'
    )
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    if is_production:
        app.config["SESSION_COOKIE_SAMESITE"] = "None"
        app.config["SESSION_COOKIE_SECURE"] = True
    else:
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

    from .models import User, Note, Point, UserCompletion, GameScore

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
    with app.app_context():
        try:
            db.create_all()
            
            from sqlalchemy import text
            try:
                with db.engine.begin() as conn:
                    result = conn.execute(text("""
                        SELECT character_maximum_length 
                        FROM information_schema.columns 
                        WHERE table_name = 'user' AND column_name = 'password'
                    """))
                    row = result.fetchone()
                    if row and row[0] and row[0] < 200:
                        conn.execute(text("ALTER TABLE \"user\" ALTER COLUMN password TYPE VARCHAR(200)"))
                        print("Updated password column to VARCHAR(200)")
            except Exception as alter_error:
                print(f"Note: Could not alter password column (may not exist yet or already updated): {alter_error}")
            
            print(f"PostgreSQL database tables created/verified successfully!")
            print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI'].split('@')[1] if '@' in app.config['SQLALCHEMY_DATABASE_URI'] else 'configured'}")
        except Exception as e:
            print(f"Error creating database tables: {str(e)}")
            import traceback
            traceback.print_exc()
            raise