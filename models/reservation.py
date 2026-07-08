from database import db

class Reservation(db.Model):

    __tablename__ = "reservations"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    atelier_id = db.Column(
        db.Integer,
        db.ForeignKey("ateliers.id"),
        nullable=False
    )

    date_reservation = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )
    
    rappel_envoye = db.Column(
    db.Boolean,
    default=False,
    nullable=False
)