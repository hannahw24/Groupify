// Script for friend search bar
// based on https://www.w3schools.com/howto/howto_js_filter_lists.asp
function addfriendsearchBar() {
    // Set parameters
    var input, filter, ul, li, a, i, txtValue;
    input = document.getElementById('barInput_addfriend');
    filter = input.value.toUpperCase();
    ul = document.getElementById("listItems_addfriend");
    li = ul.getElementsByTagName('li');
  
    // Hide entries that don't match input
    for (i = 0; i < li.length; i++) {
      a = li[i].getElementsByTagName("a")[0];
      txtValue = a.textContent || a.innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        li[i].style.display = "";
      } else {
        li[i].style.display = "none";
      }
    }
    return false
  }