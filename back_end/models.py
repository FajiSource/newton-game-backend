from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(200))
    notes = db.relationship("Note")
    points = db.relationship("Point")
    completion = db.relationship("UserCompletion", backref="user", uselist=False)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

class Point(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    points = db.Column(db.Integer)
    point_date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

class UserCompletion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True)
    soccer_completed = db.Column(db.Boolean, default=False)
    rocket_completed = db.Column(db.Boolean, default=False)
    asteroid_completed = db.Column(db.Boolean, default=False)
    quiz_completed = db.Column(db.Boolean, default=False)
    quiz_score = db.Column(db.Float, default=0.0)
    all_completed = db.Column(db.Boolean, default=False)
    completed_date = db.Column(db.DateTime(timezone=True), nullable=True)
    updated_date = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())

class GameScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    game_type = db.Column(db.String(50))
    level = db.Column(db.Integer)
    best_score = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    updated_date = db.Column(db.DateTime(timezone=True), default=func.now(), onupdate=func.now())
    __table_args__ = (db.UniqueConstraint('user_id', 'game_type', 'level', name='unique_user_game_level'),)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    username = db.Column(db.String(150))  # Store username for display
    game_type = db.Column(db.String(50), nullable=True)  # null for overall feedback
    stars = db.Column(db.Integer)  # 1-5 stars
    comment = db.Column(db.Text)
    created_date = db.Column(db.DateTime(timezone=True), default=func.now())
    user = db.relationship("User", backref="feedbacks")