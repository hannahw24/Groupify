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
        //reorder: false,
        page: -1, // Index of album being edited, -1 means none selected
        edited: false, // Albums edited or not edited
        pending: false, // Save pending
        message: "", // Text to show in pop-up
        coverList: [], // app's list of album covers
        urlList: [], // app's list of Spotify links
        server_coverList: [], // server's list of album covers
        server_urlList: [], // server's list of Spotify links
        topAlbums: [], // Search result titles
        topArtists: [], // Search result artists
        trackLinks: [], // Search result links
        artistLinks: [], // Search result artist links
        imgList: [], // Search result album covers
        totalResults: 0, // Number of results
    };
    
    // Uses user input as it is types to search Spotify
    app.search_spotify = () => {
        
        input = document.getElementById('barInput'); // Get input from searcg bar
        input = input.value;
        console.log(input);
        // Send to server
        axios.post(search_url, {
            input: input,
        }).then((result) => {
            // Update all search result fields with server result
            app.vue.topAlbums = result.data.topAlbums;
            app.vue.topArtists = result.data.topArtists;
            app.vue.imgList = result.data.imgList;
            app.vue.trackLinks = result.data.trackLinks;
            app.vue.artistLinks = result.data.artistLinks;
            app.vue.totalResults = result.data.totalResults;
            console.log(result);
        }).catch(() => {
            console.log("Caught error");
        });
    };
    
    app.compare = () => {
        // Check each entry to see if edited
        // Currently unused
        let current = JSON.stringify(app.vue.coverList);
        let original = JSON.stringify(app.vue.server_coverList);
        if (current == original)
            app.vue.edited = false;
        else 
            app.vue.edited = true;
    };
    
    // Reloads the page, needed to update cover art
    app.refresh_page = () => {
        let temp = app.vue.page;
        app.vue.page = -1;
        app.vue.page = temp;  
    };
    
    /*app.setReorder = (val) => {
        app.vue.goto(-1);
        app.vue.reorder = val;
    }*/
    
    // Adds an album to the banner
    app.add_album = (cover, url, i) =>{
        // If valid index of an album
        if (i >= 0 && i < 12) {
            // Update album data
            app.vue.coverList[i] = cover;
            app.vue.urlList[i] = url;
            app.refresh_page(); // Update display
            app.vue.edited = true; // Update edite status
        }
        else {
            app.barAlert("Select a square for this album!");
        }
    };
    
    // Delete an album from the banner
    app.delete_album = (i) => {
        // If invalid index, return
        if (i < 0 || i > 11)
            return;
        // If space is not empty, update to empty with "x"
        if (app.vue.coverList[i] != "x")
            app.vue.coverList[i] = "x";
        if (app.vue.urlList[i] != "x")
            app.vue.urlList[i] = "x";
        app.refresh_page();
        app.vue.edited = true; // Update edited status
        console.log(app.vue.edited);
    };
    
    // Save albums to server
    app.save_albums = () => {
        // If albums have been edited
        if(app.vue.edited){
            app.vue.pending = true; // Update pending status
            axios.post(squares_url, {
                // Send lists to server
                coverList: app.vue.coverList,
                urlList: app.vue.urlList
            }).then((result) => {
                // Update lists with server data
                app.vue.coverList = result.data.coverList;
                app.vue.urlList = result.data.urlList;
                app.vue.server_coverList = result.data.coverList;
                app.vue.server_urlList = result.data.urlList;
                app.vue.pending = false; // End pending
                app.vue.edited = false; // Update edited, server now matches data
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
        /*if (app.vue.reorder){
            return;
        }*/
        //updateCursor()
        app.vue.page = pg;
        console.log(app.vue.page);
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
    
    app.confirmExit = () => {
        if (app.vue.edited === false){
            window.location.replace(profileURL);
            return;
        }
        var msg = confirm("Your albums are not saved. Are you sure you want to exit?");
        if (msg === true) {
            window.location.replace(profileURL);
        }
        else {
            return;
        }  
    };
    
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
        search_spotify: app.search_spotify,
        refresh_page: app.refresh_page,
        add_album: app.add_album,
        delete_album: app.delete_album,
        save_albums: app.save_albums,
        compare: app.compare,
        barAlert: app.barAlert,
        confirmExit: app.confirmExit,
        //setReorder: app.setReorder,
        rearrange: app.rearrange,
        
        // drag and drop methods (outside app)
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
        console.log("Begin");
        axios.get(squares_url).then((result) => {
            console.log(result);
            // Start with all lists as server version
            app.vue.coverList = result.data.coverList;
            app.vue.urlList = result.data.urlList;
            app.vue.server_coverList = result.data.coverList;
            app.vue.server_urlList = result.data.urlList;
        })
    };

    // Call to the initializer.
    app.init();
};


// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);

// page and lists editable outside app
let tempPage = app.data.page;
let tempCovers = app.data.coverList;
let tempUrls = app.data.urlList;
let src = 0; // initial index of album being moved
let dest = 0; // index album is being moved to
let allowed = false;

// drag and drop functions partially based on: https://www.w3schools.com/html/html5_draganddrop.asp

/*window.onload = function updateCursor() {
    if (!allowed) {
        for(i = 0; i < 12; i++) {
            document.getElementById(i).style.cursor = "move";
        }
    }
}*/

function allowDrop(ev) {
    ev.preventDefault(); // prevent default behavior
    dest = ev.target.id; // id is the index of the album
    //console.log("SRC: " + src);
    
    // cursor change, work in progress
    
    /*if(!allowed && src === -1) {
        for(i = 0; i < 12; i++) {
            document.getElementById(i).style.cursor = "no-drop";
        }
    }
    else {
        document.body.style.cursor = "auto";
    }*/
}

function drag(ev) {
    // save state of albums and page
    allowed = true;
    tempCovers = app.data.coverList;
    tempUrls = app.data.urlList;
    tempPage = app.data.page;
    console.log("PAGE: " + tempPage);
    // save index
    src = ev.target.id;
    // store data from id
    //ev.dataTransfer.setData("text", ev.target.id);
}

function drop(ev) {
    event.preventDefault(); // prevent default behavior
    console.log("INDEXES: " + src + ", " + dest);
    if(!allowed) {
        src = 0;
        dest = 0;
        allowed = false;
        document.body.style.cursor = "auto";
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
    document.body.style.cursor = "auto";
  //var data = ev.dataTransfer.getData("text");
  //ev.target.appendChild(document.getElementById(data));
}