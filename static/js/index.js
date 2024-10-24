"use strict";

// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


app.data = {    
    data: function() {
        return {
            sightings: [],
            user_email: null,
            new_species: "",
        };
    },
    methods: {
        // Complete as you see fit.
        inc: function (s_idx, q) {
            let sighting = this.sightings[s_idx];
            let new_qty = sighting.quantity + Number(q);
            if (new_qty < 0) {
                new_qty = 0;
            }
            sighting.quantity = new_qty;
            axios.post(update_count_url, {
                id: sighting.id,
                quantity: new_qty,
            }).then(function (r) {
            });
        },
        add_species: function () {
            let self = this;
            axios.post(add_species_url, {
                species: this.new_species,
                quantity: 1,
            }).then(function (r) {
                self.sightings.push({
                    id: r.data.id,
                    species: self.new_species,
                    quantity: 1,
                });
                self.new_species = "";
            });
        }, 
        delete_species: function (s_idx) {
            let self = this;
            let sighting = this.sightings[s_idx];
            axios.post(delete_sighting_url, {
                id: sighting.id,
            }).then(function (r) {
                self.sightings.splice(s_idx, 1);
            });
        },
        delete_species_bis: function (s_idx) {
            let self = this;
            let sighting = this.sightings[s_idx];
            axios.delete(delete_sighting_bis_url, { 
                params: {id: sighting.id,}
            }).then(function (r) {
                self.sightings.splice(s_idx, 1);
            });
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

