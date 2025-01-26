function search() {
  // Declare variables
  var input, filter, table, tr, td, i, txtValue;
  input = document.getElementById("search");
  filter = input.value.toUpperCase();
  table = document.getElementById("carTable");
  tr = table.getElementsByTagName("tr");

  // Loop through all table rows, and hide those who don't match the search query
  for (i = 0; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[0].getElementsByTagName("li")[0];
    if (td) {
      txtValue = td.textContent || td.innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    }
  }
}

function modalSet(i) {
    var desc = "";
    list = document.getElementById(i);
    info = list.getElementsByTagName("li")
    for (x = 1; x < info.length; x++) {
        desc += info[x].textContent + "\n"; 
    }
    document.getElementById('carName').textContent = info[0].textContent;
    document.getElementById('carDesc').textContent = desc;
    document.getElementById('popup').showModal();
}
