import os
from dotenv import find_dotenv, load_dotenv

# find .env automatically
dotenvPath = find_dotenv()

# load up the entries as environment variables
load_dotenv(dotenvPath)

SECRET_KEY = os.getenv("SECRET_KEY")

# Configuration Flask-Mail
MAIL_SERVER = 'smtp.gmail.com'  # Serveur SMTP de Gmail
MAIL_PORT = 587  # Port SMTP
MAIL_USE_TLS = True  # Utiliser TLS (chiffrement)
MAIL_USE_SSL = False  # SSL désactivé
MAIL_USERNAME = 'azkorotmg@gmail.com'  # Votre adresse Gmail
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_DEFAULT_SENDER = ('ROTMGCollector', 'azkoROTMG@gmail.com')  # Nom et e-mail de l'expéditeur
MAIL_MAX_EMAILS = 5  # Nombre maximal d'e-mails à envoyer en une fois (facultatif)