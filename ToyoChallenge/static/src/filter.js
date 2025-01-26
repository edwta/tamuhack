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


//Open a modal view with information about selected car
function modalSet(i) {
    var desc = "";
    list = document.getElementById(i);
    info = list.getElementsByTagName("li")
    for (x = 1; x < info.length; x++) {
        desc += info[x].textContent + "\n"; 
    }
    document.getElementById('carName').textContent = info[0].textContent;
    document.getElementById('carDesc').textContent = desc;
    //If comparing two cars, show second car's details with the first car
    if (document.getElementById("compare").style.visibility == "visible") {
        document.getElementById("compare").style.visibility = "hidden";
        document.getElementById('compName').style.display = "block";
        document.getElementById('compDesc').style.display = "block";
        document.getElementById('divider').style.display = "block";

    }
    document.getElementById('popup').showModal();
}

//If "Compare" selected, prepare information of car to compare with
function setComp() {
    document.getElementById("compare").style.visibility = "visible";
    document.getElementById("compareButton").style.display = "none";
    document.getElementById('compName').textContent = document.getElementById('carName').textContent;
    document.getElementById('compDesc').textContent = document.getElementById('carDesc').textContent;
}

//Reset comparison and return to status quo
function showComp() {
    document.getElementById('compName').textContent = "";
    document.getElementById('compDesc').textContent = "";
    document.getElementById('compName').style.display = "none";
    document.getElementById('compDesc').style.display = "none";
    document.getElementById('divider').style.display = "none";
    document.getElementById("compareButton").style.display = "block";
}

function addToCompare(vehicleId) {
  let compareList = JSON.parse(localStorage.getItem("compareList")) || [];
  
  if (!compareList.includes(vehicleId)) {
      compareList.push(vehicleId);
      alert("Vehicle added to comparison!");
  } else {
      alert("Vehicle is already in comparison list.");
  }
  
  localStorage.setItem("compareList", JSON.stringify(compareList));
}

function compareCar() {
  const carName = document.getElementById('carName').textContent;
  const carId = [...document.querySelectorAll('ul')]
      .find(ul => ul.querySelector('.title')?.textContent === carName)?.id.replace('info', '');

  if (!carId) return alert('Unable to add car to comparison.');

  let compareList = JSON.parse(localStorage.getItem('compareList')) || [];
  
  if (compareList.includes(carId)) {
      alert('Car is already in the comparison list.');
      return;
  }

  if (compareList.length >= 3) {
      alert('You can only compare up to 3 cars at a time.');
      return;
  }

  compareList.push(carId);
  localStorage.setItem('compareList', JSON.stringify(compareList));
  alert(`${carName} added to comparison list.`);
}

function clearCompareList() {
  localStorage.removeItem("compareList");
  alert("Comparison list cleared.");
}
