"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later

db.define_table('checklist',
                Field('checklist_name'),
                Field('created_by', default=get_user_email),
                Field('checklist_date', 'datetime', default=get_time),
                )

db.define_table('bird',
                Field('species'),
                Field('checklist', db.checklist), # or "reference checklist"
                Field('bird_count', 'integer', requires=IS_INT_IN_RANGE(0, 1000000)),
                )

db.commit()
