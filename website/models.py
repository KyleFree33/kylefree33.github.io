from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_public = db.Column(db.Boolean, default=True)
    vote_count = db.Column(db.Integer, default=0) 
    upvote_count = db.Column(db.Integer, default=0)
    downvote_count = db.Column(db.Integer, default=0)
    title = db.Column(db.String(100))
    parent_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    replies = db.relationship('Post', backref=db.backref('parent', remote_side=[id]), lazy=True)

class Vote(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), primary_key=True)
    vote = db.Column(db.Integer)

class UserVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    vote_type = db.Column(db.String(50))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    bio = db.Column(db.String(200))
    profile_picture = db.Column(db.LargeBinary(255))
    posts = db.relationship('Post', backref='user')
