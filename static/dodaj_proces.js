function zmienPracownika() {
    const wybranyPracownik = document.getElementById('wybierzPracownika').value;
    const naglowek = document.getElementById('nrPracownika');
    if (wybranyPracownik !== "Wybierz") {
        naglowek.textContent = 'Pracownik Nr: ' + wybranyPracownik;
    } else {
        naglowek.textContent = 'Pracownik Nr: ';
    }
}

document.addEventListener("DOMContentLoaded", function() {
    const statusElements = document.querySelectorAll('.card-header-span');

    statusElements.forEach(element => {
        const statusText = element.textContent.trim().toLowerCase();

        if (statusText === 'zakonczone') {
            element.style.color = 'blue';
            // element.style = 'blue';
        } else if (statusText === 'w trakcie') {
            element.style.color = 'green';
        } else if (statusText === 'przerwane') {
            element.style.color = 'red';
        }
    });
});