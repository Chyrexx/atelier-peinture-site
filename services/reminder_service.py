from datetime import datetime, timedelta

from database import db
from models.atelier import Atelier
from services.email_service import envoyer_email


def envoyer_rappels():

    # Date de demain
    demain = (
        datetime.now() + timedelta(days=1)
    ).strftime("%Y-%m-%d")

    print(f"Recherche des ateliers du {demain}")

    ateliers = Atelier.query.filter_by(
        date=demain
    ).all()

    print(f"{len(ateliers)} atelier(s) trouvé(s).")

    for atelier in ateliers:

        print(f"Atelier : {atelier.titre}")

        for reservation in atelier.reservations:

            # Si le rappel a déjà été envoyé, on passe à la réservation suivante
            if reservation.rappel_envoye:
                continue

            print(
                f"Envoi à {reservation.utilisateur.email}"
            )

            envoyer_email(
                destinataire=reservation.utilisateur.email,
                sujet="🎨 Rappel de votre atelier demain",
                template="emails/rappel_client.html",
                utilisateur=reservation.utilisateur,
                atelier=atelier
            )

            # On marque le rappel comme envoyé
            reservation.rappel_envoye = True

    # On enregistre toutes les modifications une seule fois
    db.session.commit()

    print("✅ Vérification des rappels terminée.")