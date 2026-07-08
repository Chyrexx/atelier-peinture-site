from database import db
from flask_login import UserMixin

class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    nom = db.Column(db.String(100), nullable=False)

    prenom = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(150), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), default="client")

    reservations = db.relationship(
        "Reservation",
        backref="utilisateur",
        cascade="all, delete-orphan",
        lazy=True
    )