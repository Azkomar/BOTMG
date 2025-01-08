from flask import Flask, render_template, request, redirect, session, jsonify
from flask_mail import Mail
from datetime import timedelta
from functions import newUser, checkLogin, getId, update, countItm, updateUserItem, sortPage, sendEmail, is_valid_email, setAllItems, getListItems
import psycopg2
import os
from dotenv import find_dotenv, load_dotenv

# find .env automatically
dotenvPath = find_dotenv()
# load up the entries as environment variables
load_dotenv(dotenvPath)

app = Flask(__name__)
app.config.from_object("config")
app.permanent_session_lifetime = timedelta(days=15)

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

# Initialisation de Flask-Mail
mail = Mail(app)

conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    
    username = request.form.get("username")
    password = request.form.get("password")
    status = newUser(username, password, conn)

    response = {
        "status": status
    }
    return jsonify(response)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if "user" in session:
            return redirect("/tableSearch")
        return render_template("login.html")
    
    username = request.form.get("username")
    password = request.form.get("password")
    status = checkLogin(username, password, conn)
    if status == 200 :
        id = getId(username, conn)
        if id != 0:
            session["user_id"] = id
            session["user"] = username
            session.permanent = True
        else:
            status = 400
    response = {
        "status": status
    }
    return jsonify(response)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

##############################################################
""" Need verification """

@app.route("/tableSearch", methods=["GET", "POST"])
def tableSearch():
    if "user" in session: 
        listItems = getListItems(session, conn)
        if "size" not in session:
            size = len(listItems)
            session["size"] = size
        totalItem = countItm(session, conn)
    else:
        return redirect("/login")
    
    if request.method == "GET":
        return render_template("tableSearch.html", listItems=listItems, size=session["size"], totalItem=totalItem, username=session["user"])
    elif request.method == "POST": 
        itemId = request.form.get('btnImg')
        status = updateUserItem(session, itemId, conn)
        response = {
            "count": countItm(session, conn),
            "status": status
        }
        return jsonify(response)

@app.route("/sort", methods=["GET", "POST"])
def sort():
    if "user" in session:
        listItems = getListItems(session, conn)
        if "size" not in session:
            size = len(listItems, conn)
            session["size"] = size
        totalItem = countItm(session, conn)
    else:
        return redirect("/login")
    # Vérifier si une variable est déjà stockée dans la session
    if 'genre' in session:
        genre = session['genre']
    else:
        genre = None  # Par défaut, genre est None si non défini

    # Si la méthode est GET, on récupère le genre depuis les paramètres de l'URL
    if request.method == 'GET':
        genre = request.args.get('navBtn', genre)  # Utiliser l'argument de l'URL ou la valeur stockée
        if genre not in ("dungeon", "ust", "type"):
            return redirect("/tableSearch")
        listGenre = update(session, genre, conn)
        session['genre'] = genre  # Stocker la variable dans la session
        return render_template("sort.html", listGenre=listGenre, size=session["size"], totalItem=totalItem, username=session["user"])
    
    elif request.method == "POST":
        req = request.form.get('djnSortBtn')
        response = sortPage(req, session, conn)
        return jsonify(response)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if "user" not in session:
        return redirect("/login")
    if request.method == "GET":
        return render_template("contact.html", username=session["user"])
    if request.method == 'POST':
        # Récupérer les données du formulaire
        name = request.form['name']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']

        validSubject = ("idea", "bug", "question")

        if not name or not email or not subject or not message:
            response = {
                "status" : 400
            }
        elif subject not in validSubject:
            response = {
                "status" : 400
            }
        elif not is_valid_email(email):
            response = {
                "status" : 400
            }
        else:
            status = sendEmail(name, email, subject, message, mail, conn)
            response = {
                "status" : status
            }
        return jsonify(response)
    
@app.route("/itemSet", methods=["GET", "POST"])
def itemSet():
    if request.method == "POST":
        if request.form.get("setOne") is not None:
            setAllItems(session, '1', conn)
        elif request.form.get("setZero") is not None:
            setAllItems(session, '0', conn)
        return redirect("/tableSearch")
    return redirect("/tableSearch")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)