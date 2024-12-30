import sqlite3
import re
from werkzeug.security import generate_password_hash, check_password_hash
from uuid import uuid4
from operator import itemgetter
from flask_mail import Mail, Message

def newError(error, func, message):
    # Function used to log error into a database
    """
    The parameters are :
        error -> It's the name of the error
        func -> It's the name of the function where the error appeared
        message -> The message link to the error
    """
    try:
        with sqlite3.connect("users.db") as con:
            print(error, func, message)
            cur = con.cursor()
            cur.execute("INSERT INTO errorLog (errorName, date, function, message) VALUES (?, datetime('now'), ?, ?)", (str(error), str(func), str(message)))
            con.commit()
    except Exception as e:
        print("An error occured during the error logging...")

def newUser(username, password):
    # Function used to create a new user if the parameters are valid
    try:
        # Connexion to the database 'users.db'
        with sqlite3.connect("users.db") as con:
            # Create a pointer "cur" in this DB
            cur = con.cursor()
            # Check if the username is already taken
            cur.execute("SELECT 1 FROM users WHERE username = ?", (username,))
            # If cur.execute returns nothing, the username is available; otherwise, return an error
            if cur.fetchone() is not None:
                return 401
            # Secure the password using a hashing function
            hashPass = generate_password_hash(password)
            # Generate a unique random ID
            id = str(uuid4())
            # Create a new entry in the "bank.db" database for the new user
            if newUserDB(id) is False:
                raise Exception("Erreur lors de la création dans bank.db")
            # Add the user's information to the 'data' tuple for insertion into the DB
            data = [(username, hashPass, id)]
            cur.executemany("INSERT INTO users (username, hash, id) VALUES (?, ?, ?)",data)
            con.commit()
        return 200
    # Check if there's an error with the sql insertion
    except sqlite3.OperationalError as e:
        newError(e, newUser.__name__, "Error with SQL during the creation of a new user")
        return 400
    # Check if there's another error
    except Exception as e:
        newError(e, newUser.__name__, "Unknown error during the creation of a new user")
        return 400

def newUserDB(id):
    # Create a new line in the 'bank' database for the new user based on his ID
    """
    Return True if the line is created correctly
    Retrun False if an error occured
    """
    try:
        with sqlite3.connect("bank.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO itemUser (userId) VALUES (?)", (id,))
            con.commit()
            return True
    except sqlite3.OperationalError as e:
        newError(e, newUserDB.__name__, "Error with SQL during the creation of a new user database")
        return False

def checkLogin(username, password):
    # Check if the login information match the database
    username = tuple([username])
    try:
        with sqlite3.connect("users.db") as con:
            cur = con.cursor()
            # Check if username exist in the database
            cur.execute("SELECT username FROM users WHERE username = ?", username)
            if cur.fetchone() is not None:
                # If username exist, check if the password hashing correspond
                hashPass = cur.execute("SELECT hash FROM users WHERE username = ?", username)
                hashPass = hashPass.fetchall()
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
        newError(e, checkLogin.__name__, "Error with SQL during the connexion of a user")
        return 400
    except Exception as e:
        newError(e, checkLogin.__name__, "Unknow error during the connexion of a user")
        return 400
        

def getId(username):
    # Get an id corresponding to the username
    try:
        with sqlite3.connect("users.db") as con:
            cur = con.cursor()
            id = cur.execute("SELECT id FROM users WHERE username = ?", (username,))
            id = id.fetchall()
            return id[0][0]
    # If an error occured, return 0 value
    except sqlite3.OperationalError as e:
        newError(e, getId.__name__, "Error with SQL when getting the user's id")
        return 0
    except Exception as e:
        newError(e, getId.__name__, "Unknow error when getting the user's id")
        return 0

def getListItems():
    # Use to get the list of all the existing items
    try:
        with sqlite3.connect("users.db") as con:
            cur = con.cursor()
            listItems = cur.execute("SELECT * FROM items")
            listItems = listItems.fetchall()
            return listItems
    # If an error occured, return empty list
    except sqlite3.OperationalError as e:
        newError(e, getListItems.__name__, "Error with SQL when getting the list of all the items")
        return []
    except Exception as e:
        newError(e, getListItems.__name__, "Unknow error when getting the list of all the items")
        return []

def bigList(session):
    """
    This function link the 2 database (bank and users) in a single list of dictionnary
    the dict contain all the items informations + the state of the items (if the user has it or not) 
    """
    try:
        with sqlite3.connect("bank.db") as con:
            cur = con.cursor()
            listItems = getListItems()

            # Get all the state of the the items for the actual user
            theList = []
            stateList = cur.execute("SELECT * FROM itemUser WHERE userId = ?", (session["user_id"], ))
            stateList = stateList.fetchall()

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
            return(theList)
    # If an error occured, return empty list
    except Exception as e:
        newError(e, bigList.__name__, "Unknow error during the loading of the big list")
        return []

def update(session, genre):
    # Use to update the state of the items in the sort page
    try:
        with sqlite3.connect("users.db") as con:
            cur = con.cursor()
            # Get a list order by the selected 'genre' (dungeon, type, ust)
            listGenre = cur.execute(f"SELECT DISTINCT({genre}), COUNT({genre}), 0 FROM items GROUP BY {genre} ORDER BY {genre}")
            listGenre = listGenre.fetchall()
            listItems = bigList(session)
            listItems = sorted(listItems, key=itemgetter("dungeon"))
            # Look for the 'active' items
            for item in listItems:
                if item['state'] == '1':
                    # If there's one, check for the corresponding 'genre' and update it
                    for i, type in enumerate(listGenre):
                        if type[0] == item[genre]:  
                            listGenre[i] = (type[0], type[1], int(type[2]) + 1)

            return listGenre
    # If an error occured, return empty list
    except sqlite3.OperationalError as e:
        newError(e, update.__name__, "Error with SQL when updating the states of a list of items")
        return []
    except Exception as e:
        newError(e, update.__name__, "Unknow error when updating the states of a list of items")
        return []
    
def countItm(session):
    # Refresh the progress bar with the current number of items by looking for the total number of 'active' items
    listItems = bigList(session)
    count = 0
    for i in listItems:
        if i['state'] == "1":
            count += 1
    return count

def updateUserItem(session, itemId) :
    # Update the state of a specific item by looking at his previous state
    try:
        with sqlite3.connect("bank.db") as con:
            cur = con.cursor()
            itemState = cur.execute(f"SELECT {itemId} FROM itemUser WHERE userId = ?", (session["user_id"],)).fetchone()
            if itemState[0] == '0':
                cur.execute(f"UPDATE itemUser SET {itemId} = 1 WHERE userId = ?", (session["user_id"],))
                state = 1
            else :
                cur.execute(f"UPDATE itemUser SET {itemId} = 0 WHERE userId = ?", (session["user_id"],))
                state = 0
            con.commit()
            return state
    # If an error occured, return empty list
    except sqlite3.OperationalError as e:
        newError(e, updateUserItem.__name__, "Error with SQL when updating the state of a specific item")
        return 0
    except Exception as e:
        newError(e, updateUserItem.__name__, "Unknow error when updating the state of a specific item")
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

def sendEmail(name, email, subject, message, mail):
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
        with sqlite3.connect("bank.db") as con:
            cur = con.cursor()
            data = [(name, email, subject, message)]
            cur.executemany("INSERT INTO mail (name, mail, subject, message, date) VALUES (?, ?, ?, ?, DATETIME('now'))", data)
            con.commit()
        return 200

    except Exception as e:
        newError(e, sendEmail.__name__, "Error during the construction of the mail")
        return 400
    
def is_valid_email(email):
    # Server side check to see if the email is valid
    email_regex = r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?"
    return re.match(email_regex, email) is not None

def setAllItems(session, value):
    # Set all the items to 'Active' or 'Inactive' depending of the value
    try:
        with sqlite3.connect("bank.db") as con:
            listItems = bigList(session)
            size = len(listItems)
            cur = con.cursor()
            for i in range(size+1):
                item = "item"+str(i+1)
                # Error in the DB, there's no item103
                if item != 'item103':
                    cur.execute(f"UPDATE itemUser SET {item} = ? WHERE userId = ?", (value, session["user_id"]))
            con.commit()
    except Exception as e:
        newError(e, setAllItems.__name__, "Error during the setting of all value to 0 or 1")
        return(400)
    
def newItemId(itemId) :
    with sqlite3.connect("bank.db") as con:
        cur = con.cursor()
        # Concatenation du mot 'item' + id de l'item pour la création d'une nouvelle colone
        itemId = "item" + str(itemId)
        # Ajout de la nouvelle colonne avec le nom itemX ou x est un entier correspondant a l'id d'un item
        cur.execute(f"ALTER TABLE itemUser ADD COLUMN {itemId} TEXT NOT NULL DEFAULT '0'")
        con.commit()