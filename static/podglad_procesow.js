// function szukanieProcesu(status_procesu) {
//     // Declare variables
//     var input, filter, table, tr, a, i, txtValue;
//     input = document.getElementById('wyszukajPoces');
//     filter = input.value.toUpperCase();
//     table = document.getElementById("listaProcesow");
//     li = ul.getElementsByTagName('li');
  
//     // Loop through all list items, and hide those who don't match the search query
//     for (i = 0; i < li.length; i++) {
//       // a = li[i].getElementsByTagName("a")[0];
//       txtValue = li[i].textContent || li[i].innerText;
//       if (txtValue.toUpperCase().indexOf(filter) > -1) {
//         li[i].style.display = "";
//       } else {
//         li[i].style.display = "none";
//       }
//     }
//   }