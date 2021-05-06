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
        page: -1,
        edited: false,
        pending: false,
        message: "",
        coverList: [],
        urlList: [],
        server_coverList: [],
        server_urlList: [],
        topAlbums: [],
        topArtists: [],
        trackLinks: [],
        artistLinks: [],
        imgList: [],
        totalResults: 0,
        serverCoverList: [],
        serverUrlList: []
    };
    /*
    app.index = (a) => {
        let i = 0;
        for (let c of a) {
            c._idx = i++;
            console.log(c._idx);
        }
        return a;
    };
    
    
    //Used to save the album cover art for the user profiles. 
    app.save_album = (track, cover, squareNumber) => {
        //console.log("I'm in save_album");
        axios.post(inputAlbum, null, {params: {
            squareNumber: squareNumber,
            cover: cover,
            albumURL: track,
            }}).then((result) => {
                console.log("Received:", result.data);   
                //Goes to userProfile      
                //window.location.replace(inputAlbum);
                window.location.reload();
            }).catch(() => {
                console.log("Caught error");
                //Stays in the current window
            });
        };
    */
    
    app.search_spotify = () => {
        
        input = document.getElementById('barInput');
        input = input.value;
        console.log(input);
        axios.post(search_url, {
            input: input,
        }).then((result) => {
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
        let current = JSON.stringify(app.vue.coverList);
        let original = JSON.stringify(app.vue.server_coverList);
        if (current == original)
            app.vue.edited = false;
        else 
            app.vue.edited = true;
    };
    
    app.refresh_page = () => {
        let temp = app.vue.page;
        app.vue.page = -1;
        app.vue.page = temp;  
    };
    
    app.add_album = (cover, url, i) =>{
        app.vue.coverList[i] = cover;
        app.vue.urlList[i] = url;
        app.refresh_page();
        app.vue.edited = true;
    };
    
    app.delete_album = (i) => {
        if (app.vue.coverList[i] != "x")
            app.vue.coverList[i] = "x";
        if (app.vue.urlList[i] != "x")
            app.vue.urlList[i] = "x";
        app.refresh_page();
        app.vue.edited = true;
        console.log(app.vue.edited);
    };
    
    app.save_albums = () => {
        if(app.vue.edited){
            app.vue.pending = true;
            axios.post(squares_url, {
                coverList: app.vue.coverList,
                urlList: app.vue.urlList
            }).then((result) => {
                app.vue.coverList = result.data.coverList;
                app.vue.urlList = result.data.urlList;
                app.vue.server_coverList = result.data.coverList;
                app.vue.server_urlList = result.data.urlList;
                app.vue.pending = false;
                app.vue.edited = false;
                app.vue.message = "Albums Saved!";
                app.barAlert();
            }).catch(() => {
                // If error, keep editing
                console.log("Caught error");
                app.vue.pending = false;
                app.vue.message = "Not Saved - Error";
                app.errorAlert();
            });
        }    
    };
    
    app.controlEditButton = () => {
        editButton = document.getElementById('editButton');
        console.log(app.data.isEditing);
        if (app.data.isEditing === 0) {
            app.data.isEditing = 1;
        }
        else {
            app.data.isEditing = 0;
        }
    };
    
    app.goto = (pg) => {
        app.vue.page = pg;
        console.log(app.vue.page);
    };
    
    app.barAlert = () => {
        // Get the snackbar DIV
        var bar = document.getElementById("snackbar");

        // Add the "show" class to DIV
        bar.className = "show";

        // After 3 seconds, remove the show class from DIV
        setTimeout(function(){ bar.className = bar.className.replace("show", ""); }, 3000);
    };
    
    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        controlEditButton: app.controlEditButton,
        //save_album: app.save_album,
        goto: app.goto,
        search_spotify: app.search_spotify,
        refresh_page: app.refresh_page,
        add_album: app.add_album,
        delete_album: app.delete_album,
        save_albums: app.save_albums,
        compare: app.compare,
        barAlert: app.barAlert,
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
            app.vue.coverList = result.data.coverList;
            app.vue.urlList = result.data.urlList;
            app.vue.server_coverList = result.data.coverList;
            app.vue.server_urlList = result.data.urlList;
            //console.log(app.vue.coverList);
        })
    };

    // Call to the initializer.
    app.init();
};


// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);