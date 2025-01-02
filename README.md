# Bag of the Mad God
#### Video Demo:  <URL HERE>
#### Description:

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

### 4._.env_
    - This small file contains sensitive information such as the email password and the secret key mentioned earlier.

### 5._requirements.txt_
    - This file lists all the required packages to make the website function properly. (More details about the individual packages will follow.)

### 6._users.db_ and _bank.db_
    - These are the databases:
        - __users.db__ contains user data, item data, and an error log.
        - __bank.db__  is used to track the state of each item for each user, with values set to either 0 or 1. It also logs email-related data.
    > I made a significant mistake here. I should have used a single database to link all the information together. However, as I added more and more items, it became increasingly difficult to go back and restructure it properly. While this setup works fine for this project, it could lead to performance issues in larger projects.

### 7._static folder_
    - The __static__ folder contains the CSS stylesheet and font files, which are used across all the HTML pages.
    It also includes all the images used in the templates, as well as the JavaScript files that make the pages more dynamic.

### 8._templates folder_
    - The __templates__ folder conatins all the HTML pages which are rendered by the Flask app.

# What Are the Required Packages for It to Work?
In the __requirements.txt__ file, you can find all the packages that the website uses. Most of them are basic packages necessary for running a Flask server.
However, there are also some additional packages:
- __Werkzeug__: Used to hash passwords and verify if a password matches another by comparing their hash values.
- __uuid__: Used to generate random unique IDs for each user.
- __python-dotenv__: Allows sensitive values to be stored securely in an .env file and retrieved when needed.
- __Flask-Mail__: Used to send emails to specific addresses by configuring the email-sending process and building the email content.
- __Jinja2__: Used to embed Python variables within the HTML templates.

# Goal of this website
The goal of my project for this website is to deploy it online after completing the CS50 course. As I’ve already discussed it with members of the ROTMG (Realm of the Mad God) community, many of them are excited about the website. Even some content creators are eager to see it!
For a first website, I will be really proud if some members find it useful. :)
I also hope people will send me ideas to improve it and make it even better!