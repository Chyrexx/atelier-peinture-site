from flask import Blueprint, render_template, request, redirect, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user

from database import db
from models.user import User

auth = Blueprint("auth", __name__)


# ==========================
# INSCRIPTION
# ==========================

@auth.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        nom = request.form["nom"]
        prenom = request.form["prenom"]
        email = request.form["email"].lower().strip()
        password = request.form["password"]
        confirmation = request.form["confirmation"]

        if password != confirmation:
            flash("Les mots de passe ne correspondent pas.")
            return redirect("/register")

        utilisateur = User.query.filter_by(email=email).first()

        if utilisateur:
            flash("Cette adresse e-mail existe déjà.")
            return redirect("/register")

        nouvel_utilisateur = User(
            nom=nom,
            prenom=prenom,
            email=email,
            password=generate_password_hash(password),
            role="client"
        )

        db.session.add(nouvel_utilisateur)
        db.session.commit()

        login_user(nouvel_utilisateur)

        return redirect("/")

    return render_template("register.html")


# ==========================
# CONNEXION
# ==========================

@auth.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].lower().strip()
        password = request.form["password"]

        utilisateur = User.query.filter_by(email=email).first()

        if utilisateur and check_password_hash(utilisateur.password, password):

            login_user(utilisateur)

            return redirect("/")

        flash("Adresse e-mail ou mot de passe incorrect.")

    return render_template("login.html")


# ==========================
# DÉCONNEXION
# ==========================

@auth.route("/logout")
def logout():

    logout_user()

    return redirect("/")