from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import logout_user, login_user, login_required, current_user

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST", "OPTIONS"])
def login():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
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
                from flask import session, make_response
                login_user(user, remember=True)
                session.permanent = True
                session.modified = True
                
                response = make_response(jsonify({
                    "status": 200,
                    "message": "Account logged in Successfully!",
                    "username": user.username
                }))
                
                origin = request.headers.get("Origin")
                if origin:
                    response.headers.add("Access-Control-Allow-Origin", origin)
                response.headers.add("Access-Control-Allow-Credentials", "true")
                
                print(f"User {user.username} logged in")
                print(f"Session ID: {session.get('_id', 'N/A')}")
                print(f"Session keys: {list(session.keys())}")
                print(f"User authenticated: {user.is_authenticated}")
                print(f"Session permanent: {session.permanent}")
                print(f"Response headers: {dict(response.headers)}")
                
                return response
            else:
                response = jsonify({
                    "status": 406,
                    "message": "Incorrect Password!"
                })
                return response
        else:
            response = jsonify({
                "status": 406,
                "message": "Username does not exist"
            })
            return response
        
    response = jsonify({
        "status": 200,
        "message": "Logged In Successfully!"
    })
    return response

@auth.route("/logout", methods=["GET", "OPTIONS"])
def logout():
    if request.method == "OPTIONS":
        response = jsonify({})
        return response
    
    logout_user()
    response = jsonify({
        "status": 200,
        "message": "Logged out Successfully!"
    })
    return response

@auth.route("/check-session", methods=["GET", "OPTIONS"])
def check_session():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return response
    
    from flask_login import current_user
    from flask import session
    
    if current_user.is_authenticated:
        session.permanent = True
        session.modified = True
        response = jsonify({
            "status": 200,
            "authenticated": True,
            "username": current_user.username
        })
        origin = request.headers.get("Origin")
        if origin:
            response.headers.add("Access-Control-Allow-Origin", origin)
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response
    else:
        response = jsonify({
            "status": 401,
            "authenticated": False,
            "message": "Not authenticated"
        })
        origin = request.headers.get("Origin")
        if origin:
            response.headers.add("Access-Control-Allow-Origin", origin)
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 401

@auth.route("/sign-up", methods=["GET", "POST", "OPTIONS"])
def sign_up():
    if request.method == "OPTIONS":
        response = jsonify({})
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
            return response
        elif len(username) < 4:
            response = jsonify({
                "status": 406,
                "message": "Username must be more than 4 characters."
            })
            return response
        elif len(password1) < 7:
            response = jsonify({
                "status": 406,
                "message": "Password must contain more than 6 characters."
            })
            return response
        elif password1 != password2:
            response = jsonify({
                "status": 406,
                "message": "Password don't match!"
            })
            return response
        else:
            user = User.query.filter_by(username=username).first()
            if user:
                response = jsonify({
                    "status": 406,
                    "message": "Username already exists."
                })
                return response
            else:
                new_user = User(username=username, password=generate_password_hash(password1, method="pbkdf2:sha256"))
                db.session.add(new_user)    
                db.session.commit()
                from flask import session, make_response
                login_user(new_user, remember=True)
                session.permanent = True
                session.modified = True
                
                response = make_response(jsonify({
                    "status": 200,
                    "message": "Done Creating Account!",
                    "username": new_user.username
                }))
                
                origin = request.headers.get("Origin")
                if origin:
                    response.headers.add("Access-Control-Allow-Origin", origin)
                response.headers.add("Access-Control-Allow-Credentials", "true")
                
                return response

    response = jsonify({
        "status": 200,
        "message": "Account Created"
    })
    return response