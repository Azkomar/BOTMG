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
        console.log(data)
        let details = document.getElementById(selectedItem);
        let nbrElement = document.getElementById('nbr' + selectedItem);
        nbrElement.innerHTML = '<span class="itmUsr">' + data.djnState[0][2] + '</span>' + " / " + '<span class="totalItm">' + data.djnState[0][1] + '</span>';

        if (active.has(selectedItem)) {
            details.innerHTML = '';  // Vide le contenu si l'élément est déjà actif
            active.delete(selectedItem);
        } else {
            let contentDetails = '<td class="djnDetails">';
            let len = data.liste.length;
            // Génère les boutons en fonction de la demande
            for (let i = 0; i < len; i++) {
                if (data.liste[i][2] == 1) {
                    contentDetails += `
                        <button type="button" 
                                class="btnImgActive" 
                                value="${data.liste[i][1]}" 
                                onclick="activateItem(this, event, ${taille})">
                            <img src="${data.liste[i][3]}" 
                                alt="${data.liste[i][0]}" 
                                width="55" height="55" 
                                id="itemImage${data.liste[i][1]}"
                                title="${data.liste[i][0]}" />
                        </button>
                    `;
                } else {
                    contentDetails += `
                        <button type="button" 
                                class="btnImg" 
                                value="${data.liste[i][1]}"  
                                onclick="activateItem(this, event, ${taille})">
                            <img src="${data.liste[i][3]}" 
                                alt="${data.liste[i][0]}" 
                                width="55" height="55" 
                                id="itemImage${data.liste[i][1]}"
                                title="${data.liste[i][0]}" />
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