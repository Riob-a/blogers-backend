from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

from flask_jwt_extended import JWTManager,jwt_required, get_jwt
from models import db, User, Post, Comment, Genre, Like, Dislike
from routes.auth_routes import auth_bp
from routes.post_routes import post_bp
from routes.user_routes import user_bp
from routes.like_routes import like_bp
from routes.comments_routes import comments_bp

import cloudinary
from cloudinary.uploader import upload
import cloudinary.api

from dotenv import load_dotenv
import os

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_DATABASE_URL'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'secret_key'

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# print(os.getenv("CLOUDINARY_CLOUD_NAME"))
# print(os.getenv("CLOUDINARY_API_KEY"))  # Debugging
# print(os.getenv("CLOUDINARY_API_SECRET"))  # Debugging

db.init_app(app)
migrate = Migrate(app, db)
CORS(app)
jwt = JWTManager(app)

revoked_tokens = set()


@app.route('/')
def home():
    return jsonify({"message": "Welcome to bloggers"}), 200

# Logout route (put here to avoid circular imports)
@app.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    response = jsonify({'message': 'User logged out'})
    revoked_tokens.add(jti)

    return response, 200

@jwt.token_in_blocklist_loader
def check_if_token_in_revoked(jwt_header, jwt_payload):
    return jwt_payload['jti'] in revoked_tokens

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(post_bp)
app.register_blueprint(user_bp)
app.register_blueprint(comments_bp)
app.register_blueprint(like_bp)

if __name__ == '__main__':
    app.run(debug=True)
