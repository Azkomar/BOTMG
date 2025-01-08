import re
import psycopg2
from psycopg2 import sql
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4
from flask_mail import Mail, Message

def newError(error, func, message, conn):
    # Function used to log error into a database
    """
    The parameters are :
        error -> It's the name of the error
        func -> It's the name of the function where the error appeared
        message -> The message link to the error
    """
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO errorLog (errorName, date, function, message) VALUES (%s, NOW(), %s, %s)", (str(error), str(func), str(message)))
            conn.commit()
    except Exception as e:
        print("An error occured during the error logging...")

def newUser(username, password, conn):
    # Fonction utilisée pour créer un nouvel utilisateur si les paramètres sont valides
    try:
        # Avec cette connexion, le curseur est également géré via un "with"
        with conn.cursor() as cur:
            # Vérifier si le nom d'utilisateur est déjà pris
            cur.execute("SELECT 1 FROM users WHERE username = %s", (username,))
            if cur.fetchone() is not None:
                # Si le nom d'utilisateur existe déjà, retourner une erreur 401
                return 401

            # Sécuriser le mot de passe en utilisant une fonction de hachage
            hashPass = generate_password_hash(password)

            # Générer un ID unique avec UUID
            id = str(uuid4())

            # Insérer le nouvel utilisateur dans la table "users"
            data = (username, hashPass, id)

            # Insérer les données dans la table 'users'
            cur.execute("INSERT INTO users (username, hash, id) VALUES (%s, %s, %s)", data)
            # Valider la transaction (commit)
            conn.commit()
            if (newUserDB(id, conn) is not True):
                conn.rollback()
                return 400

            return 200
    except psycopg2.OperationalError as e:
        # Gérer les erreurs liées à la base de données
        newError(e, newUser.__name__, "Erreur avec SQL lors de la création d'un nouvel utilisateur", conn)
        conn.rollback()
        return 400
    
    except Exception as e:
        # Gérer toute autre erreur
        newError(e, newUser.__name__, "Erreur inconnue lors de la création d'un nouvel utilisateur", conn)
        conn.rollback()
        return 400
    
def newUserDB(id, conn):
    """
    Crée une nouvelle entrée dans la table 'itemStates' pour chaque item existant,
    associé à l'ID utilisateur.
    Retourne True si l'opération est réussie, sinon False.
    """
    try:
        with conn.cursor() as cur:
            # Insertion des données dans itemStates
            query = """
                INSERT INTO itemStates (userid, itemid, state)
                SELECT users.id, items.id, 0
                FROM users, items
                WHERE users.id = %s
            """
            cur.execute(query, (id,))
            conn.commit()
            return True
    except psycopg2.OperationalError as e:
        newError(e, newUserDB.__name__, "Erreur SQL lors de l'insertion dans itemStates", conn)
        conn.rollback()
        return False
    except Exception as e:
        newError(e, newUserDB.__name__, "Erreur inattendue", conn)
        conn.rollback()
        return False

def checkLogin(username, password, conn):
    # Check if the login information match the database
    username = tuple([username])
    try:
        with conn.cursor() as cur:
            # Check if username exist in the database
            cur.execute("SELECT username FROM users WHERE username = %s", username)
            if cur.fetchone() is not None:
                # If username exist, check if the password hashing correspond
                cur.execute("SELECT hash FROM users WHERE username = %s", username)
                hashPass = cur.fetchall()
                hashPass = hashPass[0][0]
                # If everything match return 200 status
                if check_password_hash(hashPass, password):
                    return 200
                # Else return 400 / error status
                else :
                    return 400
            # If username doesn't exist in the DB, return error
            else:
                return 400
    except psycopg2.OperationalError as e:
        newError(e, checkLogin.__name__, "Error with SQL during the connexion of a user", conn)
        return 400
    except Exception as e:
        newError(e, checkLogin.__name__, "Unknow error during the connexion of a user", conn)
        return 400
        

def getId(username, conn):
    # Get an id corresponding to the username
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE username = %s", (username,))
            id = cur.fetchall()
            return id[0][0]
    # If an error occured, return 0 value
    except psycopg2.OperationalError as e:
        newError(e, getId.__name__, "Error with SQL when getting the user's id", conn)
        return 0
    except Exception as e:
        newError(e, getId.__name__, "Unknow error when getting the user's id", conn)
        return 0

def getListItems(session, conn):
    # Use to get the list of all the existing items
    try:
        with conn.cursor() as cur:
            query = sql.SQL("SELECT i.*, s.state FROM items i JOIN itemStates s ON i.id = s.itemid WHERE s.userid = %s ORDER BY i.name;")
            cur.execute(query, (session["user_id"],))
            listItems = cur.fetchall()
            return listItems
    # If an error occured, return empty list
    except psycopg2.OperationalError as e:
        newError(e, getListItems.__name__, "Error with SQL when getting the list of all the items", conn)
        return []
    except Exception as e:
        newError(e, getListItems.__name__, "Unknow error when getting the list of all the items", conn)
        return []

def update(session, genre, conn):
    # Use to update the state of the items in the sort page
    allowed_genres = ["dungeon", "ust", "type"]  # Liste des noms de colonnes autorisés
    if genre not in allowed_genres:
        raise ValueError("Genre invalide")
    try:
        with conn.cursor() as cur:
            # Get a list order by the selected 'genre' (dungeon, type, ust)
            query = sql.SQL("SELECT DISTINCT(i.{column}), COUNT(i.{column}), SUM(s.state) FROM items i JOIN itemStates s ON i.id = s.itemid WHERE s.userid = %s GROUP BY (i.{column}) ORDER BY (i.{column})").format(
                column=sql.Identifier(genre))
            cur.execute(query, (session["user_id"],))
            listGenre = cur.fetchall()
            return listGenre
    # If an error occured, return empty list
    except psycopg2.OperationalError as e:
        newError(e, update.__name__, "Error with SQL when updating the states of a list of items", conn)
        return []
    except Exception as e:
        newError(e, update.__name__, "Unknow error when updating the states of a list of items", conn)
        return []
    
def countItm(session, conn):
    # Refresh the progress bar with the current number of items by looking for the total number of 'active' items
    # Connexion to bank.db
    try:
        with conn.cursor() as cur:
            result = 0
            query = sql.SQL("SELECT SUM(state) FROM itemStates WHERE userid = %s")
            cur.execute(query, (session["user_id"],))
            result = cur.fetchone()[0]
            return result
    except psycopg2.OperationalError as e:
        newError(e, countItm.__name__, "Error with SQL when counting all the active items", conn)
        return 0
    except Exception as e:
        newError(e, countItm.__name__, "Unknow error when counting all the active items", conn)
        return 0

def updateUserItem(session, itemId, conn) :
    # Update the state of a specific item by looking at his previous state
    try:
        with conn.cursor() as cur:
            query = sql.SQL("SELECT state FROM itemStates WHERE itemid = %s AND userid = %s")
            cur.execute(query, (itemId, session["user_id"]))
            itemState = cur.fetchone()[0]
            if itemState == 0:
                query = sql.SQL("UPDATE itemStates SET state = 1 WHERE itemid = %s AND userid = %s")
                cur.execute(query, (itemId, session["user_id"]))
                state = 1
            else :
                query = sql.SQL("UPDATE itemStates SET state = 0 WHERE itemid = %s AND userid = %s")
                cur.execute(query, (itemId, session["user_id"]))
                state = 0
            conn.commit()
            return state
    # If an error occured, return empty list
    except psycopg2.OperationalError as e:
        newError(e, updateUserItem.__name__, "Error with SQL when updating the state of a specific item", conn)
        return 0
    except Exception as e:
        newError(e, updateUserItem.__name__, "Unknow error when updating the state of a specific item", conn)
        return 0
def sortPage(req, session, conn):
    # Return the list corresponding to the selected 'object' in the selected 'genre'
    # Exemple : Return all the items of the 'dungeon' 'Void'
    
    # Loop throught 'listType' to get the total amount of items in this specific object
    try:
        with conn.cursor() as cur:
            query = sql.SQL("SELECT i.name, i.id, s.state, i.url FROM items i JOIN itemStates s ON i.id = s.itemid WHERE i.{columnType} = %s AND s.userid = %s").format(
                        columnType=sql.Identifier(session["genre"]))
            cur.execute(query, (req, session["user_id"]))
            liste = cur.fetchall()
            query = sql.SQL("SELECT i.{column}, COUNT(i.{column}), SUM(s.state) FROM items i JOIN itemStates s ON i.id = s.itemid WHERE i.{column} = %s AND s.userid = %s GROUP BY (i.{column}) ORDER BY (i.{column})").format(
                column=sql.Identifier(session["genre"]))
            
            cur.execute(query, (req, session["user_id"]))
            djnState = cur.fetchall()

            response = {
                "liste" : liste,
                "djnState" : djnState
            }
            return response
    except psycopg2.OperationalError as e:
        newError(e, sortPage.__name__, "Error with SQL when showing items in sort page", conn)
        return 0
    except Exception as e:
        newError(e, sortPage.__name__, "Unknow error when showing items in sort page", conn)
        return 0

def sendEmail(name, email, subject, message, mail, conn):
    # Create a Message object to send it with Flask-Mail
    try:
        # Construction of the Message object
        msg = Message(
            subject=subject,  # email subject
            recipients=["azkorotmg@gmail.com"],  # Website adresses (to)
            body=f"""
            Nouveau message reçu via le formulaire de contact :

            Nom : {name}
            E-mail : {email}
            Sujet : {subject}

            Message :
            {message}
            """
        )
        # Send email
        mail.send(msg)
        with conn.cursor() as cur:
            data = [(name, email, subject, message)]
            cur.executemany("INSERT INTO mail (name, mail, subject, message, date) VALUES (%s, %s, %s, %s, NOW())", data)
            conn.commit()
        return 200

    except Exception as e:
        newError(e, sendEmail.__name__, "Error during the construction of the mail", conn)
        return 400
    
def is_valid_email(email):
    # Server side check to see if the email is valid
    email_regex = r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
    return re.match(email_regex, email) is not None

def setAllItems(session, value, conn):
    # Set all the items to 'Active' or 'Inactive' depending of the value
    try:
        with conn.cursor() as cur:
            query = sql.SQL("UPDATE itemStates SET state = %s WHERE userid = %s")
            cur.execute(query, (value, session["user_id"]))
            conn.commit()
    except Exception as e:
        newError(e, setAllItems.__name__, "Error during the setting of all value to 0 or 1", conn)
        return(400)