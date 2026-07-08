from database import db

class Atelier(db.Model):

    __tablename__ = "ateliers"

    id = db.Column(db.Integer, primary_key=True)

    titre = db.Column(db.String(100), nullable=False)

    description = db.Column(db.Text)

    date = db.Column(db.String(20), nullable=False)

    heure = db.Column(db.String(10), nullable=False)

    duree = db.Column(db.String(20))

    niveau = db.Column(db.String(30))

    places = db.Column(db.Integer, default=10)

    image = db.Column(db.String(255))

    reservations = db.relationship(
        "Reservation",
        backref="atelier",
        cascade="all, delete-orphan",
        lazy=True
    )