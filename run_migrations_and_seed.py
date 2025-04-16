#!/usr/bin/env python3
from flask_migrate import upgrade
from werkzeug.security import generate_password_hash
from models import db, User, Post, Comment, Like
from app import app  # Import your actual Flask app

def seed_database():
    with app.app_context():
        if User.query.first():
            print("Data already exists. Skipping seeding.")
            return

        # Creating Users
        user1 = User(
            username="john_doe",
            email="john@example.com",
            password_hash=generate_password_hash("password123"),
            profile_image="https://via.placeholder.com/150"
        )

        user2 = User(
            username="jane_doe",
            email="jane@example.com",
            password_hash=generate_password_hash("securepass"),
            profile_image="https://via.placeholder.com/150"
        )
        db.session.add_all([user1, user2])
        db.session.commit()

        # Creating Posts
        post1 = Post(
            title="My First Blog Post",
            content="This is the content of my first blog post.",
            user_id=user1.id
        )

        post2 = Post(
            title="A Day in the Life",
            content="This is an article about my daily routine.",
            user_id=user2.id
        )

        db.session.add_all([post1, post2])
        db.session.commit()

        # Creating Comments
        comment1 = Comment(
            content="Great post!",
            user_id=user2.id,
            post_id=post1.id
        )

        comment2 = Comment(
            content="Thanks for sharing!",
            user_id=user1.id,
            post_id=post2.id
        )

        db.session.add_all([comment1, comment2])
        db.session.commit()

        print("Database seeded successfully!")

def run():
    with app.app_context():
        print(" Running database migrations...")
        upgrade()
        print("(>_<) Migrations complete.")

        print("Seeding database...")
        seed_database()

if __name__ == '__main__':
    run()
