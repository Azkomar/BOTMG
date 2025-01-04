let srch = document.getElementById('itemSrch');
srch.addEventListener('keyup', function(event) {
    let rows = document.querySelectorAll('.rowDjn');
    let searchText = srch.value.toLowerCase();
    rows.forEach(function(row) {
        let detailRow = document.getElementById(row.dataset.name);
        if (row.dataset.name.toLowerCase().includes(searchText)) {
            row.style.display = '';
            detailRow.style.display = '';
        } else {
            row.style.display = 'none';
            detailRow.style.display = 'none';
        }
    });
});