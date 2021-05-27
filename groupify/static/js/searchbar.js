// Script for friend search bar
// based on https://www.w3schools.com/howto/howto_js_filter_lists.asp
function searchBar() {
  // Set parameters
  var input, filter, ul, li, a, i, txtValue;
  input = document.getElementById('barInput');
  filter = input.value.toUpperCase();
  ul = document.getElementById("listItems");
  console.log(ul);
  li = ul.getElementsByTagName('li');
  col = ul.getElementsByClassName('column is-4');

  // Hide entries that don't match input
  for (i = 0; i < li.length; i++) {
    a = li[i].getElementsByTagName("a")[0];
    txtValue = a.textContent || a.innerText;
    if (txtValue.toUpperCase().indexOf(filter) > -1) {
      li[i].style.display = "";
      if (typeof col[i] != "undefined"){
        col[i].style.display = "";
      }
    } else {
      li[i].style.display = "none";
      if (typeof col[i] != "undefined"){
        col[i].style.display = "none";
      }
    }
  }
}