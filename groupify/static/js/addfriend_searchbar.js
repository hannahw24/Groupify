// Script for friend search bar
// based on https://www.w3schools.com/howto/howto_js_filter_lists.asp


// based on : https://stackoverflow.com/a/63104461
function checkKeyup() {
  document.getElementById('barInput').addEventListener("keyup", function(event) {
      // Number 13 is the "Enter" key on the keyboard
      if (event.keyCode === 13) {
        // Cancel the default action, if needed
        event.preventDefault();
        // Trigger the button element with a click
        searchBar();
        //document.getElementById("myBtn").click();
      }
    });
  }
  
  function searchBar() {
    // Set parameters
    var input, filter, ul, li, a, i, txtValue;
    input = document.getElementById('barInput');
    filter = input.value.toUpperCase();
    ul = document.getElementById("listItems");
    console.log(ul);
    li = ul.getElementsByTagName('li');
  
    // Hide entries that don't match input
    for (i = 0; i < li.length; i++) {
      fn = li[i].getElementsByClassName("friendname")[0];
      txtValue = fn.textContent || fn.innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        li[i].style.display = "";
      } else {
        li[i].style.display = "none";
      }
    }
  }