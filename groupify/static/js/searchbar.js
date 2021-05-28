// Script for playlists and albums
// based on https://www.w3schools.com/howto/howto_js_filter_lists.asp

/*
 * Groupify has three search bar files:
 *  - addfriend_searchbar.js
 *  - friendlist_searchbar.js
 *  - searchbar.js
 *
 * As well as search bar functions in some other files.
 *
 * This version identifies results with the "a" tag and handles
 * hiding multiline columns.
 *
 */
 
function searchBar() {
    // Set parameters
    var input, filter, ul, li, a, i, txtValue;
    // Searchbar input
    input = document.getElementById('barInput');
    // Filter with all uppercase
    filter = input.value.toUpperCase();
    // Total list items
    ul = document.getElementById("listItems");
    li = ul.getElementsByTagName('li');
    
    // Column will not always be defined
    // Used to hide multiline columns on the playlists page
    col = ul.getElementsByClassName('column is-4');

    // Hide entries that don't match input
    for (i = 0; i < li.length; i++) {
        // Get text value
        a = li[i].getElementsByTagName("a")[0];
        txtValue = a.textContent || a.innerText;
        // Hide if does not match input
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            li[i].style.display = "";
            // Check if col is defined and show
            if (typeof col[i] != "undefined"){
                col[i].style.display = "";
            }
        } else {
            li[i].style.display = "none";
            // Check if col is defined and hide
            if (typeof col[i] != "undefined"){
                col[i].style.display = "none";
            }
        }
    }
}