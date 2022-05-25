from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    db.app = app
    db.init_app(app)
    with app.app_context():
        db.create_all()


class User(db.Model):
    __tablename__ = 'users'
    username = db.Column(
        db.String(20), 
        primary_key=True,
        unique=True,
        )
    password = db.Column(
        db.Text,
        nullable=False
        )
    email = db.Column(
        db.String(50),
        nullable=False,
        unique=True
        )
    first_name = db.Column(
        db.String(30),
        nullable=False
        )
    last_name = db.Column(
        db.String(30),
        nullable=False
        )