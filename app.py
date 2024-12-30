from flask import Flask, render_template, request, redirect, session, jsonify
from flask_mail import Mail
from datetime import timedelta
import sqlite3
from functions import newUser, checkLogin, getId, newItemId, bigList, getListItems, update, countItm, updateUserItem, sortPage, sendEmail, is_valid_email, setAllItems

app = Flask(__name__)
app.config.from_object("config")
app.permanent_session_lifetime = timedelta(days=15)

# Initialisation de Flask-Mail
mail = Mail(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    
    username = request.form.get("username")
    password = request.form.get("password")
    status = newUser(username, password)

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
    status = checkLogin(username, password)
    if status == 200 :
        id = getId(username)
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

@app.route("/fillTable", methods=["GET", "POST"])
def fillTable():
    listItems = getListItems()
    if request.method == "GET":
        return render_template("fillTable.html", listItems=listItems)
    
    with sqlite3.connect("users.db") as con:
        cur = con.cursor()
        typeItem = request.form.get("type")
        ust = request.form.get("ust")
        name = request.form.get("name")
        dungeon = request.form.get("lootFrom")
        data =[(name, typeItem, ust, dungeon)]
        cur.executemany("INSERT INTO items (name, type, ust, dungeon) VALUES (?, ?, ?, ?)", data)
        data = [(name)]
        itemId = cur.execute("SELECT id FROM items WHERE name = ?", data)
        itemId = itemId.fetchall()
        itemId = itemId[0][0]
        newItemId(itemId)
        con.commit()
    
    return redirect("/fillTable")

@app.route("/tableSearch", methods=["GET", "POST"])
def tableSearch():
    if "user" in session: 
        listItems = bigList(session)
        if "size" not in session:
            size = len(listItems)
            session["size"] = size
        totalItem = countItm(session)
    else:
        return redirect("/login")
    
    if request.method == "GET":
        return render_template("tableSearch.html", listItems=listItems, size=session["size"], totalItem=totalItem, username=session["user"])
    elif request.method == "POST": 
        itemId = request.form.get('btnImg')
        status = updateUserItem(session, itemId)
        response = {
            "count": countItm(session),
            "status": status
        }
        return jsonify(response)

@app.route("/sort", methods=["GET", "POST"])
def sort():
    if "user" in session:
        listItems = bigList(session)
        if "size" not in session:
            size = len(listItems)
            session["size"] = size
        totalItem = countItm(session)
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
        listGenre = update(session, genre)
        session['genre'] = genre  # Stocker la variable dans la session
        return render_template("sort.html", listGenre=listGenre, size=session["size"], totalItem=totalItem, username=session["user"])
    
    elif request.method == "POST":
        req = request.form.get('djnSortBtn')
        listGenre = update(session, genre)
        response = sortPage(req, listGenre, listItems)
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
            status = sendEmail(name, email, subject, message, mail)
            response = {
                "status" : status
            }
        return jsonify(response)
    
@app.route("/itemSet", methods=["GET", "POST"])
def itemSet():
    if request.method == "POST":
        if request.form.get("setOne") is not None:
            setAllItems(session, '1')
        elif request.form.get("setZero") is not None:
            setAllItems(session, '0')
        return redirect("/tableSearch")
    return redirect("/tableSearch")

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)