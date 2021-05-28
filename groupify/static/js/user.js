// Vue app and comments based on given assignments in CSE183

// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Editng status
        isEditingAlbums: 0,
        isEditingBio: 0,
        isEditingStatus: 0,
        // User bio
        bio: "",
        originalBio: "",
        // Active status
        active: "",
        originalActive: "",
        // To display in top songs dropdown
        termString: "",
        // 1 is short term, 2 is medium term, 3 is long term
        currentTerm: 0,
        // Track info
        topTracks: [],
        imgList: [],
        trackLinks: [],
        // Artist info
        topArtists: [],
        artistLinks: [],
        artistNames: [],
        artistImages: [],
        artistURLs: [],
        genres: [[]],
        followers: [],
        artistTerm: ""

    };
    
    //Used to save the album cover art for the user profiles. 
    app.save_bio = (content) => {
        // Send bio to server
        axios.post(userBio, null, {params: {
            content: content,
            }}).then((result) => {
                // Update editing status
                app.data.isEditingBio = 0;
                // Update app bio
                bio = content;
                app.data.bio = content;
                app.data.originalBio = content;
            }).catch(() => {
                console.log("Caught error");
            });
        };
    
    // User discards change to bio
    app.cancel_bio = () => {
        app.data.bio = app.data.originalBio;
        app.data.isEditingBio = 0;
        };
    
    // Get ative status from server
    app.getStat = () => {
        axios.get(userStat).then((result) => {
            let active = result.data.userStat;
            app.data.active = active;
            app.data.originalActive = active;
            }).then(() => {
            });
    }

    // Save active status
    app.save_stat = (content) => {
        // Send status to server
        axios.post(userStat, null, {params: {
            content: content,
            }}).then((result) => {
                // Update editing status
                app.data.isEditingStatus = 0;
                // Update status on app
                active = content;
                app.data.active = content;
                app.data.originalActive = content;      
            }).catch(() => {
                console.log("Caught error");
            });
        };
    
    // User discards change to active status
    app.cancel_stat = () => {
        app.data.active = app.data.originalActive;
        app.data.isEditingStatus = 0;
        };
    
    // Change state of edit button
    app.controlEditButton = () => {
        // Find edit button
        editButton = document.getElementById('editButton');
        // Set editing status
        if (app.data.isEditingAlbums === 0) {
            app.data.isEditingAlbums = 1;
        }
        else {
            app.data.isEditingAlbums = 0;
        }
    };

    // Called to see the top 10 songs
    app.seeTerm = (term) => {
        // Get term and tracks from server
        axios.get(getTopSongs, {params: {
            term: term
            }}).then((result) => {
            app.data.termString = result.data.term_str;
            app.data.topTracks = result.data.topTracks;
            app.data.topArtists = result.data.topArtists;
            app.data.imgList = result.data.imgList;
            app.data.trackLinks = result.data.trackLinks;
            app.data.artistLinks = result.data.artistLinks;
            }).then(() => {
            });
        }
    
    // Called to change the term of top 10 songs
    app.changeTerm = (term, editable) => {
        if (editable == "True") {
            axios.post(getTopSongs, null, {params: {
                term: term,
                }}).then(() => {
                    app.seeTerm(); 
                }).catch(() => {
                    console.log("Caught error");
                });
        }
        else {
            app.seeTerm(term);
        }
        };
    
    // Get artist term from server
    app.seeArtistTerm = (term) => {
        axios.get(getTopArtists, {params: {
            term: term
            }}).then((result) => {
            app.data.artistNames = result.data.topArtists;
            app.data.artistTerm = result.data.term_str;
            app.data.artistImages = result.data.imgList;
            app.data.artistURLs = result.data.artistLinks;
            app.data.genres = result.data.genres;
            app.data.followers = result.data.followers;

            app.data.genres = app.parseArray(app.data.genres);

            }).catch(() => {
                var emptyString = [];
                for (i = 0; i < 9; i++) {
                    emptyString.push("")
                }
                // Ensure items are not undefined
                app.data.artistNames = emptyString;
                app.data.artistImages = emptyString;
                app.data.artistURLs = emptyString;
                app.data.genres = emptyString;
                app.data.followers = [];
            });
        }
    
    //Called to change the term of top 10 songs
    app.changeArtistTerm = (term, editable) => {
        if (editable == "True") {
            axios.post(getTopArtists, null, {params: {
                term: term
                }}).then(() => {
                    app.seeArtistTerm(); 
                }).catch(() => {
                    console.log("Caught error");
                });
        }
        else {
            app.seeArtistTerm(term); 
        }
        };
    
    // Parse genres array
    app.parseArray = (genres) => {
        var returnList = [];
        for (i = 0; i < genres.length; i++) {
            // Parse genres from given string, push to new string, return
            var tempString = "";
            var res = app.data.genres[i].split("'");
            res.splice(0, 1);
            res.splice(res.length-1, 1);
            for (j = 0; j < Math.min(res.length, 3); j++) {
                tempString += res[j];
            }
            returnList.push(tempString);
        }
        return returnList;
    }


    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        controlEditButton: app.controlEditButton,
        save_bio: app.save_bio,
        cancel_bio: app.cancel_bio,
        save_stat: app.save_stat,
        cancel_stat: app.cancel_stat,
        seeTerm: app.seeTerm,
        changeTerm: app.changeTerm,
        seeArtistTerm: app.seeArtistTerm,
        changeArtistTerm: app.changeArtistTerm,
        parseArray: app.parseArray
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
                // After setting the Bio move on to displaying top songs
                // and user playlists
                app.seeTerm();
                app.seeArtistTerm();
                app.getStat();
            });
    };

    // Call to the initializer.
    app.init();
};


// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);