function showItm(button, event, taille) {
    event.preventDefault();
    let selectedItem = button.value;
    let formData = new FormData();
    formData.append('djnSortBtn', selectedItem);
    // Envoyer la requête via fetch (AJAX)
    fetch('/sort', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())  // Si la réponse est JSON
    .then(data => {
        let details = document.getElementById(selectedItem);
        let nbrElement = document.getElementById('nbr' + selectedItem);
        nbrElement.innerHTML = '<span class="itmUsr">' + data.djnState[1] + '</span>' + " / " + '<span class="totalItm">' + data.djnState[0] + '</span>';

        if (active.has(selectedItem)) {
            details.innerHTML = '';  // Vide le contenu si l'élément est déjà actif
            active.delete(selectedItem);
        } else {
            let contentDetails = '<td class="djnDetails">';
            let len = data.liste.length;
            // Génère les boutons en fonction de la demande
            for (let i = 0; i < len; i++) {
                if (data.liste[i]["state"] == 1) {
                    contentDetails += `
                        <button type="button" 
                                class="btnImgActive" 
                                value="item${data.liste[i]["id"]}" 
                                onclick="activateItem(this, event, ${taille})">
                            <img src="./static/img/itemImg/${data.liste[i]["name"]}.png" 
                                alt="${data.liste[i]["name"]}" 
                                width="55" height="55" 
                                id="itemImage${data.liste[i]["id"]}"
                                title="${data.liste[i]["name"]}" />
                        </button>
                    `;
                } else {
                    contentDetails += `
                        <button type="button" 
                                class="btnImg" 
                                value="item${data.liste[i]["id"]}"  
                                onclick="activateItem(this, event, ${taille})">
                            <img src="./static/img/itemImg/${data.liste[i]["name"]}.png" 
                                alt="${data.liste[i]["name"]}" 
                                width="55" height="55" 
                                id="itemImage${data.liste[i]["id"]}"
                                title="${data.liste[i]["name"]}" />
                        </button>
                    `;
                }
            }
            contentDetails += '</td>';
            details.innerHTML = contentDetails;  // Mettre à jour le contenu
            button.scrollIntoView({
                behavior: 'smooth',
                block: 'start',
                inline: 'nearest',
            });
            active.set(selectedItem, selectedItem);  // Ajouter à la Map
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
    });
}