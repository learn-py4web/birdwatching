"use strict";

// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


app.data = {    
    data: function() {
        return {
            sightings: [],
            user_email: null,
        };
    },
    methods: {
        // Complete as you see fit.
        my_function: function() {
            // This is an example.
        },
    }
};

app.vue = Vue.createApp(app.data).mount("#app");

app.load_data = function () {
    axios.get(get_sightings_url).then(function (r) {
        app.vue.sightings = r.data.sightings;
        app.vue.user_email = r.data.user_email;
    });
}

app.load_data();

