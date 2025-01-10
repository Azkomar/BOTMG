function setItem(val, size) {
    let listeBtn = []
    if (val == '1') {
        listeBtn = document.querySelectorAll('.btnImg');
        for (let i=0; i<listeBtn.length; i++) {
            listeBtn[i].classList.replace('btnImg', 'btnImgActive');
        }
        document.getElementById('progress').style.width = '100%';
        document.getElementById('progressText').innerText = size + " / " + size;
    } else if (val == '0') {
        listeBtn = document.querySelectorAll('.btnImgActive');
        for (let i=0; i<listeBtn.length; i++) {
            listeBtn[i].classList.replace('btnImgActive', 'btnImg');
        }
        document.getElementById('progress').style.width ='0%';
        document.getElementById('progressText').innerText = '0' + " / " + size;
    }
    var formData = new FormData();
    formData.append('setter', val);  // 'btnImg' est le nom du champ dans le formulaire
    // Envoyer la requête via fetch (AJAX)
    fetch('/itemSet', {
        method: 'POST',
        body: formData  // Les données à envoyer au serveur
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('An error occured : ' + response.status);
        }
    })  // Si la réponse est JSON
    .catch(error => {
        console.error('Erreur:', error);
    });   
}