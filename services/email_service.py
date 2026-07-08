from flask_mail import Mail, Message
from flask import render_template

mail = None


def init_mail(mail_instance):
    global mail
    mail = mail_instance


def envoyer_email(destinataire, sujet, template, **kwargs):

    html = render_template(
        template,
        **kwargs
    )

    message = Message(
        subject=sujet,
        recipients=[destinataire],
        html=html
    )

    try:
        mail.send(message)
        print("✅ Email envoyé avec succès")
    except Exception as e:
        print("❌ ERREUR SMTP")
        print(type(e))
        print(e)
        raise