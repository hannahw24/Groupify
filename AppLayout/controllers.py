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

from py4web import action, request, abort, redirect, URL, Field
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated
from py4web.utils.form import Form, FormStyleBulma
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

# When you login, Spotify goes to this
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

# After callback, the user goes to this function and has their info made/updated
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

    display_name = results["display_name"]
    userID = results["id"]
    if (len(results["images"]) != 0):
        profile_pic = results["images"][0]["url"]
    else:
        profile_pic = ""

    # Assigns the userID to the session. This is used to verify who can edit
    # profiles. 
    session["userID"] = userID
    # Gets the URL ready for the redirect
    profileURL = "user/" + userID
    # Gets the User's top tracks
    tracksList = getTopTracksFunction()
    topTracks = tracksList[0]
    topArtists = tracksList[1]
    imgList = tracksList[2]
    trackLinks = tracksList[3]
    artistLinks = tracksList[4]
    # Checks to see if it can get the user from the database
    dbUserEntry = (db(db.dbUser.userID == userID).select().as_list())
    shortTermEntry = (db(db.shortTerm.topTracksOfWho == getIDFromUserTable(userID)).select().as_list())
    # This takes all the instances of the logged in user in the friends database. 	
    # This is so we can update their information.
    friendsEntries =  (db(db.dbFriends.userID == userID).select().as_list())

    # Not sure if returns as None or an empty list if user is new.
    if (dbUserEntry == None) or dbUserEntry == []:
        db.dbUser.insert(userID=userID, display_name=display_name, profile_pic=profile_pic)
        insertedID = getIDFromUserTable(userID)
    # If it is in the database, update its top tracks
    else:
        # Update all info
        db(db.dbUser.userID == userID).update(display_name=display_name)
        db(db.dbUser.userID == userID).update(profile_pic=profile_pic)
    # Updates the information in friends database so the friends NAV bar is up to date. 
    if (friendsEntries != None) and (friendsEntries != []):
        if friendsEntries[0]["profile_pic"] != profile_pic:
            print("Differences in profile pic!")
            for row in friendsEntries:
                dbRow = db(db.dbFriends.id == row["id"])
                dbRow.update(profile_pic=profile_pic)
                dbRow.update(display_name=display_name)
    # Is there shortTerm top tracks populated?
    if (shortTermEntry == None) or (shortTermEntry == []):
        insertedID = getIDFromUserTable(userID)
        print("insertedID ", insertedID)
        db.shortTerm.insert(topTracks=topTracks, topArtists=topArtists, imgList=imgList, 
                            trackLinks=trackLinks, artistLinks=artistLinks, topTracksOfWho=insertedID)
    # If it is update it
    else:
        insertedID = getIDFromUserTable(userID)
        print("insertedID ", insertedID)
        # Updates their songs of the past 4 weeks. 
        dbRow =  db(db.shortTerm.topTracksOfWho == insertedID)
        dbRow.update(topTracks=topTracks)
        dbRow.update(topArtists=topArtists)
        dbRow.update(imgList=imgList)
        dbRow.update(trackLinks=trackLinks)
        dbRow.update(artistLinks=artistLinks)
    
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
    loggedInUserEntry = db(db.dbUser.userID == session.get("userID")).select().as_list()
    currentProfileEntry = db(db.dbUser.userID == userID).select().as_list()
    shortTermList = db(db.shortTerm.topTracksOfWho == getIDFromUserTable(userID)).select().as_list()

    # Declared early for checking an error where a user hasn't listened to songs, do not remove
    topTracks = None

    # Get the fields from the shortTermList, but only if they have a reference in it 
    if shortTermList != []:
        topTracks = shortTermList[0]["topTracks"]
        topArtists = shortTermList[0]["topArtists"]
        imgList = shortTermList[0]["imgList"]
        trackLinks = shortTermList[0]["trackLinks"]
        artistLinks = shortTermList[0]["artistLinks"]

    # This handles if a user hasn't listened to any songs or has less than 10 songs listened to.
    if (topTracks == None) or len(topTracks) < 10:
        topTracks = fillerTopTracks
        topArtists = fillerTopTracks
        imgList = fillerTopTracks
        trackLinks = fillerTopTracks
        artistLinks = fillerTopTracks

    profile_pic = ""
    if (currentProfileEntry != None) and (currentProfileEntry != []):
        # Setting the top tracks and profile pic variables
        profile_pic = currentProfileEntry[0]["profile_pic"]
    print("topTracks user: ", topTracks)
    #Avoid the for loop errors in user.html that would occur if friendsList is None
    friendsList = []
    for row in loggedInUserEntry:
        userNumber = row["id"]
        friendsList = db(db.dbFriends.friendToWhoID == userNumber).select(orderby=db.dbFriends.display_name).as_list()
    if ((friendsList != None) and len(friendsList) > 0):
        print ("friendsList ", friendsList)
        print (friendsList[0]["display_name"])
    # returns editable for the "[[if (editable==True):]]" statement in layout.html
    return dict(session=session, editable=editable_profile(userID), friendsList=friendsList, topTracks=topTracks,
                topArtists=topArtists, imgList=imgList, trackLinks=trackLinks, artistLinks=artistLinks, profile_pic=profile_pic)

def getIDFromUserTable(userID):
    insertedID = (db(db.dbUser.userID == userID).select().as_list())
    if (insertedID is not None) and (insertedID != []):
        return insertedID[0]["id"]
    return None

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
    # Initialize Lists for each field
    TopSongsString= ""
    TopSongsList = []
    TopArtistsList = []
    ImgLinkList = []
    TLinkList = []
    ALinkList = []
    BigList = []
    for idx, item in enumerate(results['items']):
        # Get items from correct place in given Spotipy dictionary
        track = item['name']
        trackInfo = item['album']['artists'][0]['name']
        icon = item['album']['images'][2]['url']
        trLink = item['external_urls']['spotify']
        artLink = item['album']['artists'][0]['external_urls']['spotify']
        TopSongsList.append(track)
        TopSongsString = TopSongsString + str(track) + "<br>"
        TopArtistsList.append(trackInfo)
        ImgLinkList.append(icon)
        TLinkList.append(trLink)
        ALinkList.append(artLink)
    # Avoid empty lists
    if TopSongsList == []:
        TopSongsList = ""
    if TopArtistsList == []:
        TopArtistsList= ""
    if ImgLinkList == []:
        ImgLinkList = ""
    if TLinkList == []:
        TLinkList = ""
    if TLinkList == []:
        ALinkList = ""
    # Add all to list to be returned
    BigList.append(TopSongsList)
    BigList.append(TopArtistsList)
    BigList.append(ImgLinkList)
    BigList.append(TLinkList)
    BigList.append(ALinkList)
    # Returned to the user profile
    return BigList

@action('groupSession')
@action.uses(db, auth, 'groupSession.html', session)
def groupSession():
    # Ash: set editable to False for now, not sure if setting the theme
    #      on the groupSession page will change it for everyone
    return dict(session=session, editable=False)

# Ash: There isn't a settings page right now
@action('settings')
@action.uses(db, auth, 'settings.html', session)
def getSettings():
    return dict(session=session, editable=False)

# Haanah: There isn't an add friend page right now
@action('add_friend', method=["GET", "POST"])
@action.uses(db, auth, 'add_friend.html', session)
def addFriend():
    userID = session.get("userID")
    form = Form([Field('userID', notnull=True)], session=session, formstyle=FormStyleBulma)
    if form.accepted:
        dbUserEntry = (db(db.dbUser.userID == form.vars["userID"]).select().as_list())
        if dbUserEntry == []:
            print ("Yo this person doesn't even exist")
            redirect(URL('user', session.get("userID")))
        db.dbFriends.insert(userID=form.vars["userID"], friendToWhoID=getIDFromUserTable(userID), 
                            profile_pic=dbUserEntry[0]["profile_pic"], display_name=dbUserEntry[0]["display_name"])
        redirect(URL('user', session.get("userID")))
    return dict(form = form, session=session, editable=False)

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

fillerTopTracks = ["Listen to more songs to see results", "Listen to more songs to see results",  
"Listen to more songs to see results",  "Listen to more songs to see results", "Listen to more songs to see results", 
 "Listen to more songs to see results",  "Listen to more songs to see results",  "Listen to more songs to see results", 
  "Listen to more songs to see results",  "Listen to more songs to see results",  "Listen to more songs to see results", ]