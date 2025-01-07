function checkLogin() {
    // Get the values of the username and password fields
    var usernameField = document.querySelector("#username"); // Sélectionne l'input
    var passwordField = document.querySelector("#password");

    var username = usernameField.value; // Récupère la valeur actuelle
    var password = passwordField.value;

    // Create a FormData object and append the username and password
    var formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    // Send the request using fetch (AJAX)
    fetch('/login', {
        method: 'POST',
        body: formData // Data to send to the server
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json(); // Parse JSON if response is JSON
    })
    .then(data => {
        // Handle server response
        if (data.status === 200) {
            window.location.href = '/tableSearch';
        }
        else {
            // Réinitialiser les champs et afficher un message
            usernameField.value = '';
            passwordField.value = '';
            usernameField.focus();
            document.getElementById('error').innerHTML = 'Incorrect password or username !'
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function checkRegister() {
    const usernameField = document.querySelector("#username");
    const passwordField = document.querySelector("#password");
    const passwordRepField = document.querySelector("#passwordRep");

    const errorUsernameField = document.getElementById("errorUsername");
    const errorPasswordField = document.getElementById("errorPassword");
    const errorPasswordRepField = document.getElementById("errorPasswordRep");

    const fields = [
        { field: usernameField, message: "Please fill the username",  errorField: errorUsernameField},
        { field: passwordField, message: "Please fill the password", errorField: errorPasswordField },
        { field: passwordRepField, message: "Please confirm the password",  errorField: errorPasswordRepField}
    ];

    // Vérifier si des champs sont vides
    for (const { field, message, errorField } of fields) {
        if (!field.value.trim()) { // Vérifie si le champ est vide ou contient uniquement des espaces
            errorField.innerHTML = message;
            field.focus();
            return; // Stoppe la fonction si un champ est vide
        }
        else {
            errorField.innerHTML = '';
        }
    }

    // Vérifier que le pseudo ne contient pas de caractères spéciaux
    const username = usernameField.value;
    const usernameRegex = /^[a-zA-Z0-9-_]+$/; // Accepte uniquement lettres et chiffres
    if (!usernameRegex.test(username)) {
        errorUsernameField.innerHTML = 'Username can only contain letters and numbers.';
        usernameField.focus();
        return; // Stoppe la fonction si le pseudo est invalide
    }
    else {
        errorUsernameField.innerHTML = '';
    }

    // Vérifier la longueur du mot de passe
    const password = passwordField.value;
    const passwordRep = passwordRepField.value;

    if (password.length < 6) {
        errorPasswordField.innerHTML = 'Password must be at least 6 characters long';
        passwordField.focus();
        return; // Stoppe la fonction si la validation échoue
    }
    else {
        errorPasswordField.innerHTML = '';
    }

    // Vérifier si les mots de passe correspondent
    if (password !== passwordRep) {
        errorPasswordRepField.innerHTML = 'Passwords do not match';
        passwordRepField.focus();
        return; // Stoppe la fonction si la validation échoue
    }
    else {
        errorPasswordRepField.innerHTML = '';
    }

    // Si toutes les validations passent, préparer et envoyer les données
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    formData.append('passwordRep', passwordRep);

    fetch('/register', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Failed to register");
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 401) {
            errorUsernameField.innerHTML = 'Username is already taken';
            return;
        } else if (data.status != 200) {
            alert("An error Occured during registration")
            return;
        }
        window.location.href = "/login";  // Redirection correcte vers la page de connexion
    })
    .catch(error => {
        alert("An error occurred during registration");
    });
}