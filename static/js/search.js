let srch = document.getElementById('itemSrch');
srch.addEventListener('keyup', function(event) {
    let btns = Array.from(document.querySelectorAll('.btnImg'));
    let btnsActive = Array.from(document.querySelectorAll('.btnImgActive'));
    let allBtns = btns.concat(btnsActive);
    
    let searchText = srch.value.toLowerCase();  // Texte de recherche, en minuscules pour comparaison
    // Parcourir tous les boutons
    allBtns.forEach(function(btn) {
        // Vérifier si le texte du bouton (name) contient le texte saisi
        if (btn.name.toLowerCase().includes(searchText)) {
            btn.style.display = '';  // Afficher le bouton
        } else {
            btn.style.display = 'none';  // Masquer le bouton
        }
    });
});