// Vue app and comments based on given assignments in CSE183

// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Artist data
        artistNames: [],
        artistImages: [],
        artistURLs: [],
        genres: [[]],
        followers: [],
        // Other parameters
        
        // Number of results
        resultsLen: 0,
        fullLen:0,
        // Set to true to update page
        filterReset: false,
        // Term of artists shown
        artistTerm: ""

    };
    
    // Gets artist term data from server
    app.seeArtistTerm = (term) => {
        axios.get(getTopArtists, {params: {
            term: term
            }}).then((result) => {
            app.data.artistNames = result.data.topArtists;
            app.data.artistTerm = result.data.termStr;
            app.data.artistImages = result.data.imgList;
            app.data.artistURLs = result.data.artistLinks;
            app.data.genres = result.data.genres;
            app.data.followers = result.data.followers;
            app.data.resultsLen = result.data.topArtists.length;
            app.data.fullLen = result.data.topArtists.length;
            app.data.genres = app.parseArray(app.data.genres);

            }).catch(() => {
                // Show what the bio is
                var emptyString = [];
                for (i = 0; i < 9; i++) {
                    emptyString.push("")
                }
                // Ensure data is not undefined
                app.data.artistNames = emptyString;
                app.data.artistImages = emptyString;
                app.data.artistURLs = emptyString;
                app.data.genres = emptyString;
                app.data.resultsLen = 0;
                app.data.fullLen = 0;
                // Empty to prevent "Followers" from appearing
                app.data.followers = [];
                console.log("Caught error in seeArtistTerm");
            });
        };
    
    // Called to change the term of artists (4 weeks, 6 months, all time)
    app.changeArtistTerm = (term, editable) => {
        // Call seeArtistTerm() to get data for new term
        if (editable == "True") {
            axios.post(getTopArtists, null, {params: {
                term: term
                }}).then(() => {
                    app.seeArtistTerm(); 
                }).catch(() => {
                    console.log("Caught error in changeArtistTerm");
                });
        }
        else {
            app.seeArtistTerm(term); 
        }
        // Clear filter on new results.
        input = document.getElementById('barInput');
        input.value = "";
    };
    
    // Parse genres from server
    app.parseArray = (genres) => {
        var returnList = [];
        // Separate genres in given string
        for (i = 0; i < genres.length; i++) {
            var tempString = "";
            var res = app.data.genres[i].split("'");
            res.splice(0, 1);
            res.splice(res.length-1, 1);
            // Add parsed results to return string
            for (j = 0; j < Math.min(res.length, 3); j++) {
                tempString += res[j];
            }
            returnList.push(tempString);
        }
        return returnList;
    };
    
    // Script for friend search bar
    // based on https://www.w3schools.com/howto/howto_js_filter_lists.asp
    app.searchBar = () => {
        // Set parameters
        var input, filter, ul, li, a, i, txtValue;
        var rLen = 0;
        // Search bar input
        input = document.getElementById('barInput');
        // Change to upper case
        filter = input.value.toUpperCase();
        ul = document.getElementById("listItems");
        li = ul.getElementsByTagName('li');

        // Hide entries that don't match input
        for (i = 0; i < li.length; i++) {
            a = li[i].getElementsByTagName("a")[0];
            txtValue = a.textContent || a.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                li[i].style.display = "";
                // Increment result total if not hidden
                rLen++;
            } else {
                li[i].style.display = "none";
            }
        }
        app.vue.resultsLen = rLen;
        // Quickly reset to update displayed page
        app.vue.filterReset = true;
        app.vue.filterReset = false;
    };
    

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        seeArtistTerm: app.seeArtistTerm,
        changeArtistTerm: app.changeArtistTerm,
        parseArray: app.parseArray,
        searchBar: app.searchBar,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        app.seeArtistTerm();
    };

    // Call to the initializer.
    app.init();
};


// This takes the (empty) app object, and initializes it.
init(app);