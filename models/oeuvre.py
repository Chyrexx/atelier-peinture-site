from database import db


class Oeuvre(db.Model):

    __tablename__ = "oeuvres"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    titre = db.Column(
        db.String(150),
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    image = db.Column(
        db.String(255),
        nullable=False
    )

    date_ajout = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )