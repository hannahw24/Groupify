// Script for friend list panel search bar
// based on https://www.w3schools.com/howto/howto_js_filter_lists.asp

/*
 * Groupify has three search bar files:
 *  - addfriend_searchbar.js
 *  - friendlist_searchbar.js
 *  - searchbar.js
 *
 * As well as search bar functions in some other files.
 *
 * This version identifies input with the "friendname" id.
 *
 */

function searchBar() {
  // Set parameters
  var input, filter, ul, li, a, i, txtValue;
  // Searchbar input
  input = document.getElementById('barInput');
  // Filter with all upper case
  filter = input.value.toUpperCase();
  ul = document.getElementById("listItems");
  li = ul.getElementsByTagName('li');

  // Hide entries that don't match input
  for (i = 0; i < li.length; i++) {
      // Get results with friendname id
      fn = li[i].getElementsByClassName("friendname")[0];
      txtValue = fn.textContent || fn.innerText;
      // Hide if does not match input
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
          li[i].style.display = "";
      } else {
          li[i].style.display = "none";
      }
  }
}