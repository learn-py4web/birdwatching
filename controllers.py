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

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email
from py4web.utils.form import Form, FormStyleBulma
from py4web import Field

url_signer = URLSigner(session)

@action('index')
@action.uses('index.html', db, auth.user)
def index():
    checklists = db(db.checklist.created_by == get_user_email()).select(orderby=~db.checklist.checklist_date)
    return dict(checklists=checklists)


def get_birds(bird_string):
    """Returns a list of pairs (count, species) of the birds
    the user wants to create."""
    lines = bird_string.split("\n")
    birds = []
    for l in lines:
        w = l.split()
        if len(w) > 1:
            birds.append((int(w[0]), " ".join(w[1:])))
    return birds

def validate_birds(form):
    # Variables are in form.vars["name of variable"]
    # You can set errors in form.errors["name of variable"]
    lines = form.vars["birds"].split("\n")
    for l in lines:
        w = l.split()
        if len(w) == 1:
            form.errors["birds"] = "Line '{}' does not contain a count and a species".format(l)
            break
        if len(w) > 1:
            try:
                c = int(w[0])
            except:
                form.errors["birds"] = "Line '{}' does not start with a count".format(l)
                break
            

@action('add', method=["GET", "POST"])
@action.uses('add.html', db, auth.user)
def add():
    form = Form(
        [Field('name'),
         Field('birds', 'text')],
        formstyle=FormStyleBulma,
        csrf_session=session,
        validation=validate_birds
    )
    if form.accepted:
        # We have to insert checklist and birds. 
        # Let's create the checklist first. 
        checklist_id = db.checklist.insert(checklist_name=form.vars["name"])
        # Now for the birds.
        birds = get_birds(form.vars["birds"])
        for c, b in birds:
            db.bird.insert(
                checklist=checklist_id,
                species=b,
                bird_count=c
            )
        redirect(URL('view', checklist_id))
    return dict(form=form)

@action('view/<checklist_id:int>')
@action.uses('view.html', db, session, auth.user, url_signer)
def view(checklist_id=None):
    # c = db(db.checklist.id == checklist_id).select().first()
    c = db.checklist[checklist_id]
    if c is None or c.created_by != get_user_email(): 
        redirect(URL('index'))
    # Gets birds in checklist. 
    birds = db(db.bird.checklist == checklist_id).select()
    return dict(checklist=c, birds=birds, url_signer=url_signer)

@action('inc_bird/<checklist_id:int>/<amount:int>/<bird_id:int>')
@action.uses(db, url_signer.verify())
def inc_bird(checklist_id, amount, bird_id):
    c = db.checklist[checklist_id]
    if c is None or c.created_by != get_user_email():
        redirect(URL('view', checklist_id))
    b = db.bird[bird_id]
    if b is None:
        redirect(URL('view', checklist_id))
    new_count = b.bird_count + amount
    if new_count <= 0:
        db(db.bird.id == bird_id).delete()
    else:
        b.update_record(bird_count=new_count)
    redirect(URL('view', checklist_id))
        
@action('add_species/<checklist_id:int>', method=["GET", "POST"])
@action.uses('add_species.html', db, auth.user)
def add_species(checklist_id):
    c = db.checklist[checklist_id]
    if c is None or c.created_by != get_user_email():
        redirect(URL('view', checklist_id))
    form = Form(
        [Field('birds', 'text')],
        formstyle=FormStyleBulma,
        csrf_session=session,
        validation=validate_birds
    )
    if form.accepted:
        birds = get_birds(form.vars["birds"])
        for c, b in birds:
            # Checks if the bird already exists.
            existing_b = db((db.bird.checklist == checklist_id) & (db.bird.species == b)).select().first()
            if existing_b is not None:
                # The bird already exists. We just increment its count. 
                existing_b.update_record(bird_count = existing_b.bird_count + c)
            else:
                # The bird is new.
                db.bird.insert(
                    checklist=checklist_id,
                    species=b,
                    bird_count=c
                )
        redirect(URL('view', checklist_id))
    return dict(form=form)
        

    