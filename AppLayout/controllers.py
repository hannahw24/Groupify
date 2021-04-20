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
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated
############ Notice, new utilities! ############
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth
import time
import os
import uuid
################################################

# The cache folder is located in the /py4web folder. 
# Keep this in mind when we move on from local hosting. 
caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

def session_cache_path():
    return caches_folder + session.get('uuid')

# Ash: Permissions needed to be accepted by the user at login. There are more but these are the ones
# we use right now, so they are the only ones we ask.
scopes = "user-library-read user-read-private user-follow-read user-follow-modify user-top-read"

@action('index', method='GET')
@action.uses('index.html', session)
def getIndex():
    return dict(session=session, editable=False)

# https://github.com/plamere/spotipy/blob/master/examples/search.py
# Emulates the caching, authentication managing, and uuid assigning as 
# shown in the above git repository. It is an example of multi-person login
# with spotipy. 
# See License of code at https://github.com/plamere/spotipy/blob/master/LICENSE.md 
@action('login', method='GET')
@action.uses('login.html', session)
def userLogin():
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    # Magic code; takes in our client_id, secret_id, and redirect_uri and 
    # and once the user accepts the requested permissions it retrieves a token for us.
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope=scopes,
                                                cache_handler=cache_handler, 
                                                show_dialog=True)
    auth_url = auth_manager.get_authorize_url()
    # In this case the auth_url is [localhost]/callback
    return redirect(auth_url)

@action('callback')
@action.uses(session)
def getCallback():
    # Ash: Clear the session in case a user has logged out. If we don't do this and a user tries to login with another
    # account then they will be logged in to their first account no matter what. 
    session.clear()
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(scope=scopes,
                                                cache_handler=cache_handler, 
                                                show_dialog=True)
    # How to get a parameter from a url.
    # https://stackoverflow.com/questions/5074803/retrieving-parameters-from-a-url 
    code = request.GET.get('code')
    error = request.GET.get('error')
    # Ash: If the user cancels their login then this handles the error by taking them back to the login page.
    if error is not None:
        print(error)
        return redirect(URL('index'))
    auth_manager.get_access_token(code)
    return redirect("getUserInfo")

# Places a User's info in the database and then sends them to their profile.
@action('getUserInfo')
@action.uses(db, session)
def getUserInfo():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('login')

    # Necessary to make a call to the API.
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    # "sp.current_user()" returns: display name, email
    # url to user, id, images (profile pic), and premium status
    results = spotify.current_user()

    #print(results)
    #print("")
    #print (results["display_name"]) #Example: "Ash"
    display_name = results["display_name"]
    #print (results["id"])
    userID = results["id"]
    if (len(results["images"]) != 0):
        #print (results["images"][0]["url"])
        profile_pic = results["images"][0]["url"]
    else:
        # We need to assign a default picture for users without a profile picture.
        profile_pic = None

    #Test function ignore
    #search()

    # Assigns the userID to the session. This is used to verify who can edit
    # profiles. 
    session["userID"] = userID
    # Gets the URL ready for the redirect
    profileURL = "user/" + userID
    # Gets the User's top tracks
    topTracks = getTopTracksFunction()
    # Checks to see if it can get the user from the database
    dbUserEntry = (db(db.dbUser.userID == userID).select().as_list())
    # Not sure if returns as None or an empty list if user is new.
    if (dbUserEntry == None) or dbUserEntry == []:
        db.dbUser.insert(userID=userID, display_name=display_name, profile_pic=profile_pic, topTracks=topTracks)
        print("Hello1")
        return redirect(profileURL)
    # If it is in the database, update its top tracks
    else:
        db.dbUser.update_or_insert(db.dbUser.userID == userID,
                                topTracks=topTracks)
        print("Hello2")
        return redirect(profileURL)

# Profile tests (currently no difference between them)
# http://127.0.0.1:8000/AppLayout/user/1228586386           Ash's Main Account
# http://127.0.0.1:8000/AppLayout/user/wjmmbwcxcja7s2acm9clcydkb    Ash's Test Account
@action('user/<userID>', method='GET')
@action.uses('user.html', session)
def getUserProfile(userID=None):
    # Function determines whether or not the current user can edit the profile
    print("Editable: ", editable_profile(userID))
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if (not auth_manager.validate_token(cache_handler.get_cached_token())) or (userID == None):
        return redirect(URL('index'))
    # Command below finds friends of the profile user is viewing 
    # rows = db(db.dbUser.userID == userID).select().as_list()

    # Commands below finds friends of the person logged in
    profile_info = session.get("userID")
    rows = db(db.dbUser.userID == profile_info).select().as_list()

    topTracks = ""
    profile_pic = ""
    currentProfileTopTracksList = (db(db.dbUser.userID == userID).select().as_list())
    if (currentProfileTopTracksList != None) and (currentProfileTopTracksList != []):
        topTracks = currentProfileTopTracksList[0]["topTracks"]
        profile_pic = currentProfileTopTracksList[0]["profile_pic"]
    print("topTracks user: ", topTracks)
    #Avoid the for loop errors in user.html that would occur if friendsList is None
    friendsList = []
    for row in rows:
        userNumber = row["id"]
        friendsList = db(db.dbFriends.friendToWhoID == userNumber).select().as_list()
    if ((friendsList != None) and len(friendsList) > 0):
        print ("friendsList ", friendsList)
        print (friendsList[0]["display_name"])
    # returns editable for the "[[if (editable==True):]]" statement in layout.html
    return dict(session=session, editable=editable_profile(userID), friendsList=friendsList, topTracks=topTracks, profile_pic=profile_pic)

# Returns whether the user can edit a profile
@action.uses(session)
def editable_profile(userID):
    profileOwner = False
    if userID == None:
        return profileOwner
    profile_info = session.get("userID")
    # Checking if the session already has a token stored
    if profile_info != userID:
        return profileOwner

    profileOwner = True
    return profileOwner

# https://jsonformatter.curiousconcept.com/
@action.uses(session)
def search():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('login')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    results = spotify.search("The Strokes", limit=1)
    print (results)
    return

# AppLayout/getLikedTracks
# Returns the most recent 20 liked songs
@action('getLikedTracks')
def getLikedTracks():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('login')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    results = spotify.current_user_saved_tracks()
    #Taken from the quick start of Spotipy authorization flow
    #https://spotipy.readthedocs.io/en/2.18.0/#authorization-code-flow
    LikedSongsString= ""
    for idx, item in enumerate(results['items']):
        track = item['track']
        LikedSongsString = LikedSongsString + str((idx, track['artists'][0]['name'], " – ", track['name'])) + "<br>"
    return LikedSongsString

def getTopTracksFunction():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('login')
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    # long_term = all time
    # medium_term = 6 months
    # short_term = 4 weeks
    results = spotify.current_user_top_tracks(limit=10, offset=0, time_range="short_term")
    #Taken from the quick start of Spotipy authorization flow
    #https://spotipy.readthedocs.io/en/2.18.0/#authorization-code-flow
    TopSongsString= ""
    TopSongsList = []
    for idx, item in enumerate(results['items']):
        track = item['name']
        TopSongsList.append(track)
        TopSongsString = TopSongsString + str(track) + "<br>"
    # Shown in the anaconda window 
    print(TopSongsString)

    if TopSongsList == []:
        TopSongsList = ""
    # Returned to the user profile
    return TopSongsList

@action('groupSession')
@action.uses(db, auth, 'groupSession.html', session)
def groupSession():
    return dict(session=session, editable=False)

# Ash: There isn't a settings page right now
@action('settings')
@action.uses(db, auth, 'settings.html', session)
def getSettings():
    return dict(session=session, editable=False)

# Taken from the spotipy examples page referenced above.
@action('sign_out')
@action.uses(session)
def sign_out():
    try:
        # Remove the CACHE file (.cache-test) so that a new user can authorize.
        os.remove(session_cache_path())
        session.clear()
    except OSError as e:
        print ("Error: %s - %s." % (e.filename, e.strerror))
    return redirect(URL('index'))
