// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
      // The variable that determines how often an API call is made. 
      // UNSAFE: easily modified by an attacker to 0.
      hostAPICallTimer: 4,
      // Keeps track if it is time to make an API call.
      secondsPassedSinceCall: 0,
      // Keeps only the seconds of the timestamp in which the host updated the database entry.
      timeWhenDatabaseWasUpdated: 0,

      isPlaying: false,      
      isHost: false,

      // Keep track of whether or not the user has clicked the play/pause button. 
      preventButtonsFromBeingClicked: false,
      // Keep track of whether or not the visitor has clicked the synchronize button. 
      isSynchronizing: false,

      // Displays an error to the user.
      displayError: "",

      // Information about the song and the playback bar.
      playingTrackName: "",
      playingTrackArtist: "",
      playingTrackImage: "",
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

      displayNames: "",
      displayPictures: "",
    };
    
    // Function that retrieves the people in the group session from the database table. 
    app.getPeopleInSession = () => {
      axios.get(getPeopleInSession).then((result) => {
        app.data.displayNames = result.data.displayNames;
        app.data.displayPictures = result.data.profilePictures;
        console.log(result.data.redirect)
        if (result.data.redirect != false) {
          window.location = refreshGroupSession;
        }
        }).catch(() => {
          console.log("Error getting names and pictures");
        });
    }

    // Removes the logged in user from the group session table in the
    // database. Called when user leaves the group session window.
    app.removePeopleInSession = () => {
      axios.post(removePeopleInSession).then((result) => {
        }).catch(() => {
          console.log("Error removing people in session");
        });
    }

    // Function called by the host every interval of seconds determined by 'hostAPICallTimer'
    // In the backend (controllers.py), a Spotify API call is made to determine the song the host
    // is playing. The axios call then returns information about the song: 
    // (name, artist, length, position, image). This function then uses this information to 
    // display the appropriate names and times of the song. 
    app.getPlayingTrack = () => {
      axios.get(currentPlaying).then((result) => {
        console.log("In getPlayingTrack");
        app.data.isPlaying = result.data.isPlaying;

        app.data.playingTrackName = result.data.trackName;
        app.data.playingTrackArtist = result.data.artistName;
        app.data.playingTrackImage = result.data.imageURL;
        app.data.timeWhenDatabaseWasUpdated = result.data.timeWhenCallWasMade;
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
        }).then(() => {
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
      
      axios.post(search_url, {
        queueListImage: app.vue.queueListImage,
        queueListURL: app.vue.queueListURL,
      }).catch(() => {
        console.log("Caught error");
      });

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
 

    // Function that updates the user's position in a song outside of backend calls. 
    app.updateSongTimeEachSecond = () =>{
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
      // increments the position of the song by 1 second.
      app.data.currSeconds++;
      app.data.playingTrackPos++;
      // Above code might lead to 61 for a flash second
      if (app.data.currSeconds >= 60) {
        app.data.currMinutes++;
        app.data.currSeconds -= 60;
      }
      if (app.data.currSeconds < 10) {
        app.data.currSeconds = "0" + (app.data.currSeconds).toString();
      }
      app.data.songProgressBar = app.data.playingTrackPos/app.data.playingTrackLength * 100;      
  };

    // Adds a second to the timer holding how long it has been since an API call. 
    // Also determines if it is time to make a call (using hostAPICallTimer).
    app.increaseTimeSinceCall = () =>{
      // If it is the time to make an API call, do so. 
      if (app.data.secondsPassedSinceCall >= app.data.hostAPICallTimer) {
        try {
          app.getPlayingTrack();
          app.data.secondsPassedSinceCall = 0;
        }
        catch(err) {
          console.log("axios call failure in increaseTimeSinceCall");
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

    // Function that looks at the host's database table to display the song information 
    // (name, artist, length, position, image), and in the backend (controllers.py) makes
    // a call to the Spotify API to play the song at the specific time. 
    app.synchronizeVisitor = () => {
      // This axios call returns all the information about the song the host is playing.
      axios.get(synchronizeVisitor).then((result) => {
        app.data.preventButtonsFromBeingClicked = true;
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
        }).catch(() => {
          //This error occurs when the synchronizeVisitor URL has a userID but no deviceID.
          if ((synchronizeVisitor.toString()).slice(-1) == "/") {
            app.data.displayError = "Spotify Is Not Open"
            axios.get(getDevice).then((result) => {
              // adding the deviceID to the axios get URL.
              console.log("result.data.deviceID ", result.data.deviceID)
              synchronizeVisitor = synchronizeVisitor + result.data.deviceID;
            }).then(() => {
              app.data.preventButtonsFromBeingClicked = false;
              app.data.isSynchronizing = false;
              return
            });
          }
          console.log("error caught in synchronizeVisitor");
          app.data.isPlaying = "";
          app.data.playingTrackName = "None";
          app.data.playingTrackArtist = "None";
          app.data.playingTrackImage = "https://bulma.io/images/placeholders/128x128.png";
          app.data.currMinutes = NaN;
          app.data.currSeconds = NaN;  
          app.data.playingTrackLength = NaN;
          app.data.lengthMinutes = NaN;
          app.data.lengthSeconds = NaN;
          app.data.songProgressBar = 0;
        }).then(() => {
            app.data.preventButtonsFromBeingClicked = false;
            app.data.isSynchronizing = false;
            console.log("synchronizeVisitor Finished");
        });
    }

    // Determines whether the visitor should wait to synchronize. 
    app.synchronizeVisitorHandler = () => {
      axios.get(shouldSynchronizeVisitor).then((result) => {
        // Obtains the time of the last update the host made. 
        app.data.timeWhenDatabaseWasUpdated = result.data.timeWhenCallWasMade;
        // Gets the current time.
        var d = new Date();
        var n = d.getUTCSeconds();
        console.log("n = ", n);
        console.log("app.data.timeWhenDatabaseWasUpdated ", app.data.timeWhenDatabaseWasUpdated);
        console.log("seconds until next call is ", (app.data.timeWhenDatabaseWasUpdated + 5));
        // Determines when the next call by the host will be made by adding the set call timer
        // to it. Then takes the modulo to determine how many seconds are left until the next 
        // call is made. 
        var modulo = ((app.data.timeWhenDatabaseWasUpdated + (app.data.hostAPICallTimer + 1)) % n)
        console.log("modulo ", modulo);
        // Currently, if there is still 3.5 seconds until the host will make a call, then 
        // the visitor will synch immediately. 
        if (modulo >= 3.5) {
          // good time to synch
          console.log("good time to synch ", modulo);
          app.synchronizeVisitor();
        }
        // Else, the visitor will wait until the host has made a call, then immediately
        // synchronize. 
        else {
          // display a loading icon to the user informing them that they are going to synchronize.
          app.data.isSynchronizing = true;
          // wait for later
          console.log("wait for later");
          setTimeout(app.synchronizeVisitor, modulo*1000);
          return;
        }
      }).catch(() => {
        console.log("Error in synchronizeVisitorHandler");
        return;
      })
    }

    // Pauses or Unpauses a song
    // content: true is unpausing a song, false is pausing.
    app.playOrPause = (content) => {
      console.log("playOrPause");
      app.data.preventButtonsFromBeingClicked = true;
      // If the host has paused or played, it is a good time to update the song information in the
      // database.
      if (app.data.isHost) {
        // Will make a call, so reset the time since the last call.
        app.data.secondsPassedSinceCall = 0;
        app.getPlayingTrack();
      }
      // *controversial*: hitting the play button will synch the visitor with the host, rather
      // than play whatever song at whatever position the visitor is at. The latter causes
      // much more maintenance of the playback bar, which is why it is not implemented here. 
      else if (app.data.isHost == false && content == true) {
        app.synchronizeVisitor();
        return;
      }
      // This makes a call to the backend (controllers.py) which handles the Spotify API calls
      // to pause or unpause a song.
      axios.get(pauseOrPlayTrack, {params: {
        content: content
        }}).then((result) => {
              app.data.isPlaying = content;
              app.data.preventButtonsFromBeingClicked = false;
          }).catch(() => {
            // Checks to see if the problem is a missing deviceID, 
            // This can occur when a user does not have an instance of spotify when entering
            // the groupSession page. If they later open one, then this will get the deviceID
            // and make the playOrPause call once again. 
            if ((pauseOrPlayTrack.toString()).slice(-1) == "/") {
              app.data.displayError = "Spotify Is Not Open"
              axios.get(getDevice).then((result) => {
                // adding the deviceID to the axios get URL.
                console.log("result.data.deviceID ", result.data.deviceID)
                pauseOrPlayTrack = pauseOrPlayTrack + result.data.deviceID;
              }).then(() => {
                //app.playOrPause(content);
                app.data.preventButtonsFromBeingClicked = false;
              });
            }
            // This error occurs when the user has already paused the song in their
            // Spotify window, but then tries to pause on the groupSession page. 
            // The Spotify API returns an error when trying to pause a song that is 
            // already paused. 
            else {
              app.data.isPlaying = content;
              app.data.preventButtonsFromBeingClicked = false;
              return;
            }
          });
      };

    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
      getPlayingTrack: app.getPlayingTrack,
      search_spotify_songs: app.search_spotify_songs,
      add_song: app.add_song,
      increaseTimeSinceCall: app.increaseTimeSinceCall,
      synchronizeVisitor: app.synchronizeVisitor,
      playOrPause: app.playOrPause,
      synchronizeVisitorHandler: app.synchronizeVisitorHandler,
      removePeopleInSession: app.removePeopleInSession,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
      // Get people in the session.
      app.getPeopleInSession();
      // UNSAFE: easily modified by an attacker to be 1.
      // currently set to 15 seconds
      var g=setInterval(app.getPeopleInSession, 15000);

      // Makes a call to determine if the user is the host
      // UNSAFE: easily modified by an attacker to be true.
      axios.get(isGroupSessionHost).then((result) => {
          // If host, get song they are playing and set a timer to determine
          // when next call should be.  
          if (result.data.isHost == true) {
            app.data.isHost = true;
            app.getPlayingTrack();
            var t=setInterval(app.increaseTimeSinceCall, 1000);
          }
          // If visitor, synchronize with the host. 
          // *Potentially 5 seconds off*
          else {
            app.synchronizeVisitor();
            var t=setInterval(app.updateSongTimeEachSecond, 1000);
          }
      })
    };

    // Call to the initializer.
    app.init();

    // When a user leaves the groupSession, their profile will be 
    // removed from the display. 
    window.onbeforeunload = function() {
      app.removePeopleInSession();
    };

};


// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);