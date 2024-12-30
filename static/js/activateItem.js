function activateItem(button, event, itemMax) {
    // Aide de chatGPT
    // Empêche le comportement par défaut du bouton (soumission de formulaire)
    event.preventDefault();

    // Récupérer la valeur de l'élément sélectionné
    var selectedItem = button.value;

    // Créer un objet FormData pour envoyer la donnée du bouton
    var formData = new FormData();
    formData.append('btnImg', selectedItem);  // 'btnImg' est le nom du champ dans le formulaire
    // Envoyer la requête via fetch (AJAX)
    fetch('/tableSearch', {
        method: 'POST',
        body: formData  // Les données à envoyer au serveur
    })
    .then(response => response.json())  // Si la réponse est JSON
    .then(data => {
        let size = parseInt(itemMax);
        let totalItem = data.count;
        let percent = (totalItem / size) * 100;
        document.getElementById('progress').style.width = percent + '%';
        document.getElementById('progressText').innerText = totalItem + " / " + size;
        if (data.status == 1) {
            button.classList.replace('btnImg', 'btnImgActive');
        }
        else {
            button.classList.replace('btnImgActive', 'btnImg');;
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
    });
}