import sqlite3
import re
import psycopg2
from psycopg2 import sql
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4
from operator import itemgetter
from flask_mail import Mail, Message


def get_db_connection():
    conn = psycopg2.connect(
        dbname="defaultdb",
        user="appuser",
        password="botmgcuties",
        host="bagofthemadgoddb-guillaume-f0ac.d.aivencloud.com",
        port="21708"
    )
    return conn

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

            # Création d'une nouvelle ligne
            newUserDB(id)

            # Valider la transaction (commit)
            conn.commit()
    
    except psycopg2.OperationalError as e:
        # Gérer les erreurs liées à la base de données
        newError(e, newUser.__name__, "Erreur avec SQL lors de la création d'un nouvel utilisateur", conn)
        return 400
    
    except Exception as e:
        # Gérer toute autre erreur
        newError(e, newUser.__name__, "Erreur inconnue lors de la création d'un nouvel utilisateur", conn)
        return 400
    
def newUserDB(id, conn):
    # Create a new line in the 'bank' database for the new user based on his ID
    """
    Return True if the line is created correctly
    Retrun False if an error occured
    """
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO itemUser (userId) VALUES (%s)", (id,))
            conn.commit()
            return True
    except sqlite3.OperationalError as e:
        newError(e, newUserDB.__name__, "Error with SQL during the creation of a new user database", conn)
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
    except sqlite3.OperationalError as e:
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
    except sqlite3.OperationalError as e:
        newError(e, getId.__name__, "Error with SQL when getting the user's id", conn)
        return 0
    except Exception as e:
        newError(e, getId.__name__, "Unknow error when getting the user's id", conn)
        return 0

def getListItems(conn):
    # Use to get the list of all the existing items
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM items")
            listItems = cur.fetchall()
            return listItems
    # If an error occured, return empty list
    except sqlite3.OperationalError as e:
        newError(e, getListItems.__name__, "Error with SQL when getting the list of all the items", conn)
        return []
    except Exception as e:
        newError(e, getListItems.__name__, "Unknow error when getting the list of all the items", conn)
        return []

def bigList(session, conn):
    """
    This function link the 2 database (bank and users) in a single list of dictionnary
    the dict contain all the items informations + the state of the items (if the user has it or not) 
    """
    try:
        with conn.cursor() as cur:
            listItems = getListItems(conn)
            # Get all the state of the the items for the actual user
            theList = []
            cur.execute("SELECT * FROM itemUser WHERE userId = %s", (session["user_id"], ))
            stateList = cur.fetchall()
            # Converting the list into tuple
            stateList[0] = ','.join(stateList[0])
            stateList = stateList[0].split(',')
            del(stateList[0])

            # loop throught the list of all the items
            for i in range(len(listItems)):
                # For each items we store the data into a new dictonnary
                dictItems = {}
                dictItems["name"] = listItems[i][0]
                dictItems["type"] = listItems[i][1]
                dictItems["ust"] = listItems[i][2]
                dictItems["dungeon"] = listItems[i][3]
                dictItems["id"] = listItems[i][4]
                dictItems["state"] = stateList[i]
                theList.append(dictItems)
            # Sort the list by name
            theList = sorted(theList, key=lambda dict: dict['name'])
            return(theList)
    # If an error occured, return empty list
    except Exception as e:
        newError(e, bigList.__name__, "Unknow error during the loading of the big list", conn)
        return []

def update(session, genre, conn):
    # Use to update the state of the items in the sort page
    allowed_genres = ["dungeon", "ust", "type"]  # Liste des noms de colonnes autorisés
    if genre not in allowed_genres:
        raise ValueError("Genre invalide")
    try:
        with conn.cursor() as cur:
            # Get a list order by the selected 'genre' (dungeon, type, ust)
            cur.execute(f"SELECT DISTINCT ({genre}), COUNT ({genre}), 0 FROM items GROUP BY ({genre}) ORDER BY ({genre})")
            listGenre = cur.fetchall()
            listItems = bigList(session, conn)
            listItems = sorted(listItems, key=itemgetter("dungeon"))

            # Convert listGenre in dictionnary for quick access
            genre_dict = {type[0]: (type[0], type[1], int(type[2])) for type in listGenre}

            # Update listGenre with genre_dict
            for item in listItems:
                if item['state'] == '1':
                    genre_key = item[genre]
                    if genre_key in genre_dict:
                        # Update the corresponding value
                        genre_dict[genre_key] = (genre_key, genre_dict[genre_key][1], genre_dict[genre_key][2] + 1)

            # Rebuild the list based on the dictionnary
            listGenre = list(genre_dict.values())
            return listGenre
    # If an error occured, return empty list
    except sqlite3.OperationalError as e:
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
            cur.execute("SELECT * FROM itemUser WHERE userId = %s", (session["user_id"],))
            listValue = cur.fetchall()
            listValue[0] = ','.join(listValue[0])
            listValue = listValue[0].split(',')
            del(listValue[0])
            for i in range(len(listValue)):
                if listValue[i-1] == '1':
                    result += 1
            return result
    except sqlite3.OperationalError as e:
        newError(e, countItm.__name__, "Error with SQL when counting all the active items", conn)
        return 0
    except Exception as e:
        newError(e, countItm.__name__, "Unknow error when counting all the active items", conn)
        return 0

def updateUserItem(session, itemId, conn) :
    # Update the state of a specific item by looking at his previous state
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT {itemId} FROM itemUser WHERE userId = %s", (session["user_id"],))
            itemState = cur.fetchone()
            if itemState[0] == '0':
                cur.execute(f"UPDATE itemUser SET {itemId} = 1 WHERE userId = %s", (session["user_id"],))
                state = 1
            else :
                cur.execute(f"UPDATE itemUser SET {itemId} = 0 WHERE userId = %s", (session["user_id"],))
                state = 0
            conn.commit()
            return state
    # If an error occured, return empty list
    except sqlite3.OperationalError as e:
        newError(e, updateUserItem.__name__, "Error with SQL when updating the state of a specific item", conn)
        return 0
    except Exception as e:
        newError(e, updateUserItem.__name__, "Unknow error when updating the state of a specific item", conn)
        return 0
def sortPage(type, listType, listItems):
    # Return the list corresponding to the selected 'object' in the selected 'genre'
    # Exemple : Return all the items of the 'dungeon' 'Void'
    
    # Loop throught 'listType' to get the total amount of items in this specific object
    for i in range(len(listType)):
            if (listType[i][0] == type):
                activeType = [listType[i][1], listType[i][2]]
    # Return a list of items matching the requirement (genre and object)
    responseList = []
    for i in range(len(listItems)):
        if (listItems[i]["ust"] == type) :
            responseList.append({"name": listItems[i]["name"], "state": listItems[i]["state"], "id": listItems[i]["id"]})
        elif (listItems[i]["dungeon"] == type) :
            responseList.append({"name": listItems[i]["name"], "state": listItems[i]["state"], "id": listItems[i]["id"]})
        elif (listItems[i]["type"] == type) :
            responseList.append({"name": listItems[i]["name"], "state": listItems[i]["state"], "id": listItems[i]["id"]})
    response = {
        "djnState": activeType,
        "liste": responseList
    }
    return response

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
            listItems = bigList(session, conn)
            size = len(listItems)
            for i in range(size):
                item = "item"+str(i+1)
                cur.execute(f"UPDATE itemUser SET {item} = %s WHERE userId = %s", (value, session["user_id"]))
            conn.commit()
    except Exception as e:
        newError(e, setAllItems.__name__, "Error during the setting of all value to 0 or 1", conn)
        return(400)