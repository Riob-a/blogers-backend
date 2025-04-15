from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import Post, Like, Dislike, db

like_bp = Blueprint('like_bp', __name__)

# ORIGINAL CODE
# @like_bp.route('/api/posts/<int:post_id>/like', methods=['POST'])
# @jwt_required()
# def like_post(post_id):
#     user_id = get_jwt_identity()
#     post = Post.query.get_or_404(post_id)

#     # Check if user already liked the post
#     existing_like = Like.query.filter_by(user_id=user_id, post_id=post_id).first()
#     if existing_like:
#         return jsonify({"message": "You already liked this post"}), 400

#     new_like = Like(user_id=user_id, post_id=post_id)
#     db.session.add(new_like)
#     db.session.commit()

#     return jsonify({"message": "Post liked", "like_count": Like.query.filter_by(post_id=post_id).count()}), 200  
@like_bp.route('/api/posts/<int:post_id>/like', methods=['POST'])
@jwt_required()
def like_post(post_id):
    user_id = get_jwt_identity()
    post = Post.query.get_or_404(post_id)

    # Prevent duplicate like
    if Like.query.filter_by(user_id=user_id, post_id=post_id).first():
        return jsonify({"message": "You already liked this post"}), 400

    # 🧹 Remove any existing dislike
    existing_dislike = Dislike.query.filter_by(user_id=user_id, post_id=post_id).first()
    if existing_dislike:
        db.session.delete(existing_dislike)

    new_like = Like(user_id=user_id, post_id=post_id)
    db.session.add(new_like)
    db.session.commit()

    return jsonify({
        "message": "Post liked",
        "like_count": Like.query.filter_by(post_id=post_id).count(),
        "dislike_count": Dislike.query.filter_by(post_id=post_id).count()
    }), 200


@like_bp.route("/api/posts/<int:post_id>/unlike", methods=['DELETE'])
@jwt_required()
def unlike_post(post_id):
    user_id = get_jwt_identity()
    post = Post.query.get_or_404(post_id)

    like = Like.query.filter_by(user_id=user_id, post_id=post_id).first()
    if not like:
        return jsonify({"message": "You haven't liked this post"}), 400

    db.session.delete(like)
    db.session.commit()

    return jsonify(post.to_dict(user_id)), 200


@like_bp.route('/api/posts/<int:post_id>/likes', methods=['GET'])
def get_post_likes(post_id):
    post = Post.query.get_or_404(post_id)
    return jsonify({"like_count": Like.query.filter_by(post_id=post_id).count()})  # Ensured consistency

# dislikes
@like_bp.route('/api/posts/<int:post_id>/dislike', methods=['POST'])
@jwt_required()
def dislike_post(post_id):
    user_id = get_jwt_identity()
    post = Post.query.get_or_404(post_id)

    # Prevent duplicate dislike
    if Dislike.query.filter_by(user_id=user_id, post_id=post_id).first():
        return jsonify({"message": "You already disliked this post"}), 400

    # Optionally remove like if it exists
    existing_like = Like.query.filter_by(user_id=user_id, post_id=post_id).first()
    if existing_like:
        db.session.delete(existing_like)

    new_dislike = Dislike(user_id=user_id, post_id=post_id)
    db.session.add(new_dislike)
    db.session.commit()

    return jsonify(post.to_dict(user_id)), 200


@like_bp.route('/api/posts/<int:post_id>/undislike', methods=['DELETE'])
@jwt_required()
def undislike_post(post_id):
    user_id = get_jwt_identity()
    post = Post.query.get_or_404(post_id)

    dislike = Dislike.query.filter_by(user_id=user_id, post_id=post_id).first()
    if not dislike:
        return jsonify({"message": "You haven't disliked this post"}), 400

    db.session.delete(dislike)
    db.session.commit()

    return jsonify(post.to_dict(user_id)), 200

@like_bp.route('/api/posts/<int:post_id>/dislikes', methods=['GET'])
def get_post_dislikes(post_id):
    post = Post.query.get_or_404(post_id)
    return jsonify({"dislike_count": Dislike.query.filter_by(post_id=post_id).count()})
