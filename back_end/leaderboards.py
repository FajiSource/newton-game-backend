from flask import Blueprint, jsonify
from sqlalchemy import func
from . import db
from .models import User, Point

leaderboard = Blueprint("leaderboard", __name__)

@leaderboard.route("/leaderboard", methods=["GET"])
def leaderboards():
    try:
        results = db.session.query(
            User.id,
            User.username,
            func.max(Point.points).label('total_points')
        ).join(
            Point, User.id == Point.user_id
        ).group_by(
            User.id, User.username
        ).order_by(
            func.max(Point.points).desc()
        ).limit(10).all()
        
        leaderboard_data = []
        for rank, (user_id, username, total_points) in enumerate(results, start=1):
            leaderboard_data.append({
                'rank': rank,
                'username': username,
                'points': int(total_points) if total_points else 0
            })
        
        return jsonify({
            'status': 200,
            'leaderboard': leaderboard_data
        })
    except Exception as e:
        return jsonify({
            'status': 500,
            'message': f'Error fetching leaderboard: {str(e)}'
        }), 500