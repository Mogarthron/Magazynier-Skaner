var uwagiPracownikaModal = document.getElementById('uwagiPracownika');

  uwagiPracownikaModal.addEventListener('show.bs.modal', function (event) {

  var button = event.relatedTarget;

  var opis = button.getAttribute('data-bs-whatever');
 
  var username = opis.split("_")[0]
  var id_procesu = opis.split("_")[1]
 
  var modalTitle = uwagiPracownikaModal.querySelector('.modal-title');
  var modalBodyInput = uwagiPracownikaModal.querySelector('.modal-body input');

  modalTitle.textContent = username + ': UWAGI DO PROCESU NR: ' + id_procesu;
//   modalBodyInput.value = username;
  modalBodyInput.value = "ZAPISZ UWAGĘ";
    });