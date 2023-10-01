from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import current_user
from .models import Post, UserVote, Vote
from . import db
import json
from flask import redirect, url_for

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
def home():
    top_level_posts = Post.query.filter_by(parent_id=None).all()
    return render_template("home.html", user=current_user, posts=top_level_posts)


@views.route('/reply-to-post', methods=['POST'])
def reply_to_post():
    post_content = request.form.get('post')
    parent_post_id = request.form.get('parent_id')  # Get the parent post ID

    if not post_content or len(post_content) < 1:
        flash('Reply is too short!', category='error') 
    else:
        reply = Post(data=post_content, user_id=current_user.id, parent_id=parent_post_id)
        db.session.add(reply)
        db.session.commit()
        flash('Reply added!', category='success')
    
    post = Post.query.get_or_404(parent_post_id)
    replies = Post.query.filter_by(parent_id=parent_post_id).all()

    return render_template("post_detail.html", post=post, replies=replies, user=current_user)



@views.route('/delete-post', methods=['POST'])
def delete_post():  
    post = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    postId = post['postId']
    post = Post.query.get(postId)
    if post:
        if post.user_id == current_user.id:
            db.session.delete(post)
            db.session.commit()

    return jsonify({})

@views.route('/upvote-post', methods=['POST'])
def upvote_post():
    post_data = json.loads(request.data)
    postId = post_data['postId']
    post = Post.query.get(postId)
    if not current_user.is_authenticated:
        return jsonify({'error': 'Not authenticated', 'vote_count': post.vote_count})

    vote = Vote.query.filter_by(user_id=current_user.id, post_id=postId).first()
    if not vote:
        new_vote = Vote(user_id=current_user.id, post_id=postId, vote=1)
        db.session.add(new_vote)
        post.vote_count += 1
    else:
        if vote.vote == -1:
            vote.vote = 1
            post.vote_count += 2
        elif vote.vote == 1: # User has already upvoted
            db.session.delete(vote) # Removing the vote
            post.vote_count -= 1
    
    db.session.commit()
    return jsonify({'vote_count': post.vote_count})

@views.route('/downvote-post', methods=['POST'])
def downvote_post():
    post_data = json.loads(request.data)
    postId = post_data['postId']
    post = Post.query.get(postId)
    if not current_user.is_authenticated:
        return jsonify({'error': 'Not authenticated', 'vote_count': post.vote_count})

    vote = Vote.query.filter_by(user_id=current_user.id, post_id=postId).first()
    if not vote:
        new_vote = Vote(user_id=current_user.id, post_id=postId, vote=-1)
        db.session.add(new_vote)
        post.vote_count -= 1
    else:
        if vote.vote == 1:
            vote.vote = -1
            post.vote_count -= 2
        elif vote.vote == -1: # User has already downvoted
            db.session.delete(vote) # Removing the vote
            post.vote_count += 1

    db.session.commit()
    return jsonify({'vote_count': post.vote_count})

@views.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    
    if request.method == 'POST' and current_user.is_authenticated:
        reply_data = request.form.get('post')
        if not reply_data or len(reply_data) < 1:
            flash('Reply is too short!', category='error') 
        else:
            reply = Post(data=reply_data, user_id=current_user.id, parent_id=post_id)
            db.session.add(reply)
            db.session.commit()
            flash('Reply added!', category='success')
    
    replies = Post.query.filter_by(parent_id=post_id).all()

    return render_template("post_detail.html", post=post, replies=replies)

@views.route('/about', methods=['GET'])
def about():
    return render_template("about.html", user=current_user)

@views.route('/create_post', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        title = request.form.get('title')
        post_content = request.form.get('post')
        parent_post_id = request.form.get('parent_id')  # Get the parent post ID
        
        if not title or len(title) < 1:
            flash('Title is too short!', category='error')
        elif not post_content or len(post_content) < 1:
            flash('Post is too short!', category='error') 
        else:
            new_post = Post(title=title, data=post_content, user_id=current_user.id, parent_id=parent_post_id)
            db.session.add(new_post)
            db.session.commit()
            flash('Post added!', category='success')
            return redirect(url_for('views.home'))  # Redirecting to the homepage after successful post submission

    return render_template("post.html", user=current_user)