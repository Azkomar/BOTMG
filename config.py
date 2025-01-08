import os
from dotenv import find_dotenv, load_dotenv

# find .env automatically
dotenvPath = find_dotenv()

# load up the entries as environment variables
load_dotenv(dotenvPath)

SECRET_KEY = os.getenv("SECRET_KEY")

# Configuration Flask-Mail
MAIL_SERVER = 'smtp.mailgun.org'  # Serveur SMTP de Mailgun
MAIL_PORT = 587  # Port SMTP
MAIL_USE_TLS = True  # Utiliser TLS (chiffrement)
MAIL_USE_SSL = False  # SSL désactivé
MAIL_USERNAME = 'postmaster@sandbox1c63be7e2b4441aba3d5fcd8b333ec85.mailgun.org'  # Votre adresse Mailgun
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_DEFAULT_SENDER = 'postmaster@sandbox1c63be7e2b4441aba3d5fcd8b333ec85.mailgun.org'  # Nom et e-mail de l'expéditeur
MAIL_MAX_EMAILS = None  # Nombre maximal d'e-mails à envoyer en une fois (facultatif)