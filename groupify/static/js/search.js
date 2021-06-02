// Vue app and comments based on given assignments in CSE183

// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        isEditing: 0,
        bio: "",
        // Index of album being edited, -1 means none selected
        page: -1,
        // Albums edited or not edited
        edited: false,
        // Save pending
        pending: false,
        // Text to show in pop-up
        message: "",
        // app's list of album covers
        coverList: [],
        // app's list of Spotify links
        urlList: [],
        // server's list of album covers
        serverCoverList: [],
        // server's list of Spotify links
        serverUrlList: [],
        // Search result titles
        topAlbums: [],
        // Search result artists
        topArtists: [],
        // Search result links
        trackLinks: [],
        // Search result artist links
        artistLinks: [],
        // Search result album covers
        imgList: [],
        // Number of results
        totalResults: 0,
    };
    
    // Uses user input as it is types to search Spotify
    app.searchSpotify = () => {
        // Get input from search bar
        input = document.getElementById('barInput');
        input = input.value;
        // Send to server
        axios.post(searchURL, {
            input: input,
        }).then((result) => {
            // Update all search result fields with server result
            app.vue.topAlbums = result.data.topAlbums;
            app.vue.topArtists = result.data.topArtists;
            app.vue.imgList = result.data.imgList;
            app.vue.trackLinks = result.data.trackLinks;
            app.vue.artistLinks = result.data.artistLinks;
            app.vue.totalResults = result.data.totalResults;
        }).catch(() => {
            console.log("Caught error");
        });
    };
    
    // Reloads the page, needed to update cover art
    app.refreshPage = () => {
        let temp = app.vue.page;
        app.vue.page = -1;
        app.vue.page = temp;  
    };
    
    // Adds an album to the banner
    app.addAlbum = (cover, url, i) =>{
        // If valid index of an album
        if (i >= 0 && i < 12) {
            // Update album data
            app.vue.coverList[i] = cover;
            app.vue.urlList[i] = url;
            // Update display
            app.refreshPage();
            // Update edite status
            app.vue.edited = true;
        }
        else {
            app.barAlert("Select a square for this album!");
        }
    };
    
    // Delete an album from the banner
    app.deleteAlbum = (i) => {
        // If invalid index, return
        if (i < 0 || i > 11)
            return;
        // If space is not empty, update to empty with "x"
        if (app.vue.coverList[i] != "x")
            app.vue.coverList[i] = "x";
        if (app.vue.urlList[i] != "x")
            app.vue.urlList[i] = "x";
        app.refreshPage();
        // Update edited status
        app.vue.edited = true;
    };
    
    // Save albums to server
    app.saveAlbums = () => {
        // If albums have been edited
        if(app.vue.edited){
            app.vue.pending = true; // Update pending status
            axios.post(squaresURL, {
                // Send lists to server
                coverList: app.vue.coverList,
                urlList: app.vue.urlList
            }).then((result) => {
                // Update lists with server data
                app.vue.coverList = result.data.coverList;
                app.vue.urlList = result.data.urlList;
                app.vue.serverCoverList = result.data.coverList;
                app.vue.serverUrlList = result.data.urlList;
                // End pending
                app.vue.pending = false;
                // Update edited, server now matches data
                app.vue.edited = false;
                app.barAlert("Albums Saved!");
            }).catch(() => {
                // If error, alert user
                console.log("Caught error");
                app.vue.pending = false;
                app.barAlert("Not Saved - Error");
            });
        }    
    };
    
    // Go to specific page (album index)
    app.goto = (pg) => {
        app.vue.page = pg;
    };
    
    // Take in a message and display with alert
    // Based on: https://www.w3schools.com/howto/howto_js_snackbar.asp
    app.barAlert = (msg) => {
        // Update message to be displayed
        app.vue.message = msg;
        
        // Get the snackbar DIV
        var bar = document.getElementById("snackbar");

        // Add the "show" class to DIV
        bar.className = "show";

        // After 3 seconds, remove the show class from DIV
        setTimeout(function(){ bar.className = bar.className.replace("show", ""); }, 3000);
    };
    
    // Send message confirming exit when albums are unsaved
    app.confirmExit = () => {
        // No message if saved
        if (app.vue.edited === false){
            window.location.replace(profileURL);
            return;
        }
        // Set message and show alert
        var msg = confirm("Your albums are not saved. Are you sure you want to exit?");
        if (msg === true) {
            window.location.replace(profileURL);
        }
        else {
            return;
        }  
    };
    
    // Update albums in app and set edited value
    app.rearrange = (covers, urls, edit) => {
        app.vue.coverList = covers;
        app.vue.urlList = urls;
        if (app.vue.edited === false){
            app.vue.edited = edit;
        }
    };
    
    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        goto: app.goto,
        searchSpotify: app.searchSpotify,
        refreshPage: app.refreshPage,
        addAlbum: app.addAlbum,
        deleteAlbum: app.deleteAlbum,
        saveAlbums: app.saveAlbums,
        barAlert: app.barAlert,
        confirmExit: app.confirmExit,
        rearrange: app.rearrange,
        
        // Drag and drop methods (outside app)
        drag: drag,
        drop: drop,
        allowDrop: allowDrop,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        axios.get(squaresURL).then((result) => {
            // Start with all lists as server version
            app.vue.coverList = result.data.coverList;
            app.vue.urlList = result.data.urlList;
            app.vue.serverCoverList = result.data.coverList;
            app.vue.serverUrlList = result.data.urlList;
        })
    };

    // Call to the initializer.
    app.init();
};


// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);

// Page and lists editable outside app
let tempPage = app.data.page;
let tempCovers = app.data.coverList;
let tempUrls = app.data.urlList;
// initial index of album being moved
let src = 0;
// index album is being moved to
let dest = 0;
// if dropping current element is allowed
let allowed = false;

// Drag and drop functions partially based on: https://www.w3schools.com/html/html5_draganddrop.asp

// Hovering over drop area
function allowDrop(ev) {
    // prevent default behavior
    ev.preventDefault();
    // id is the index of the album
    dest = ev.target.id;
}

// Dragging draggable element
function drag(ev) {
    // save state of albums and page
    allowed = true;
    tempCovers = app.data.coverList;
    tempUrls = app.data.urlList;
    tempPage = app.data.page;
    // save index
    src = ev.target.id;
}

// Execute drop
function drop(ev) {
    // prevent default behavior
    event.preventDefault();
    // if not allowed, reset and exit
    if(!allowed) {
        src = 0;
        dest = 0;
        allowed = false;
        return;
    }
    // update page based on where selected album moves
    if (src > tempPage && dest <= tempPage) {
        app.goto(parseInt(tempPage)+1);
    }
    else if (src < tempPage && dest >= tempPage) {
        app.goto(parseInt(tempPage)-1);
    }
    else if (src == tempPage) {
        app.goto(dest);
    }
    // reorder albums
    tempCovers.splice(dest, 0, tempCovers.splice(src, 1)[0]);
    tempUrls.splice(dest, 0, tempUrls.splice(src, 1)[0]);
    console.log(tempCovers);
    // send new order to app
    edit = (src != dest);
    app.rearrange(tempCovers, tempUrls, edit);
    allowed = false;
    src = 0;
    dest = 0;
}