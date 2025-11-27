from flask import Blueprint, render_template, request, flash, jsonify,send_file
from flask_login import login_required, current_user

import json
import os

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

@view.route("/save-completion", methods=["POST", "OPTIONS"])
def save_completion():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return response
    
    from flask_login import current_user
    from .models import UserCompletion
    from . import db
    from sqlalchemy.sql import func
    
    if not current_user.is_authenticated:
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
        data = request.json if request.is_json else request.form
        game_type = data.get("gameType")
        quiz_score = data.get("quizScore")
        
        if not game_type:
            response = jsonify({
                "status": 406,
                "message": "gameType is required"
            })
            response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
            response.headers.add("Access-Control-Allow-Credentials", "true")
            return response, 406
        
        user_completion = UserCompletion.query.filter_by(user_id=current_user.id).first()
        if not user_completion:
            user_completion = UserCompletion(user_id=current_user.id)
            db.session.add(user_completion)
        
        if game_type == "soccer":
            user_completion.soccer_completed = True
        elif game_type == "rocket":
            user_completion.rocket_completed = True
        elif game_type == "asteroid":
            user_completion.asteroid_completed = True
        elif game_type == "quiz":
            if quiz_score is not None:
                quiz_score_float = float(quiz_score)
                if quiz_score_float >= 80.0:
                    user_completion.quiz_completed = True
                    user_completion.quiz_score = quiz_score_float
                else:
                    response = jsonify({
                        "status": 200,
                        "message": "Quiz score saved but not completed (need 80% or perfect)",
                        "quizScore": quiz_score_float,
                        "quizCompleted": False
                    })
                    response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
                    response.headers.add("Access-Control-Allow-Credentials", "true")
                    return response
        
        if (user_completion.soccer_completed and 
            user_completion.rocket_completed and 
            user_completion.asteroid_completed and 
            user_completion.quiz_completed):
            if not user_completion.all_completed:
                user_completion.all_completed = True
                user_completion.completed_date = func.now()
        
        user_completion.updated_date = func.now()
        db.session.commit()
        
        response = jsonify({
            "status": 200,
            "message": "Completion status saved successfully!",
            "completion": {
                "soccer": user_completion.soccer_completed,
                "rocket": user_completion.rocket_completed,
                "asteroid": user_completion.asteroid_completed,
                "quiz": user_completion.quiz_completed,
                "quizScore": user_completion.quiz_score,
                "allCompleted": user_completion.all_completed
            }
        })
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response
    except Exception as e:
        print(f"Error in save_completion: {str(e)}")
        import traceback
        traceback.print_exc()
        response = jsonify({
            "status": 500,
            "message": f"Error saving completion: {str(e)}"
        })
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 500

@view.route("/get-completion", methods=["GET", "OPTIONS"])
def get_completion():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return response
    
    from flask_login import current_user
    from .models import UserCompletion
    
    if not current_user.is_authenticated:
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
        user_completion = UserCompletion.query.filter_by(user_id=current_user.id).first()
        
        if not user_completion:
            completion_data = {
                "soccer": False,
                "rocket": False,
                "asteroid": False,
                "quiz": False,
                "quizScore": 0.0,
                "allCompleted": False
            }
        else:
            completion_data = {
                "soccer": user_completion.soccer_completed,
                "rocket": user_completion.rocket_completed,
                "asteroid": user_completion.asteroid_completed,
                "quiz": user_completion.quiz_completed,
                "quizScore": user_completion.quiz_score,
                "allCompleted": user_completion.all_completed
            }
        
        response = jsonify({
            "status": 200,
            "completion": completion_data
        })
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response
    except Exception as e:
        print(f"Error in get_completion: {str(e)}")
        import traceback
        traceback.print_exc()
        response = jsonify({
            "status": 500,
            "message": f"Error getting completion: {str(e)}"
        })
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 500

@view.route("/get-game-score", methods=["GET", "OPTIONS"])
def get_game_score():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("Access-Control-Allow-Methods", "GET, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return response
    
    from flask_login import current_user
    from .models import GameScore
    
    if not current_user.is_authenticated:
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
        game_type = request.args.get("gameType")
        level = request.args.get("level", type=int)
        
        if not game_type or level is None:
            response = jsonify({
                "status": 406,
                "message": "gameType and level are required"
            })
            response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
            response.headers.add("Access-Control-Allow-Credentials", "true")
            return response, 406
        
        game_score = GameScore.query.filter_by(
            user_id=current_user.id,
            game_type=game_type,
            level=level
        ).first()
        
        if not game_score:
            score_data = {
                "bestScore": 0,
                "completed": False
            }
        else:
            score_data = {
                "bestScore": game_score.best_score,
                "completed": game_score.completed
            }
        
        response = jsonify({
            "status": 200,
            "score": score_data
        })
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response
    except Exception as e:
        print(f"Error in get_game_score: {str(e)}")
        import traceback
        traceback.print_exc()
        response = jsonify({
            "status": 500,
            "message": f"Error getting game score: {str(e)}"
        })
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 500

@view.route("/save-game-score", methods=["POST", "OPTIONS"])
def save_game_score():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        return response
    
    from flask_login import current_user
    from .models import GameScore
    from . import db
    from sqlalchemy.sql import func
    
    if not current_user.is_authenticated:
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
        data = request.json if request.is_json else request.form
        game_type = data.get("gameType")
        level = data.get("level")
        score = data.get("score")
        completed = data.get("completed", False)
        
        if not game_type or level is None or score is None:
            response = jsonify({
                "status": 406,
                "message": "gameType, level, and score are required"
            })
            response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
            response.headers.add("Access-Control-Allow-Credentials", "true")
            return response, 406
        
        try:
            level = int(level)
            score = int(score)
        except (ValueError, TypeError):
            response = jsonify({
                "status": 406,
                "message": "level and score must be numbers"
            })
            response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
            response.headers.add("Access-Control-Allow-Credentials", "true")
            return response, 406
        
        game_score = GameScore.query.filter_by(
            user_id=current_user.id,
            game_type=game_type,
            level=level
        ).first()
        
        if not game_score:
            game_score = GameScore(
                user_id=current_user.id,
                game_type=game_type,
                level=level,
                best_score=score,
                completed=completed
            )
            db.session.add(game_score)
            points_to_add = score
        else:
            if score > game_score.best_score:
                points_to_add = score - game_score.best_score
                game_score.best_score = score
            else:
                points_to_add = 0
            
            if completed:
                game_score.completed = True
            
            game_score.updated_date = func.now()
        
        db.session.commit()
        
        response = jsonify({
            "status": 200,
            "message": "Game score saved successfully",
            "bestScore": game_score.best_score,
            "pointsToAdd": points_to_add,
            "wasNewRecord": points_to_add > 0
        })
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response
    except Exception as e:
        print(f"Error in save_game_score: {str(e)}")
        import traceback
        traceback.print_exc()
        response = jsonify({
            "status": 500,
            "message": f"Error saving game score: {str(e)}"
        })
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Credentials", "true")
        return response, 500
    

@view.route('/list-files')
def list_files():
    folder = "/opt/render/project/src"
    return jsonify(os.listdir(folder))

@view.route('/backup-db')
def backup_db():
    db_path = "/opt/render/project/src/instance/database.db"  

    if not os.path.exists(db_path):
        return {"error": "database.db not found"}, 404

    return send_file(
        db_path,
        as_attachment=True,
        download_name="database-backup.db"
    )
