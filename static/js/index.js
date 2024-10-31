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
            pending: false,
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
            self.pending = true;
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
                self.pending = false;
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
        upload_image: function (s_idx) {
            let self = this;
            let file_picker = document.createElement("input");
            file_picker.type = "file";
            file_picker.onchange = function () {
                let file = file_picker.files[0];
                console.log(file.name);
                let reader = new FileReader();
                reader.addEventListener("load", function () {
                    let img_url = reader.result;
                    // Add it to the list of thumbnails for the bird. 
                    let sighting = self.sightings[s_idx];
                    sighting.thumbnails.push(img_url);
                    // Upload the image. 
                    axios.post(add_image_url, {
                        id: sighting.id,
                        image_url: img_url,
                    });
                });
            reader.readAsDataURL(file);
            };
            file_picker.click();
        }
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

