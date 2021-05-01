// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        isEditingAlbums: 0,
        isEditingBio: 0,
        bio: "",
        originalBio: "",
        //To display in top songs dropdown
        termString: "",
        //1 is short term, 2 is medium term, 3 is long term
        currentTerm: 0,
        topTracks: [],
        topArtists: [],
        imgList: [],
        trackLinks: [],
        artistLinks: [],
    };
    
    //Used to save the album cover art for the user profiles. 
    app.save_bio = (content) => {
        console.log("I'm in save_bio");
        axios.post(userBio, null, {params: {
            content: content,
            }}).then((result) => {
                app.data.isEditingBio = 0;
                console.log("Received:", result.data);
                bio = content;
                app.data.bio = content;
                app.data.originalBio = content;
                //Goes to userProfile      
                //window.location.replace(profileURL);       
            }).catch(() => {
                console.log("Caught error");
                //Stays in the current window
            });
        };

    app.cancel_bio = () => {
        console.log("I'm in cancel_bio");
        app.data.bio = app.data.originalBio;
        app.data.isEditingBio = 0;
        //bio = app.data.originalBio;
        };

    app.controlEditButton = () => {
        editButton = document.getElementById('editButton');
        console.log(app.data.isEditingAlbums);
        if (app.data.isEditingAlbums === 0) {
            app.data.isEditingAlbums = 1;
        }
        else {
            app.data.isEditingAlbums = 0;
        }
    };

    app.seeTerm = () => {
        console.log("I'm in seeTerm");
        axios.get(getTopSongs).then((result) => {
            app.data.termString = result.data.term_str;
            app.data.topTracks = result.data.topTracks;
            app.data.topArtists = result.data.topArtists;
            app.data.imgList = result.data.imgList;
            app.data.trackLinks = result.data.trackLinks;
            app.data.artistLinks = result.data.artistLinks;
            }).then(() => {
                //show what the bio is.
                console.log(app.data.termString);
            });
        }
    
    app.changeTerm = (term) => {
        console.log("I'm in changeTerm");
        axios.post(getTopSongs, null, {params: {
            term: term,
            }}).then(() => {
                console.log("Term changed to :", term); 
                app.seeTerm(); 
            }).catch(() => {
                console.log("Caught error");
            });
        };


    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        controlEditButton: app.controlEditButton,
        save_bio: app.save_bio,
        cancel_bio: app.cancel_bio,
        seeTerm: app.seeTerm,
        changeTerm: app.changeTerm
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {

        axios.get(userBio).then((result) => {
            let bio = result.data.userBio;
            app.data.bio = bio;
            app.data.originalBio = bio;
            }).then(() => {
                //show what the bio is.
                console.log(app.data.bio);
                app.seeTerm();
            });

    };

    // Call to the initializer.
    app.init();
};


// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
