# Bag of the Mad God
#### Video Demo:  <URL HERE>

# Brief Explaination
This project is related to the video game "Realm of the Mad God."
It’s a website that functions somewhat like an application, and its purpose is to help you keep track of the loot you acquire in the game.

# How does it work ?
To get started, simply visit the corresponding URL and sign up!
The registration process is simple and does not require an email address.

Once you’re registered, you’ll see a grid displaying all the rare items in the game.
To add items to your account, simply click on the item you want, and it will be added to your collection.

On this page, there are two extra buttons that allow you to __activate__ or __deactivate__ all the items.
Additionally, there are buttons to sort the page using different parameters. For example, you can click on _Dungeon_ to sort the items by the location they come from. You also have a _Type_ option and a _UST_ option for different sorting methods.

At the top of the window, a progress bar indicates the number of items you’ve collected.

To wrap up this section, there’s a link to the wiki (accessible by clicking on the eye icon at the top) and a contact form (accessible by clicking on _Contact_) if you have any questions or ideas.

# What Do the Files Do?
### 1._app.py_
    - __app.py__ is where the routes are defined. It works alongside the functions in functions.py.
    All the POST and GET requests are set up here, and there are also verifications to check if the user is logged in.
    To prevent unauthorized access to specific routes, redirections are implemented as necessary.
    Many of the routes return a _jsonify_ object to make the pages more dynamic.
### 2._functions.py_
    - __functions.py__ contains all the abstract functions that we prefer to keep out of the app file.
    Most of these functions are used to communicate with the database, either to display items or to modify values related to the user.

### 3._config.py_
    - __config.py__ contains all the setup parameters needed to ensure everything works smoothly.
    It includes all the data required to configure _Flask-Mail_ for automatically sending emails to registered addresses.
    It also loads the _SecretKey_ necessary for signing session cookies.

### 4._requirements.txt_
    - This file lists all the required packages to make the website function properly. (More details about the individual packages will follow.)

### 5._static folder_
    - The __static__ folder contains the CSS stylesheet and font files, which are used across all the HTML pages.
    It also includes all the images used in the templates, as well as the JavaScript files that make the pages more dynamic.

### 6._templates folder_
    - The __templates__ folder conatins all the HTML pages which are rendered by the Flask app.

# What Are the Required Packages for It to Work?
In the __requirements.txt__ file, you can find all the packages that the website uses. Most of them are basic packages necessary for running a Flask server.
However, there are also some additional packages:
- __Werkzeug__: Used to hash passwords and verify if a password matches another by comparing their hash values.
- __uuid__: Used to generate random unique IDs for each user.
- __python-dotenv__: Allows sensitive values to be stored securely in an .env file and retrieved when needed.
- __Flask-Mail__: Used to send emails to specific addresses by configuring the email-sending process and building the email content.
- __Jinja2__: Used to embed Python variables within the HTML templates.
- __psycopg2__: Used to connect to the Postgres database

# Goal of this website
The goal of this website is simply to create something I would love to have in the game: a collection log !
I hope you enjoy this amateur website! :)