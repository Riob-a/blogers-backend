from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Comment, User, Post
from datetime import datetime

comments_bp = Blueprint('comments', __name__)

# GET all comments (Optional: filter by post_id)
@comments_bp.route('/api/comments', methods=['GET'])
def get_comments():
    post_id = request.args.get('post_id')
    if post_id:
        comments = Comment.query.filter_by(post_id=post_id).all()
    else:
        comments = Comment.query.all()

    return jsonify([{
        'id': comment.id,
        'content': comment.content,
        'user_id': comment.user_id,
        'post_id': comment.post_id,
        'created_at': comment.created_at,
        'updated_at': comment.updated_at
    } for comment in comments]), 200

# GET a specific comment by ID
@comments_bp.route('/api/comments/<int:comment_id>', methods=['GET'])
def get_comment(comment_id):
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({'error': 'Comment not found'}), 404

    return jsonify({
        'id': comment.id,
        'content': comment.content,
        'user_id': comment.user_id,
        'post_id': comment.post_id,
        'created_at': comment.created_at,
        'updated_at': comment.updated_at
    }), 200

# POST a new comment (requires authentication)
@comments_bp.route('/api/comments', methods=['POST'])
@jwt_required()
def create_comment():
    data = request.get_json()
    user_id = get_jwt_identity()
    
    if 'content' not in data or 'post_id' not in data:
        return jsonify({'error': 'Content and post_id are required'}), 400

    # Check if the post exists
    post = Post.query.get(data['post_id'])
    if not post:
        return jsonify({'error': 'Post not found'}), 404

    new_comment = Comment(
        content=data['content'],
        user_id=user_id,
        post_id=data['post_id']
    )
    db.session.add(new_comment)
    db.session.commit()

    return jsonify({'message': 'Comment created', 'comment_id': new_comment.id}), 201

# PATCH (update) a comment (only owner can update)
@comments_bp.route('/api/comments/<int:comment_id>', methods=['PATCH'])
@jwt_required()
def update_comment(comment_id):
    comment = Comment.query.get(comment_id)
    user_id = get_jwt_identity()

    if not comment:
        return jsonify({'error': 'Comment not found'}), 404

    if comment.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    if 'content' in data:
        comment.content = data['content']
        comment.updated_at = datetime.utcnow()

    db.session.commit()

    return jsonify({'message': 'Comment updated'}), 200

# DELETE a comment (only owner can delete)
@comments_bp.route('/api/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    comment = Comment.query.get(comment_id)
    user_id = get_jwt_identity()

    if not comment:
        return jsonify({'error': 'Comment not found'}), 404

    if comment.user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(comment)
    db.session.commit()

    return jsonify({'message': 'Comment deleted'}), 200
