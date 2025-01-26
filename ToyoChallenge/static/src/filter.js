function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

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
      console.log(filter);
      console.log(txtValue.toUpperCase());
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
    if (document.getElementById("compare").style.visibility == "visible") {
        document.getElementById("compare").style.visibility = "hidden";
        document.getElementById('compName').style.display = "block";
        document.getElementById('compDesc').style.display = "block";
        document.getElementById('divider').style.display = "block";

    }
    document.getElementById('popup').showModal();
}

function setComp() {
    document.getElementById("compare").style.visibility = "visible";
    document.getElementById("compareButton").style.display = "none";
    document.getElementById('compName').textContent = document.getElementById('carName').textContent;
    document.getElementById('compDesc').textContent = document.getElementById('carDesc').textContent;
}

function showComp() {
    document.getElementById('compName').textContent = "";
    document.getElementById('compDesc').textContent = "";
    document.getElementById('compName').style.display = "none";
    document.getElementById('compDesc').style.display = "none";
    document.getElementById('divider').style.display = "none";
    document.getElementById("compareButton").style.display = "block";
}