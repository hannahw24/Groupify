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
      //playingTrackURI: "",
      playingTrackPos: "",
      playingTrackLength: "",
      songProgressBar: "",
      currMinutes: "",
      currSeconds: "",
      lengthMinutes: "",
      lengthSeconds: "",
      topTracks: "", 
      topArtists: "",
      imgList: "",
      artistLinks: "",
      totalResults: "",
      totalResults: 0, // Number of results
      queueListImage: [], //list of songs in queue; picture
      queueListURL: [], //list of songs in queue; link
    };
    
    app.getPlayingTrack = () => {
      axios.get(currentPlaying).then((result) => {
        //include local variable checking later.
        app.data.playingTrackName = result.data.trackName;
        app.data.playingTrackArtist = result.data.artistName;
        app.data.playingTrackImage = result.data.imageURL;

        app.data.playingTrackPos = result.data.curPosition;
        app.data.playingTrackPos = parseInt(app.data.playingTrackPos);
        app.data.playingTrackPos = app.data.playingTrackPos/1000;
        app.data.currMinutes = Math.floor(app.data.playingTrackPos / 60);
        app.data.currSeconds = Math.floor(app.data.playingTrackPos - app.data.currMinutes * 60);
        if (app.data.currSeconds < 10) {
          app.data.currSeconds = "0" + (app.data.currSeconds).toString();
        }

        app.data.playingTrackLength = result.data.trackLength;
        app.data.playingTrackLength = parseInt(app.data.playingTrackLength);
        app.data.playingTrackLength = app.data.playingTrackLength/1000;
        app.data.lengthMinutes = Math.floor(app.data.playingTrackLength / 60);
        app.data.lengthSeconds = Math.floor(app.data.playingTrackLength - app.data.lengthMinutes * 60);
        if (app.data.lengthSeconds < 10) {
          app.data.lengthSeconds = "0" + (app.data.lengthSeconds).toString();
        }
        //console.log(app.data.lengthSeconds);

        app.data.songProgressBar = app.data.playingTrackPos/app.data.playingTrackLength * 100;

        //var spotifyTrackLinkPrefix = "https://open.spotify.com/embed/track/";
        //app.data.playingTrackURI = spotifyTrackLinkPrefix.concat(result.data.trackURI);
        }).then(() => {
            //console.log("getPlayingTrack Finished");
        });
    }

    app.search_spotify_songs = () => {
        
      input2 = document.getElementById('songSearch'); // Get input from searcg bar
      input2 = input2.value;
      console.log(input2);
      // Send to server
      axios.post(search_url, {
          input2: input2,
      }).then((result) => {
          // Update all search result fields with server result
          app.vue.topTracks = result.data.topTracks;
          app.vue.topArtists = result.data.topArtists;
          app.vue.imgList = result.data.imgList;
          app.vue.trackLinks = result.data.trackLinks;
          app.vue.artistLinks = result.data.artistLinks;
          app.vue.totalResults = result.data.totalResults;
          console.log(result2);
      }).catch(() => {
          console.log("Caught error");
      });
  };

    // Adds an album to the banner
    app.add_song = (cover, url) =>{
        // If valid index of a song
        // if (i >= 0 && i < 12) {
        //     // Update album data
        //     app.vue.queueListImage[i] = cover;
        //     app.vue.queueListURL[i] = url;
        // }
        app.vue.queueListImage[i] = cover;
        app.vue.queueListURL[i] = url;
    };

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
      getPlayingTrack: app.getPlayingTrack,
      search_spotify_songs: app.search_spotify_songs,
      add_song: app.add_song,
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