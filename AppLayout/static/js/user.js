// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        isEditing: 0
    };

    app.index = (a) => {
        return a;
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
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // TODO: Load the posts from the server instead.
        // We set the posts.
        
        //posts_url is from previos HW must chage
        axios.get(posts_url).then((result) => {
            app.vue.posts = app.index("filler");
            }).then(() => {
                console.log("Begin");
            });
    };

    // Call to the initializer.
    app.init();
};


// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
