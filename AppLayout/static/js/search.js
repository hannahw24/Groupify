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
    };

    app.index = (a) => {
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
    
    // We form the dictionary of all methods, so we can assign them
    // to the Vue app in a single blow.
    app.methods = {
        controlEditButton: app.controlEditButton,
        save_album: app.save_album
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
    };

    // Call to the initializer.
    app.init();
};


// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
