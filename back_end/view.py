from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
import json

view = Blueprint("views", __name__)

@view.route("/", methods=["GET", "POST"])
@login_required
def home():
    from .models import Note, User
    from . import db

    if request.method == "POST":
        note = request.form.get("note") or ""

        if len(note) < 1:
            return {
                "status": 406,
                "message": "Note too short!"
            }
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            return {
                "status": 200,
                "message": "Feedback Added!"
            }

@view.route("/delete-note", methods=["POST"])
def delete_note():
    try:
        data = json.loads(request.data)
    except Exception:
        return {"error": "invalid request"}, 400

    note_id = data.get("noteID") or data.get("noteId")
    if not note_id:
        return {"error": "missing note id"}, 400

    from .models import Note
    from . import db

    note = Note.query.get(note_id)
    if not note:
        return {"error": "note not found"}, 404

    if note.user_id != current_user.id:
        return {"error": "unauthorized"}, 403

    db.session.delete(note)
    db.session.commit()
    return jsonify({})

@view.route("/save-points", methods=["POST", "OPTIONS"])
def save_points():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return response
    
    from flask_login import current_user, login_required
    from .models import Point
    from . import db
    from flask import session
    
    print(f"save-points endpoint called")
    print(f"Request cookies: {dict(request.cookies)}")
    print(f"Session keys: {list(session.keys())}")
    print(f"Session ID: {session.get('_id', 'N/A')}")
    print(f"Current user authenticated: {current_user.is_authenticated}")
    print(f"Current user: {current_user.username if current_user.is_authenticated else 'None'}")
    print(f"Request headers Origin: {request.headers.get('Origin', 'N/A')}")
    
    if not current_user.is_authenticated:
        print("User not authenticated, returning 401")
        response = jsonify({
            "status": 401,
            "message": "Authentication required. Please login again."
        })
        origin = request.headers.get("Origin")
        if origin:
            response.headers.add("Access-Control-Allow-Origin", origin)
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 401
    
    try:
        
        print(f"User {current_user.username} is authenticated")
        
        data = request.json if request.is_json else request.form
        points = data.get("points")
        
        print(f"Received points: {points}")
        
        if points is None:
            response = jsonify({
                "status": 406,
                "message": "Points value is required"
            })
            return response, 406
        
        try:
            points = int(points)
        except (ValueError, TypeError):
            response = jsonify({
                "status": 406,
                "message": "Points must be a number"
            })
            return response, 406
        
        new_point = Point(points=points, user_id=current_user.id)
        db.session.add(new_point)
        db.session.commit()
        
        print(f"Points saved successfully: {points} for user {current_user.username}")
        
        response = jsonify({
            "status": 200,
            "message": "Points saved successfully!",
            "points": points
        })
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response
    except Exception as e:
        print(f"Error in save_points: {str(e)}")
        import traceback
        traceback.print_exc()
        response = jsonify({
            "status": 500,
            "message": f"Error saving points: {str(e)}"
        })
        return response, 500