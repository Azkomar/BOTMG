export function initPage(totalItem, size) {
    let percent = (totalItem / size) * 100;
    document.getElementById('progress').style.width = percent + '%';
}

// Appeler la fonction automatiquement lorsque le DOM est complètement chargé
document.addEventListener('DOMContentLoaded', function() {
    initPage(totalItem, size);
});