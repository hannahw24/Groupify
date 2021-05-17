  
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
        reorder: false,
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
    
    app.setReorder = (val) => {
        app.vue.goto(-1);
        app.vue.reorder = val;
    }
    
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
        if (app.vue.reorder){
            return;
        }
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
    
    app.rearrange = (covers, urls) => {
        app.vue.coverList = covers;
        app.vue.urlList = urls;
        app.vue.edited = true;
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
        setReorder: app.setReorder,
        rearrange: app.rearrange,
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

let tempIdx = -1;
let tempPage = app.data.page;
let tempCovers = app.data.coverList;
let tempUrls = app.data.urlList;
let dest = 0;

function allowDrop(ev) {
    ev.preventDefault();
    dest = ev.target.id;
}

function drag(ev) {
    tempCovers = app.data.coverList;
    tempUrls = app.data.urlList;
    tempPage = app.data.page;
    ev.dataTransfer.setData("text", ev.target.id);
    tempIdx = ev.target.id;
}

function drop(ev) {
    event.preventDefault();
    console.log("INDEXES: " + tempIdx + ", " + dest);
    if (tempIdx > tempPage && dest <= tempPage) {
        app.goto(tempPage+1);
    }
    else if (tempIdx < tempPage && dest >= tempPage) {
        app.goto(tempPage-1);
    }
    else if (tempIdx == tempPage) {
        app.goto(dest);
    }
    tempCovers.splice(dest, 0, tempCovers.splice(tempIdx, 1)[0]);
    tempUrls.splice(dest, 0, tempUrls.splice(tempIdx, 1)[0]);
    console.log(tempCovers);
    app.rearrange(tempCovers, tempUrls);
  //var data = ev.dataTransfer.getData("text");
  //ev.target.appendChild(document.getElementById(data));
}