// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
      playingTrackName: "",
      playingTrackArtist: "",
      playingTrackImage: "",
      playingTrackURI: "",
    };
    
    app.getPlayingTrack = () => {
      axios.get(currentPlaying).then((result) => {
        //include local variable checking later.
        app.data.playingTrackName = result.data.trackName;
        app.data.playingTrackArtist = result.data.artistName;
        app.data.playingTrackImage = result.data.imageURL;
        var spotifyTrackLinkPrefix = "https://open.spotify.com/embed/track/";
        app.data.playingTrackURI = spotifyTrackLinkPrefix.concat(result.data.trackURI);
        }).then(() => {
            //show what the bio is.
            console.log("getPlayingTrack Finished");
        });
    }



    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
      getPlayingTrack: app.getPlayingTrack,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
      var t=setInterval(app.getPlayingTrack, 1000);
    };

    // Call to the initializer.
    app.init();
};


// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);

