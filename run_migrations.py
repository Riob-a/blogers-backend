from app import app
from models import db
from flask_migrate import upgrade

with app.app_context():
    upgrade()
