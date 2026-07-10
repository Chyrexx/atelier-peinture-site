from flask import Flask, render_template, request, redirect

from flask_mail import Mail
from services.email_service import init_mail
from services.email_service import envoyer_email
from services.reminder_service import envoyer_rappels

from flask_login import LoginManager, login_required, current_user

from werkzeug.security import generate_password_hash, check_password_hash

from flask_migrate import Migrate

from config import Config
from database import db
from flask import flash

from models.atelier import Atelier
from models.reservation import Reservation
from models.oeuvre import Oeuvre
from models.user import User

from services.scheduler_service import demarrer_scheduler

import os
from werkzeug.utils import secure_filename

from routes.auth import auth

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

mail = Mail(app)

init_mail(mail)

print("===== CONFIG MAIL =====")
print("MAIL_USERNAME :", app.config["MAIL_USERNAME"])
print("MAIL_PASSWORD :", "OK" if app.config["MAIL_PASSWORD"] else "VIDE")
print("=======================")

migrate = Migrate(app, db)

with app.app_context():

    db.create_all()

    ADMIN_EMAIL = app.config["ADMIN_EMAIL"]
    ADMIN_PASSWORD = app.config["ADMIN_PASSWORD"]

    admin = User.query.filter_by(email=ADMIN_EMAIL).first()

    if admin is None:

        admin = User(
            nom="Maman",
            prenom="Admin",
            email=ADMIN_EMAIL,
            password=generate_password_hash(ADMIN_PASSWORD),
            role="admin"
        )

        db.session.add(admin)
        db.session.commit()

demarrer_scheduler(app)

app.register_blueprint(auth)
# -----------------------------
# Flask Login
# -----------------------------

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# -----------------------------
# Pages publiques
# -----------------------------

@app.route("/")
def accueil():
    return render_template("index.html")


@app.route("/planning")
def planning():

    ateliers = Atelier.query.all()

    return render_template(
        "planning.html",
        ateliers=ateliers
    )

@app.route("/mes-reservations")
@login_required
def mes_reservations():

    reservations = Reservation.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template(
        "mes_reservations.html",
        reservations=reservations
    )

@app.route("/galerie")
def galerie():

    oeuvres = Oeuvre.query.order_by(
        Oeuvre.date_ajout.desc()
    ).all()

    return render_template(
        "galerie.html",
        oeuvres=oeuvres
    )


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/apropos")
def apropos():
    return render_template("apropos.html")


# -----------------------------
# Administration
# -----------------------------

@app.route("/admin")
@login_required
def admin():

    if current_user.role != "admin":
        return redirect("/")

    nb_ateliers = Atelier.query.count()

    nb_reservations = Reservation.query.count()

    nb_oeuvres = Oeuvre.query.count()

    nb_utilisateurs = User.query.count()
    
    prochains_ateliers = (
        Atelier.query
        .order_by(Atelier.date.asc(), Atelier.heure.asc())
        .limit(5)
        .all()
    )
    
    dernieres_reservations = (
    Reservation.query
    .order_by(Reservation.date_reservation.desc())
    .limit(5)
    .all()
    )
    
    
    
    return render_template(

    "admin/dashboard.html",

    nb_ateliers=nb_ateliers,
    nb_reservations=nb_reservations,
    nb_oeuvres=nb_oeuvres,
    nb_utilisateurs=nb_utilisateurs,

    prochains_ateliers=prochains_ateliers,
    dernieres_reservations=dernieres_reservations

    )


@app.route("/admin/ajouter", methods=["POST"])
@login_required
def ajouter_atelier():

    if current_user.role != "admin":
        return redirect("/")

    atelier = Atelier(
        titre=request.form["titre"],
        description=request.form["description"],
        date=request.form["date"],
        heure=request.form["heure"],
        duree=request.form["duree"],
        niveau=request.form["niveau"],
        places=int(request.form["places"])
    )

    db.session.add(atelier)
    db.session.commit()

    return redirect("/admin")

@app.route("/admin/supprimer/<int:id>")
def supprimer_atelier(id):

    atelier = Atelier.query.get_or_404(id)

    db.session.delete(atelier)

    db.session.commit()

    return redirect("/admin")


@app.route("/admin/modifier/<int:id>", methods=["GET", "POST"])
@login_required
def modifier_atelier(id):

    if current_user.role != "admin":
        return redirect("/")

    atelier = Atelier.query.get_or_404(id)

    if request.method == "POST":

        atelier.titre = request.form["titre"]
        atelier.description = request.form["description"]
        atelier.date = request.form["date"]
        atelier.heure = request.form["heure"]
        atelier.duree = request.form["duree"]
        atelier.niveau = request.form["niveau"]
        atelier.places = int(request.form["places"])

        db.session.commit()

        return redirect("/admin/ateliers")

    return render_template(
        "modifier_atelier.html",
        atelier=atelier
    )

@app.route("/admin/ateliers")
@login_required
def admin_ateliers():

    if current_user.role != "admin":
        return redirect("/")

    ateliers = Atelier.query.order_by(
        Atelier.date.asc(),
        Atelier.heure.asc()
    ).all()

    return render_template(
        "admin/ateliers.html",
        ateliers=ateliers
    )
    
@app.route("/admin/reservations")
@login_required
def admin_reservations():

    if current_user.role != "admin":
        return redirect("/")

    reservations = (
        Reservation.query
        .order_by(Reservation.date_reservation.desc())
        .all()
    )

    return render_template(
        "admin/reservations.html",
        reservations=reservations
    )
    
@app.route("/admin/utilisateurs")
@login_required
def admin_utilisateurs():

    if current_user.role != "admin":
        return redirect("/")

    utilisateurs = (
        User.query
        .order_by(User.nom.asc(), User.prenom.asc())
        .all()
    )

    return render_template(
        "admin/utilisateurs.html",
        utilisateurs=utilisateurs
    )

@app.route("/admin/oeuvre/modifier/<int:id>", methods=["POST"])
@login_required
def modifier_oeuvre(id):

    if current_user.role != "admin":
        return redirect("/")

    oeuvre = Oeuvre.query.get_or_404(id)

    oeuvre.titre = request.form["titre"]
    oeuvre.description = request.form["description"]

    fichier = request.files.get("image")

    if fichier and fichier.filename != "":

        nom_fichier = secure_filename(fichier.filename)

        chemin = os.path.join(
            "static",
            "uploads",
            "oeuvres",
            nom_fichier
        )

        fichier.save(chemin)

        oeuvre.image = nom_fichier

    db.session.commit()

    flash(
        "Œuvre modifiée avec succès.",
        "success"
    )

    return redirect("/admin/oeuvres")

@app.route("/admin/oeuvre/supprimer/<int:id>")
@login_required
def supprimer_oeuvre(id):

    if current_user.role != "admin":
        return redirect("/")

    oeuvre = Oeuvre.query.get_or_404(id)

    # Supprimer l'image du disque si elle existe
    if oeuvre.image:

        chemin = os.path.join(
            "static",
            "uploads",
            "oeuvres",
            oeuvre.image
        )

        if os.path.exists(chemin):
            os.remove(chemin)

    db.session.delete(oeuvre)
    db.session.commit()

    flash(
        "Œuvre supprimée avec succès.",
        "success"
    )

    return redirect("/admin/oeuvres")

@app.route("/admin/utilisateur/<int:id>")
@login_required
def voir_utilisateur(id):

    if current_user.role != "admin":
        return redirect("/")

    utilisateur = User.query.get_or_404(id)

    return render_template(
        "admin/utilisateur.html",
        utilisateur=utilisateur
    )
    
@app.route("/admin/utilisateur/supprimer/<int:id>")
@login_required
def supprimer_utilisateur(id):

    if current_user.role != "admin":
        return redirect("/")

    utilisateur = User.query.get_or_404(id)

    # Impossible de supprimer un administrateur
    if utilisateur.role == "admin":

        flash(
            "Impossible de supprimer un administrateur.",
            "danger"
        )

        return redirect("/admin/utilisateurs")

    db.session.delete(utilisateur)
    db.session.commit()

    flash(
        "Utilisateur supprimé avec succès.",
        "success"
    )

    return redirect("/admin/utilisateurs")

# -----------------------------
# Lancement
# -----------------------------

@app.route("/reservation/<int:atelier_id>")
@login_required
def reserver(atelier_id):

    atelier = Atelier.query.get_or_404(atelier_id)

    # Vérifie qu'il reste des places
    if atelier.places <= 0:
        return "Désolé, cet atelier est complet."

    # Vérifie si l'utilisateur a déjà réservé
    reservation = Reservation.query.filter_by(
        user_id=current_user.id,
        atelier_id=atelier.id
    ).first()

    if reservation:
        return "Vous avez déjà réservé cet atelier."

    nouvelle_reservation = Reservation(
    user_id=current_user.id,
    atelier_id=atelier.id,
    rappel_envoye=False
    )

    db.session.add(nouvelle_reservation)

    atelier.places -= 1

    db.session.commit()

    # ==========================
    # Email au client
    # ==========================

    envoyer_email(
        destinataire=current_user.email,
        sujet="🎨 Votre réservation est confirmée",
        template="emails/reservation_client.html",
        utilisateur=current_user,
        atelier=atelier
    )

    # ==========================
    # Email à l'administratrice
    # ==========================

    envoyer_email(
        destinataire=app.config["ADMIN_EMAIL"],
        sujet="📌 Nouvelle réservation",
        template="emails/reservation_admin.html",
        utilisateur=current_user,
        atelier=atelier
    )

    return redirect("/mes-reservations")

@app.route("/mon-compte")
@login_required
def mon_compte():

    reservations = Reservation.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template(
        "mon_compte.html",
        reservations=reservations
    )

@app.route("/modifier-profil", methods=["GET", "POST"])
@login_required
def modifier_profil():

    if request.method == "POST":

        current_user.nom = request.form["nom"]

        current_user.prenom = request.form["prenom"]

        current_user.email = request.form["email"].lower().strip()

        db.session.commit()

        return redirect("/mon-compte")

    return render_template("modifier_profil.html")

@app.route("/changer-mot-de-passe", methods=["GET", "POST"])
@login_required
def changer_mot_de_passe():

    if request.method == "POST":

        ancien = request.form["ancien"]
        nouveau = request.form["nouveau"]
        confirmation = request.form["confirmation"]

        # Vérifie l'ancien mot de passe
        if not check_password_hash(current_user.password, ancien):
            return "Ancien mot de passe incorrect."

        # Vérifie la confirmation
        if nouveau != confirmation:
            return "Les nouveaux mots de passe ne correspondent pas."

        # Enregistre le nouveau mot de passe
        current_user.password = generate_password_hash(nouveau)

        db.session.commit()

        return redirect("/mon-compte")

    return render_template("changer_mot_de_passe.html")

@app.route("/annuler-reservation/<int:id>")
@login_required
def annuler_reservation(id):

    reservation = Reservation.query.get_or_404(id)

    # Sécurité : seul le propriétaire ou un admin peut annuler
    if reservation.user_id != current_user.id and current_user.role != "admin":
        return redirect("/")

    atelier = reservation.atelier

    atelier.places += 1

        # ==========================
    # Email au client
    # ==========================

    envoyer_email(
        destinataire=current_user.email,
        sujet="❌ Réservation annulée",
        template="emails/annulation_client.html",
        utilisateur=current_user,
        atelier=atelier
    )

    # ==========================
    # Email à l'administratrice
    # ==========================

    envoyer_email(
        destinataire=app.config["ADMIN_EMAIL"],
        sujet="❌ Annulation d'une réservation",
        template="emails/annulation_admin.html",
        utilisateur=current_user,
        atelier=atelier
    )
    
    db.session.delete(reservation)

    db.session.commit()

    return redirect("/mes-reservations")

@app.route("/admin/atelier/<int:id>")
@login_required
def participants_atelier(id):

    if current_user.role != "admin":
        return redirect("/")

    atelier = Atelier.query.get_or_404(id)

    reservations = Reservation.query.filter_by(
        atelier_id=id
    ).all()

    return render_template(
    "admin/participants.html",
    atelier=atelier,
    reservations=reservations
    )
    
@app.route("/test-email")
@login_required
def test_email():

    atelier = Atelier.query.first()

    envoyer_email(
        destinataire=current_user.email,
        sujet="🎨 Test du système d'e-mails",
        template="emails/reservation_client.html",
        utilisateur=current_user,
        atelier=atelier
    )

    return "✅ Email envoyé ! Vérifie ta boîte de réception."

@app.route("/test-rappel")
@login_required
def test_rappel():

    envoyer_rappels()

    return "✅ Rappels envoyés."

@app.route("/admin/oeuvres", methods=["GET", "POST"])
@login_required
def admin_oeuvres():

    if current_user.role != "admin":
        return redirect("/")

    if request.method == "POST":

        titre = request.form["titre"]
        description = request.form["description"]

        fichier = request.files["image"]

        if fichier:

            nom_fichier = secure_filename(fichier.filename)

            chemin = os.path.join(
                "static",
                "uploads",
                "oeuvres",
                nom_fichier
            )

            fichier.save(chemin)

            oeuvre = Oeuvre(
                titre=titre,
                description=description,
                image=nom_fichier
            )

            db.session.add(oeuvre)
            db.session.commit()

            return redirect("/admin/oeuvres")

    oeuvres = Oeuvre.query.order_by(
        Oeuvre.date_ajout.desc()
    ).all()

    return render_template(
    "admin/admin_oeuvres.html",
    oeuvres=oeuvres
    )

if __name__ == "__main__":
    app.run(debug=True)