from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from models import User, db
from cloudinary.uploader import upload

auth_bp = Blueprint('auth', __name__)



@auth_bp.route('/api/register', methods=['POST'])
def register():
    # Access form data instead of JSON
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    profile_image = request.files.get('profile_image')  # This is the uploaded file

    if not username or not email or not password:
        return jsonify({'message': 'Missing fields'}), 400

    hashed_password = generate_password_hash(password)

    uploaded_image_url  = None

    if profile_image:
        try:
            print("Uploading image:", profile_image.filename)  # Debugging
            upload_result = upload(profile_image)
            uploaded_image_url = upload_result.get('secure_url')
            print("Upload successful:", uploaded_image_url)  # Debugging
        except Exception as e:
            print("Cloudinary Upload Error:", str(e))  # Print actual error
            return jsonify({'message': 'An error occurred while uploading the image', 'error': str(e)}), 400

    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({'message': 'Username or email already exists'}), 400

    new_user = User(
        username=username,
        email=email,
        password_hash=hashed_password,
        profile_image=uploaded_image_url 
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Username or email already exists'}), 400


@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()

    if user and check_password_hash(user.password_hash, data['password']):
        token = create_access_token(identity=user.id)
        return jsonify({'access_token': token,}), 200

    return jsonify({'message': 'Invalid credentials'}), 401

@auth_bp.route("/api/auth/me", methods=["GET"])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    return jsonify({"id": user_id}), 200

# @jwt.token_in_blocklist_loader
# def check_if_token_in_revoked(jwt_header, jwt_payload):
#     return jwt_payload['jti'] in revoked_tokens

