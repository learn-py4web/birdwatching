"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL, HTTP
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email
from .settings import ADMIN_LIST
from .admin_fixture import Admin
from .local_storage_fixture import LocalStorageDemo

import math

admin = Admin(auth, ADMIN_LIST)
local_storage_demo = LocalStorageDemo()


@action('index')
@action.uses('index.html', db, auth)
def index():
    return dict(
        # COMPLETE: return here any signed URLs you need.
        get_sightings_url = URL('get_sightings'),
        add_species_url = URL('add_species'),
        update_count_url = URL('update_count'),
        delete_sighting_url = URL('delete_sighting'),
        delete_sighting_bis_url = URL('delete_sighting_bis'),
    )

    
@action('get_sightings')
@action.uses(db, auth.user)
def get_sightings():
    user_email = get_user_email()
    sightings = []
    if user_email:
        sightings = db(db.sighting.user_email == user_email).select(orderby=db.sighting.species).as_list()
    return dict(sightings=sightings, user_email=user_email)


@action('update_count', method="POST")
@action.uses(db, auth.user)
def update_count():
    user_email = get_user_email()
    id = request.json.get('id')
    quantity = request.json.get('quantity')

    # db((db.sighting.id == id) & 
    #    (db.sighting.user_email == user_email)).update(quantity=quantity)
    # return "ok"

    sighting = db(db.sighting.id == id).select().first()
    if not sighting or sighting.user_email != user_email:
        raise HTTP(403)
    sighting.update_record(quantity=quantity)
    return "ok"


@action('add_species', method="POST")
@action.uses(db, auth.user)
def add_species():
    species = request.json.get('species')
    quantity = request.json.get('quantity')
    id = db.sighting.insert(species=species, quantity=quantity)
    return dict(id=id)


@action('delete_sighting', method="POST")
@action.uses(db, auth.user)
def delete_sighting():
    user_email = get_user_email()
    id = request.json.get('id')
    db((db.sighting.id == id) & 
       (db.sighting.user_email == user_email)).delete()
    return "ok"

@action('delete_sighting_bis', method="DELETE")
@action.uses(db, auth.user)
def delete_sighting():
    user_email = get_user_email()
    id = request.params.get('id')
    db((db.sighting.id == id) & 
       (db.sighting.user_email == user_email)).delete()
    return "ok"
