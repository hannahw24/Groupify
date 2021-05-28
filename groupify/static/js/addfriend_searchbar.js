// Script for search bar on add friend page
// based on https://www.w3schools.com/howto/howto_js_filter_lists.asp

/*
 * Groupify has three search bar files:
 *  - addfriend_searchbar.js
 *  - friendlist_searchbar.js
 *  - searchbar.js
 *
 * As well as search bar functions in some other files.
 *
 * This version of the searchbar uses a submit button and includes a
 * listener for the enter key.
 *
 */

// Checks for enter key
// based on : https://stackoverflow.com/a/63104461
function checkKeyup() {
    document.getElementById('barInput').addEventListener("keyup", function(event) {
        // Number 13 is the "Enter" key on the keyboard
        if (event.keyCode === 13) {
            // Cancel the default action, if needed
            event.preventDefault();
            // Trigger the button element with a click
            searchBar();
        }
    });
}

// Filters search
function searchBar() {
    // Set parameters
    var input, filter, ul, li, a, i, txtValue;
    // Store search input
    input = document.getElementById('barInput');
    // Change case
    filter = input.value.toUpperCase();
    ul = document.getElementById("listItems");
    li = ul.getElementsByTagName('li');

    // Hide entries that don't match input
    for (i = 0; i < li.length; i++) {
        // Identify friendname element
        fn = li[i].getElementsByClassName("friendname")[0];
        // Store text value of entry
        txtValue = fn.textContent || fn.innerText;
        // Hide if the entry does not match the input
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            li[i].style.display = "";
        } else {
            li[i].style.display = "none";
        }
    }
}