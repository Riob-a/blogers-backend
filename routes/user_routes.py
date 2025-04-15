from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, db
from werkzeug.utils import secure_filename
import cloudinary
from cloudinary.uploader import upload

import os

user_bp = Blueprint('user', __name__)


@user_bp.route('/api/profile', methods=['GET'])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    return jsonify({'username': user.username, 'email': user.email, 'profile_image': user.profile_image, 'created_at': user.created_at }), 200

@user_bp.route('/api/profile/update', methods=['PATCH'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)

    print("Request received:", request.form)  # Debugging
    print("Files received:", request.files)  # Debugging

    username = request.form.get('username')
    email = request.form.get('email')
    profile_image = request.files.get('profile_image')

    if not username and not email and not profile_image:
        return jsonify({'message': 'No data provided'}), 400

    if username:
        user.username = username
    if email:
        user.email = email

    if profile_image:
        try:
            # Upload image to Cloudinary
            upload_result = upload(profile_image)
            user.profile_image = upload_result.get('secure_url')  # Save the Cloudinary URL in the database
        except Exception as e:
            print("Cloudinary Upload Error:", e) # Print the error for debugging
            return jsonify({'message': 'Failed to upload image', 'error': str(e)}), 400

    db.session.commit()

    return jsonify({
        'username': user.username,
        'email': user.email,
        'profile_image': user.profile_image,
        'created_at': user.created_at
    })
    
# currently being tested
@user_bp.route('/api/users/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'username': user.username,
        'profile_image': user.profile_image,
    }), 200

