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
      isHost: false,

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
      message: "", // Text to show in pop-up
      page: -1,
    };
    
    app.getPlayingTrack = () => {
      axios.get(currentPlaying).then((result) => {
        console.log("In getPlayingTrack");
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

        //var spotifyTrackLinkPrefix = "https://open.spotify.com/embed/track/";
        //app.data.playingTrackURI = spotifyTrackLinkPrefix.concat(result.data.trackURI);
        }).then(() => {
            //console.log("getPlayingTrack Finished");
        });
    }

    app.search_spotify_songs = () => {
        
      input2 = document.getElementById('songSearch'); // Get input from searcg bar
      input2 = input2.value;
      //console.log(input2);
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
          //console.log(result2);
      }).catch(() => {
          console.log("Caught error");
      });
  };

    // Adds an album to the banner
    app.add_song = (cover, url) =>{
        let i=0;
       for(i = 0; i<10; i++){
         if(app.vue.queueListImage[i] == null){
           app.vue.queueListImage[i] = cover;
           app.vue.queueListURL[i] = url;
           app.refresh_page(); // Update display
           app.barAlert("Added to list!");
           break;
         }
         app.refresh_page(); // Update display
       }
       if(i>=10){
         app.barAlert("Only 10 songs queued at once!");
       }
      //maybe add a post????
      //Do basically this:
      // Send to server
      // axios.post(search_url, {
      //   input2: input2,
      // }).then((result) => {
      //     // Update all search result fields with server result
      //     app.vue.topTracks = result.data.topTracks;
      //     app.vue.topArtists = result.data.topArtists;
      //     app.vue.imgList = result.data.imgList;
      //     app.vue.trackLinks = result.data.trackLinks;
      //     app.vue.artistLinks = result.data.artistLinks;
      //     app.vue.totalResults = result.data.totalResults;
      //     //console.log(result2);
      // }).catch(() => {
      //     console.log("Caught error");
      // });
      
      //In controller: add if post line which then adds to database
    };

    // Take in a message and display with alert
   // Based on: https://www.w3schools.com/howto/howto_js_snackbar.asp
    app.barAlert = (msg) => {
    // Update message to be displayed
      app.vue.message = msg;
    
      // Get the snackbar DIV
      var bar = document.getElementById("snackbar");

      //clear the search input and all the resulting searches
      document.getElementById("songSearch").value = null;
      axios.post(search_url, {
        input2: input2,
      }).then((result) => {
          // Update all search result fields with null values so nothing pops up
          app.vue.topTracks = null;
          app.vue.topArtists = null;
          app.vue.imgList = null;
          app.vue.trackLinks = null;
          app.vue.artistLinks = null;
          app.vue.totalResults = null;
          //console.log(result2);
      }).catch(() => {
          console.log("Caught error");
      });

      // Add the "show" class to DIV
      bar.className = "show";

      // After 3 seconds, remove the show class from DIV
      setTimeout(function(){ bar.className = bar.className.replace("show", ""); }, 3000);
    };

    app.refresh_page = () => {
      let temp = app.vue.page;
      app.vue.page = -1;
      app.vue.page = temp; 
    };
 


    app.updateSongTimeEachSecond = () =>{
      console.log("isPlaying ", app.data.isPlaying);
      if (app.data.isPlaying == false) {
        return;
      }
      // If the host is done with a song, sync their next song. 
      if (app.data.isHost) {
        if ((app.data.playingTrackPos >= app.data.playingTrackLength)) {
          app.getPlayingTrack();
          // Just made a call, so no need to update less than 5 seconds from now
          app.data.secondsPassedSinceCall = 0;
        }
      }
      // If user is not host and the track has finished, sync the next song. 
      else if (app.data.playingTrackPos >= app.data.playingTrackLength) {
        app.synchronizeVisitor();
      }
      app.data.currSeconds = parseInt(app.data.currSeconds);
      // Might lead to 61 for a flash second
      app.data.currSeconds++;
      app.data.playingTrackPos++;
      if (app.data.currSeconds >= 60) {
        app.data.currMinutes++;
        app.data.currSeconds -= 60;
      }
      if (app.data.currSeconds < 10) {
        app.data.currSeconds = "0" + (app.data.currSeconds).toString();
      }

      app.data.songProgressBar = app.data.playingTrackPos/app.data.playingTrackLength * 100;
      console.log("songProgressBar in updateSongTimeEachSecond() is ", app.data.songProgressBar);
      
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

    // Takes in whether or not to play or pause a track. 
    // true is playing, false is paused.
    app.playOrPause = (content) => {
      console.log("playOrPause");
      axios.get(pauseOrPlayTrack, {params: {
        content: content
        }}).then((result) => {
              app.data.isPlaying = content;
              //app.getPlayingTrack();
          }).catch(() => {
              console.log("Caught error");
          });
      };

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
      getPlayingTrack: app.getPlayingTrack,
      search_spotify_songs: app.search_spotify_songs,
      add_song: app.add_song,
      increaseTime: app.increaseTime,
      synchronizeVisitor: app.synchronizeVisitor,
      playOrPause: app.playOrPause,
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
            app.data.isHost = true;
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