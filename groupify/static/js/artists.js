// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        artistNames: [],
        artistImages: [],
        artistURLs: [],
        genres: [[]],
        followers: [],
        resultsLen: 0,
        filterReset: false,
        fullLen:0,
        artistTerm: ""

    };
    
    app.seeArtistTerm = (term) => {
        console.log("I'm in seeArtistTerm");
        axios.get(getTopArtists, {params: {
            term: term
            }}).then((result) => {
            app.data.artistNames = result.data.topArtists;
            app.data.artistTerm = result.data.term_str;
            app.data.artistImages = result.data.imgList;
            app.data.artistURLs = result.data.artistLinks;
            app.data.genres = result.data.genres;
            app.data.followers = result.data.followers;
            console.log("Followers", app.data.followers)
            app.data.resultsLen = result.data.topArtists.length;
            app.data.fullLen = result.data.topArtists.length;
            app.data.genres = app.parseArray(app.data.genres);

            }).catch(() => {
                //show what the bio is.
                console.log("Error in seeArtistTerm")
                var emptyString = [];
                for (i = 0; i < 9; i++) {
                    emptyString.push("")
                }
                app.data.artistNames = emptyString;
                app.data.artistImages = emptyString;
                app.data.artistURLs = emptyString;
                app.data.genres = emptyString;
                app.data.resultsLen = 0;
                app.data.fullLen = 0;
                //empty to prevent "Followers" from appearing
                app.data.followers = [];
            });
        };
    
    //Called to change the term of top 10 songs
    app.changeArtistTerm = (term, editable) => {
        console.log("I'm in changeArtistTerm");
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
        input = document.getElementById('barInput');
        input.value = "";
    };

    app.parseArray = (genres) => {
        var returnList = [];
        for (i = 0; i < genres.length; i++) {
            var tempString = "";
            console.log(genres[i]);
            var res = app.data.genres[i].split("'");
            res.splice(0, 1);
            res.splice(res.length-1, 1);
            console.log("res", res);
            for (j = 0; j < Math.min(res.length, 3); j++) {
                tempString += res[j];
            }
            console.log("tempString", tempString);
            returnList.push(tempString);
        }
        console.log("returnList", returnList);
        return returnList;
    };
    
    // Script for friend search bar
    // based on https://www.w3schools.com/howto/howto_js_filter_lists.asp
    app.searchBar = () => {
        // Set parameters
        var input, filter, ul, li, a, i, txtValue;
        var rLen = 0;
        input = document.getElementById('barInput');
        filter = input.value.toUpperCase();
        ul = document.getElementById("listItems");
        console.log(ul);
        li = ul.getElementsByTagName('li');

        // Hide entries that don't match input
        for (i = 0; i < li.length; i++) {
            a = li[i].getElementsByTagName("a")[0];
            txtValue = a.textContent || a.innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                li[i].style.display = "";
                rLen++;
            } else {
                li[i].style.display = "none";
            }
        }
        app.vue.resultsLen = rLen;
        app.vue.filterReset = true;
        app.vue.filterReset = false;
        console.log(app.vue.resultsLen);
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


// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
