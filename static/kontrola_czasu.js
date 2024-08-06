var uwagiPracownikaModal = document.getElementById('uwagiPracownika');

uwagiPracownikaModal.addEventListener('show.bs.modal', function (event) {

  var button = event.relatedTarget;

  var opis = button.getAttribute('data-bs-whatever');

  var username = opis.split("_")[0]
  var id_procesu = opis.split("_")[1]

  var modalTitle = uwagiPracownikaModal.querySelector('.modal-title');
  var modalBodyInput = uwagiPracownikaModal.querySelector('.modal-body input');

  var zapisz_uwage = document.getElementById("zapiszUwage")

  modalTitle.textContent = username + ': UWAGI DO PROCESU NR: ' + id_procesu;
  zapisz_uwage.name = "zapiszUwagiDoProcesu_" + id_procesu;
  modalBodyInput.value = "ZAPISZ UWAGĘ";
});


function szukanieProcesu() {
  // Declare variables
  var input, filter, ul, li, a, i, txtValue;
  input = document.getElementById('wyszukajPoces');
  filter = input.value.toUpperCase();
  ul = document.getElementById("listaProcesow");
  li = ul.getElementsByTagName('li');

  // Loop through all list items, and hide those who don't match the search query
  for (i = 0; i < li.length; i++) {
    // a = li[i].getElementsByTagName("a")[0];
    txtValue = li[i].textContent || li[i].innerText;
    if (txtValue.toUpperCase().indexOf(filter) > -1) {
      li[i].style.display = "";
    } else {
      li[i].style.display = "none";
    }
  }
}