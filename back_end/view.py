from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from flask_cors import CORS, cross_origin
import json

# NOTE: Importing models at module import time can sometimes trigger
# circular-import problems (ImportError) in Flask apps where the package
# `back_end` initializes `db` and registers blueprints in `create_app()`.
# To avoid that, import the `Note` model (and package `db`) inside the
# request-handling functions where they're actually needed.

view = Blueprint("views", __name__)

# Allowed origins for CORS
ALLOWED_ORIGINS = ["http://localhost:5173", "https://newton-game-xv9d.vercel.app"]

def get_allowed_origin():
    """Get the allowed origin from the request, or return the first allowed origin."""
    origin = request.headers.get("Origin")
    if origin in ALLOWED_ORIGINS:
        return origin
    return ALLOWED_ORIGINS[0]

cors = CORS(view, resources={
    r"/*": {
        "origins": ALLOWED_ORIGINS,
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# NOTE: The correct Flask parameter name is `methods` (plural).
# Using `method=[...]` will raise TypeError: unexpected keyword argument 'method'.
@view.route("/", methods=["GET", "POST"])
@login_required
def home():
    # Import models and db here to avoid circular-import / ImportError when
    # the module is imported during app startup.
    from .models import Note, User
    from . import db

    if request.method == "POST":
        # request.form.get may return None if 'note' isn't supplied.
        # Guard against that to avoid TypeError from len(None).
        note = request.form.get("note") or ""

        if len(note) < 1:
            # flash("Note too short!", category="error")
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


# NOTE: Defining two routes with the same path `/` (one for GET/POST and
# another for delete) causes routing conflicts. Use a distinct endpoint
# for delete actions and the correct `methods` keyword.
@view.route("/delete-note", methods=["POST"])
def delete_note():
    # request.data is a bytes object; parse JSON safely and handle errors.
    try:
        data = json.loads(request.data)
    except Exception:
        # Return a client error if JSON is invalid.
        return {"error": "invalid request"}, 400

    # The original code mistakenly accessed Note.data["noteID"].
    # `Note` is the model class; `Note.data` is a Column descriptor, not
    # the incoming JSON. We must read the note ID from the parsed JSON.
    note_id = data.get("noteID") or data.get("noteId")
    if not note_id:
        return {"error": "missing note id"}, 400

    # Import Note and db here to avoid ImportError during module import.
    from .models import Note
    from . import db

    note = Note.query.get(note_id)
    if not note:
        return {"error": "note not found"}, 404

    # Ensure the logged-in user owns the note before deleting.
    if note.user_id != current_user.id:
        return {"error": "unauthorized"}, 403

    db.session.delete(note)
    db.session.commit()
    return jsonify({})

@view.route("/save-points", methods=["POST", "OPTIONS"])
@cross_origin(origins=["http://localhost:5173", "https://newton-game-xv9d.vercel.app"], supports_credentials=True)
@login_required
def save_points():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", get_allowed_origin())
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response
    
    from .models import Point
    from . import db
    
    try:
        data = request.json if request.is_json else request.form
        points = data.get("points")
        
        if points is None:
            response = jsonify({
                "status": 406,
                "message": "Points value is required"
            })
            response.headers.add("Access-Control-Allow-Origin", get_allowed_origin())
            response.headers.add("Access-Control-Allow-Credentials", "true")
            return response, 406
        
        try:
            points = int(points)
        except (ValueError, TypeError):
            response = jsonify({
                "status": 406,
                "message": "Points must be a number"
            })
            response.headers.add("Access-Control-Allow-Origin", get_allowed_origin())
            response.headers.add("Access-Control-Allow-Credentials", "true")
            return response, 406
        
        new_point = Point(points=points, user_id=current_user.id)
        db.session.add(new_point)
        db.session.commit()
        
        response = jsonify({
            "status": 200,
            "message": "Points saved successfully!",
            "points": points
        })
        response.headers.add("Access-Control-Allow-Origin", get_allowed_origin())
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response
    except Exception as e:
        response = jsonify({
            "status": 500,
            "message": f"Error saving points: {str(e)}"
        })
        response.headers.add("Access-Control-Allow-Origin", get_allowed_origin())
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 500