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
    Field('profile_pic'),
<<<<<<< HEAD
=======
    Field('topTracks')
>>>>>>> 09e791cc15bd4c252a9796cecd4d7c84460e65c6
)

db.define_table(
    'dbFriends',
    Field('userID', notnull=True, unique=True),
    Field('display_name'),
    Field('profile_pic'),
    #Ash: This should connect the friends table to the user table
    Field('friendToWhoID', db.dbUser)
)

<<<<<<< HEAD

# Table to store the short_term tracks, medium_term and long_term should have their own tables
db.define_table(
    'shortTerm',
    Field('topTracks', 'list:string'),
    Field('topArtists', 'list:string'), # Artists for each top track
    Field('imgList', 'list:string'),
    Field('trackLinks', 'list:string'),
    Field('artistLinks', 'list:string'), 
    Field('topTracksOfWho', db.dbUser)
)

=======
>>>>>>> 09e791cc15bd4c252a9796cecd4d7c84460e65c6
#“extra” is not a keyword; it’s a custom attribute now attached to the field object. You can do it with tables too but they must be preceded by an underscore to avoid naming conflicts with fields:
#db.table._extra = {}


db.commit()