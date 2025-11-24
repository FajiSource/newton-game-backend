from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import logout_user, login_user, login_required, current_user
from flask_cors import CORS, cross_origin

auth = Blueprint("auth", __name__)

# Allowed origins for CORS
ALLOWED_ORIGINS = ["http://localhost:5173", "https://newton-game-xv9d.vercel.app"]

def get_allowed_origin():
    """Get the allowed origin from the request, or return the first allowed origin."""
    origin = request.headers.get("Origin")
    if origin in ALLOWED_ORIGINS:
        return origin
    return ALLOWED_ORIGINS[0]
cors = CORS(auth, resources={
    r"/*": {
        "origins": ["http://localhost:5173", "https://newton-game-xv9d.vercel.app"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

@cross_origin(origins=["http://localhost:5173", "https://newton-game-xv9d.vercel.app"], supports_credentials=True)
@auth.route("/login", methods=["GET", "POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", get_allowed_origin())
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response
    
    if request.method == "POST":
        data = request.json if request.is_json else request.form
        username = (
            data.get("username")
            or data.get("email")
            or data.get("firstName")
            or ""
        ).strip()
        password = data.get("password")

        from .models import User
        from . import db

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                response = jsonify({
                    "status": 200,
                    "message": "Account logged in Successfully!",
                    "username": user.username
                })
                response.headers.add("Access-Control-Allow-Origin", get_allowed_origin())
                response.headers.add("Access-Control-Allow-Credentials", "true")
                return response
            else:
                response = jsonify({
                    "status": 406,
                    "message": "Incorrect Password!"
                })
                response.headers.add("Access-Control-Allow-Origin", get_allowed_origin())
                response.headers.add("Access-Control-Allow-Credentials", "true")
                return response
        else:
            response = jsonify({
                "status": 406,
                "message": "Email does not exist"
            })
            response.headers.add("Access-Control-Allow-Origin", get_allowed_origin())
            response.headers.add("Access-Control-Allow-Credentials", "true")
            return response
        
    response = jsonify({
        "status": 200,
        "message": "Logged In Successfully!"
    })
    response.headers.add("Access-Control-Allow-Origin", get_allowed_origin())
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response

@cross_origin(origins=["http://localhost:5173", "https://newton-game-xv9d.vercel.app"], supports_credentials=True)
@auth.route("/logout", methods=["GET", "OPTIONS"])
def logout():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", get_allowed_origin())
        response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response
    
    logout_user()
    response = jsonify({
        "status": 200,
        "message": "Logged out Successfully!"
    })
    response.headers.add("Access-Control-Allow-Origin", get_allowed_origin())
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response

@auth.route("/sign-up", methods=["GET", "POST", "OPTIONS"])
@cross_origin(origins=["http://localhost:5173", "https://newton-game-xv9d.vercel.app"], supports_credentials=True)
def sign_up():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", get_allowed_origin())
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response
    
    if request.method == "POST":
        data = request.json if request.is_json else request.form
        username = data.get("username") or ""
            
        password1 = data.get("password1") or ""
        password2 = data.get("password2") or ""

        from .models import User
        from . import db

        user = User.query.filter_by(username=username).first()

        if user:
            response = jsonify({
                "status": 406,
                "message": "Username Already Exist!"
            })
            response.headers.add("Access-Control-Allow-Origin", get_allowed_origin())
            response.headers.add("Access-Control-Allow-Credentials", "true")
            return response
        elif len(username) < 4:
            response = jsonify({
                "status": 406,
                "message": "Username must be more than 4 characters."
            })
            response.headers.add("Access-Control-Allow-Origin", get_allowed_origin())
            response.headers.add("Access-Control-Allow-Credentials", "true")
            return response
        elif len(password1) < 7:
            response = jsonify({
                "status": 406,
                "message": "Password must contain more than 6 characters."
            })
            response.headers.add("Access-Control-Allow-Origin", get_allowed_origin())
            response.headers.add("Access-Control-Allow-Credentials", "true")
            return response
        elif password1 != password2:
            response = jsonify({
                "status": 406,
                "message": "Password don't match!"
            })
            response.headers.add("Access-Control-Allow-Origin", get_allowed_origin())
            response.headers.add("Access-Control-Allow-Credentials", "true")
            return response
        else:
            user = User.query.filter_by(username=username).first()
            if user:
                response = jsonify({
                    "status": 406,
                    "message": "Username already exists."
                })
                response.headers.add("Access-Control-Allow-Origin", get_allowed_origin())
                response.headers.add("Access-Control-Allow-Credentials", "true")
                return response
            else:
                new_user = User(username=username, password=generate_password_hash(password1, method="pbkdf2:sha256"))
                db.session.add(new_user)    
                db.session.commit()
                login_user(new_user, remember=True)
                response = jsonify({
                    "status": 200,
                    "message": "Done Creating Account!",
                    "username": new_user.username
                })
                response.headers.add("Access-Control-Allow-Origin", get_allowed_origin())
                response.headers.add("Access-Control-Allow-Credentials", "true")
                return response

    response = jsonify({
        "status": 200,
        "message": "Account Created"
    })
    response.headers.add("Access-Control-Allow-Origin", get_allowed_origin())
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response