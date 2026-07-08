from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()


def demarrer_scheduler(app):

    from services.reminder_service import envoyer_rappels

    def job():

        with app.app_context():
            envoyer_rappels()

    scheduler.add_job(
    job,
    trigger="interval",
    hours=1,
    id="rappel_ateliers",
    replace_existing=True
    )

    scheduler.start()

    print("✅ Scheduler démarré.")