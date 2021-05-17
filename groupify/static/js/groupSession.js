// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
      // The variable that determines how often an API call is made. 
      apiCallTimer: 5,
      // Keeps track if it is time to make an API call.
      secondsPassedSinceCall: 0,

      isPlaying: false,      

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
        app.data.isPlaying = result.data.isPlaying;

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

        app.data.songProgressBar = app.data.playingTrackPos/app.data.playingTrackLength * 100;
        console.log("songProgressBar in getPlayingTrack() is ", app.data.songProgressBar);
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
    app.addSong = (cover, url) =>{
        // If valid index of a song
        // if (i >= 0 && i < 12) {
        //     // Update album data
        //     app.vue.queueListImage[i] = cover;
        //     app.vue.queueListURL[i] = url;
        // }
        app.vue.queueListImage[i] = cover;
        app.vue.queueListURL[i] = url;
    };

    app.updateSongTimeEachSecond = () =>{
      if (app.data.isPlaying == false) {
        return;
      }
      app.data.currSeconds = parseInt(app.data.currSeconds);
      app.data.currSeconds++;
      app.data.playingTrackPos++;
      if (app.data.currSeconds >= 60) {
        app.data.currMinutes++;
        app.data.currSeconds -= 60;
      }

      app.data.songProgressBar = app.data.playingTrackPos/app.data.playingTrackLength * 100;
      console.log("songProgressBar in updateSongTimeEachSecond() is ", app.data.songProgressBar);

      if (app.data.currSeconds < 10) {
        app.data.currSeconds = "0" + (app.data.currSeconds).toString();
      }

      if (app.data.playingTrackPos >= app.data.playingTrackLength) {
        app.synchronizeVisitor();
      }
  };

    app.increaseTime = () =>{
      // If it is the time to make an API call, do so. 
      if (app.data.secondsPassedSinceCall == app.data.apiCallTimer) {
        try {
          app.getPlayingTrack();
          app.data.secondsPassedSinceCall = 0;
        }
        catch(err) {
          console.log("axios call failure");
          app.data.secondsPassedSinceCall = 0;
        }
      }
      // If it is not time to make an API call for the song the host 
      // is listening to, then increase the time passed since the last
      // call. 
      else {
        app.data.secondsPassedSinceCall++;
        app.updateSongTimeEachSecond();
      }
    }

    app.synchronizeVisitor = () => {
      axios.get(synchronizeVisitor).then((result) => {
        //include local variable checking later.
        app.data.isPlaying = result.data.isPlaying;
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
        app.data.songProgressBar = app.data.playingTrackPos/app.data.playingTrackLength * 100;
        //var t=setInterval(app.synchronizeVisitor, 1000);
        }).then(() => {
            console.log("synchronizeVisitor Finished");
        });
    }

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
      getPlayingTrack: app.getPlayingTrack,
      search_spotify_songs: app.search_spotify_songs,
      addSong: app.addSong,
      increaseTime: app.increaseTime,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
      axios.get(isGroupSessionHost).then((result) => {
          if (result.data.isHost == true) {
            console.log("isHost");
            //immediately get the song a user is playing. 
            app.getPlayingTrack();
            var t=setInterval(app.increaseTime, 1000);
          }
          else {
            console.log("is not Host");
            app.synchronizeVisitor();
            var t=setInterval(app.updateSongTimeEachSecond, 1000);
          }
      }).then(() => {
          console.log("hey");
      });
    };

    // Call to the initializer.
    app.init();
};


// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);