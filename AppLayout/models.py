"""
This file defines the database models
"""

from .common import db, Field
from pydal.validators import *

### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later
#
# db.commit()
#
db.define_table(
    'dbUser',
    Field('userID', notnull=True, unique=True),
    Field('display_name'),
    #Ash: email may be unnecessary. 
    Field('profile_pic')
)

db.define_table(
    'dbFriends',
    Field('userID', notnull=True, unique=True),
    Field('display_name'),
    Field('profile_pic'),
    #Ash: This should connect the friends table to the user table
    Field('friendToWhoID', db.dbUser)
)

#“extra” is not a keyword; it’s a custom attribute now attached to the field object. You can do it with tables too but they must be preceded by an underscore to avoid naming conflicts with fields:
#db.table._extra = {}


db.commit()