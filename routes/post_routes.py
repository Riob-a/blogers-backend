from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from models import Post, Genre, db

post_bp = Blueprint('post', __name__)


@post_bp.route('/api/posts', methods=['POST'])
@jwt_required()
def create_post():
    data = request.get_json()
    user_id = get_jwt_identity()

    new_post = Post(title=data['title'], content=data['content'], user_id=user_id)

    if 'genres' in data:
        genre_names = data['genres']
        genres = []
        for name in genre_names:
            genre = Genre.query.filter_by(name=name).first()
            if not genre:
                genre = Genre(name=name)
                db.session.add(genre)
            genres.append(genre)

        new_post.genres = genres
        
    db.session.add(new_post)
    db.session.commit()
    return jsonify({'id': new_post.id, 'message': 'Post created successfully'}), 201

@post_bp.route('/api/posts', methods=['GET'])
def get_posts():
    try:
        verify_jwt_in_request(optional=True)
        user_id = get_jwt_identity()
    except Exception:
        user_id = None

    posts = Post.query.all()
    return jsonify([
        post.to_dict(user_id) for post in posts
    ])

   
# ORIGINAL CODE
# @post_bp.route('/api/posts', methods=['GET'])
# def get_posts():
#     posts = Post.query.all()
#     return jsonify([
#         {
#             'id': post.id,
#             'title': post.title, 
#             'content': post.content, 
#             'username': post.user.username,
#             'genres': [genre.name for genre in post.genres] if post.genres else []
#         } for post in posts
#     ])


@post_bp.route('/api/posts/<int:id>', methods=['GET'])
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify({
        'id': post.id, 
        'title': post.title, 
        'content': post.content, 
        'username': post.user.username, 
        'user_id': post.user_id, 
        'created_at': post.created_at, 
        'genres': [genre.name for genre in post.genres]
        })
    # added username to the response


@post_bp.route('/api/user/posts', methods=['GET'])
@jwt_required()
def get_user_posts():
    user_id = get_jwt_identity()
    print(f"JWT user_id: {user_id}")
    posts = Post.query.filter_by(user_id=user_id).all()
    print(f"Posts: {posts}")
    return jsonify([
        {'id': post.id, 
        'title': post.title, 
        'content': post.content,
        'genres': [genre.name for genre in post.genres]
        } for post in posts
])

@post_bp.route('/api/posts/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_post(id):
    user_id = get_jwt_identity()  # Get the authenticated user's ID
    post = Post.query.get_or_404(id)

    if post.user_id != user_id:
        return jsonify({'error': 'You are not authorized to delete this post'}), 403

    db.session.delete(post)
    db.session.commit()
    
    return jsonify({'message': 'Post deleted successfully'}), 200

@post_bp.route('/api/posts/<int:id>', methods=['PUT'])
@jwt_required()
def update_post(id):
    user_id = get_jwt_identity()
    post = Post.query.get_or_404(id)

    if post.user_id != user_id:
        return jsonify({'error': 'You are not authorized to edit this post'}), 403

    data = request.get_json()

    # Update title and content if provided
    if 'title' in data:
        post.title = data['title']
    if 'content' in data:
        post.content = data['content']

    # Optional: update genres
    if 'genres' in data:
        genre_names = data['genres']
        genres = []
        for name in genre_names:
            genre = Genre.query.filter_by(name=name).first()
            if not genre:
                genre = Genre(name=name)
                db.session.add(genre)
            genres.append(genre)
        post.genres = genres

    db.session.commit()

    return jsonify({'message': 'Post updated successfully', 'post': post.to_dict(user_id)}), 200

        
    
# @post_bp.route('/api/posts/latest', methods=['GET'])
# def get_latest_post():
#     latest_post = Post.query.order_by(Post.created_at.desc()).first()
#     if latest_post:
#         return jsonify({
#             "id": latest_post.id,
#             "title": latest_post.title,
#             "content": latest_post.content[:150] + "...",  # Shortened excerpt
#             "user_id": latest_post.user_id,
#             "created_at": latest_post.created_at.strftime('%Y-%m-%d %H:%M:%S')  # Format datetime
#         })
#     return jsonify({"error": "No posts found"}), 404