SECRET_KEY = '29e50e4c8cdc3cc45ecc9f2553331fa1c12f5bec86ee51c0daa7571022c5960e'

# Configuration Flask-Mail
MAIL_SERVER = 'smtp.gmail.com'  # Serveur SMTP de Gmail
MAIL_PORT = 587  # Port SMTP
MAIL_USE_TLS = True  # Utiliser TLS (chiffrement)
MAIL_USE_SSL = False  # SSL désactivé
MAIL_USERNAME = 'azkorotmg@gmail.com'  # Votre adresse Gmail
MAIL_PASSWORD = 'doxkybuciotltxhg'  # Mot de passe ou mot de passe d'application Gmail
MAIL_DEFAULT_SENDER = ('ROTMGCollector', 'azkoROTMG@gmail.com')  # Nom et e-mail de l'expéditeur
MAIL_MAX_EMAILS = 5  # Nombre maximal d'e-mails à envoyer en une fois (facultatif)