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
Warning: Fixtures MUST be declared with @action.uses({fixtures}) 
else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL, Field
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated
from py4web.utils.form import Form, FormStyleBulma
from py4web.utils.url_signer import URLSigner
from html.parser import HTMLParser
from datetime import datetime
import time
############ Notice, new utilities! ############
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import os
import uuid
################################################
os.environ["SPOTIPY_CLIENT_ID"] = "f4cfb74420ed4bcaab8408922adb5820"
os.environ["SPOTIPY_CLIENT_SECRET"] = "d9ff6b1b8e0d4dd3a421f0c1e4f70e67"
os.environ["SPOTIPY_REDIRECT_URI"] = "http://127.0.0.1:8000/groupify/callback"

# The cache folder is located in the /py4web folder. 
# Keep this in mind when we move on from local hosting.
caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

def session_cache_path():
    return caches_folder + session.get('uuid')

# Ash: Permissions needed to be accepted by the user at login. There are more but these are the ones
# we use right now, so they are the only ones we ask.
scopes = "user-library-read user-read-private user-follow-read \
user-follow-modify user-top-read streaming user-read-email streaming \
app-remote-control user-read-playback-state user-modify-playback-state \
user-read-currently-playing"

url_signer = URLSigner(session)

def getUserID():
    return session.get("userID")

@action('index', method='GET')
@action.uses('index.html', session)
def getIndex(userID=None):
    # If session is still active, we do not ask users to login again.
    if session.get("userID") is not None:
        # Instead of redirecting them to their profiles, we send them
        # to "getUserInfo" to see any of their information has changed.
        print (session.get("userID"))
        return getUserInfo()
    if userID is not None:
        user_from_table = db.dbUser[getIDFromUserTable(session.get("userID"))]
        theme_colors = return_theme(user_from_table.chosen_theme)

        return dict(
            session=session,
            editable=False,
            background_bot=theme_colors[0],
            background_top=theme_colors[1],
            )
    else:
        return dict( 
            session=session, editable=False,
            background_bot=None,
            background_top=None,)

# https://github.com/plamere/spotipy/blob/master/examples/search.py
# Emulates the caching, authentication managing, and uuid assigning as
# shown in the above git repository. It is an example of multi-person login
# with spotipy.
# See License of code at https://github.com/plamere/spotipy/blob/master/LICENSE.md 
# Step 0: Visitor is unknown, give random ID, then make them sign in
# with Spotify
@action('login', method='GET')
@action.uses('index.html', session)
def userLogin():
    if not session.get('uuid'):
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

# Step 1: When you login, Spotify goes back to this
@action('callback')
@action.uses(session)
def getCallback():
    # Clear the session in case a user has logged out. If we don't do this and a user tries to login with another
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
    # Redirect to the function that stores user information in database tables.
    return redirect("getUserInfo")

# Step 2: After callback, the user goes to this function and has their info made/updated
# Places a User's info in the database and then sends them to their profile.
@action('getUserInfo')
@action.uses(db, session)
def getUserInfo():
    # Makes sure we have a user token from Spotify, else return user to login
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect(URL('login'))

    # Necessary to make a call to the API.
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    # url to user, id, images (profile pic), and premium status
    results = spotify.current_user()
    print (results)
    display_name = results["display_name"]
    display_name = display_name.capitalize()
    userID = results["id"]
    premiumStatus = results["product"]

    # Sets the profile pic of the user, if no profile pic found on spotify, set it to nothing
    if (len(results["images"]) != 0):
        profile_pic = results["images"][0]["url"]
    else:
        profile_pic = ""

    # Assigns the userID to the session. This is used to verify who can edit
    # profiles. 
    session["userID"] = userID
    # Gets the URL ready for the redirect
    profileURL = "user/" + userID
    # Obtains the user entry from dbUser 
    dbUserEntry = (db(db.dbUser.userID == userID).select().as_list())
    # Finds the album covers table corresponding to the user
    squareEntries = db(db.squares.albumsOfWho == getIDFromUserTable(userID)).select().as_list()
    # This takes all the instances of the logged in user in the friends database. 	
    # This is so we can update their information.
    friendsEntries =  (db(db.dbFriends.userID == userID).select().as_list())


    # Not sure if returns as None or an empty list if user is new.
    if (dbUserEntry == None) or dbUserEntry == []:
        db.dbUser.insert(userID=userID, display_name=display_name, 
                        profile_pic=profile_pic, premiumStatus=premiumStatus)
        insertedID = getIDFromUserTable(userID)
    # If it is in the database, update its top tracks
    else:
        # Update all info
        db(db.dbUser.userID == userID).update(display_name=display_name)
        db(db.dbUser.userID == userID).update(profile_pic=profile_pic)
        db(db.dbUser.userID == userID).update(premiumStatus=premiumStatus)
    # Updates the information in friends database so the friends NAV bar is up to date. 
    if (friendsEntries != None) and (friendsEntries != []):
        # If user profile or name has changed, update it.
        if (friendsEntries[0]["profile_pic"] != profile_pic) or \
            (friendsEntries[0]["display_name"] != display_name):
            for row in friendsEntries:
                dbRow = db(db.dbFriends.id == row["id"])
                dbRow.update(profile_pic=profile_pic)
                dbRow.update(display_name=display_name)
                
    # These are function calls that store/update the user's tops songs
    # over three time periods
    getTopTracksLen(userID, "short_term")	
    getTopTracksLen(userID, "medium_term")	
    getTopTracksLen(userID, "long_term")

    getTopArtistsLen(userID, "shortArtists")
    getTopArtistsLen(userID, "mediumArtists")
    getTopArtistsLen(userID, "longArtists")

    # Stores/updates user playlists
    storePlaylists(userID)

    # If the album covers table is empty, we insert it here
    if (squareEntries == None) or (squareEntries == []):
        insertedID = getIDFromUserTable(userID)
        db.squares.insert(albumsOfWho=insertedID)
    # After inserting/updating user information, send them to their 
    # profile page
    return redirect(URL(profileURL))

# A function that updates the top songs table specified by "term".
def getTopTracksLen(userID, term):
    # A list containing information about the User's top tracks. 
    # "term" is a period passed in to select the songs from a desired time.
    tracksList = getTopTracksFunction(term)
    topTracks = tracksList[0] # Names
    topArtists = tracksList[1] # Names
    imgList = tracksList[2] # URLs to images
    trackLinks = tracksList[3] # URLs to songs
    artistLinks = tracksList[4] # URLs to artists

    # Selects the correct user entry from the desired time period
    if term == 'short_term':
        termEntry = (db(db.shortTerm.topTracksOfWho 
                    == getIDFromUserTable(userID)).select().as_list())
    elif term == 'medium_term':
        termEntry = (db(db.mediumTerm.topTracksOfWho 
                    == getIDFromUserTable(userID)).select().as_list())
    elif term == 'long_term':
        termEntry = (db(db.longTerm.topTracksOfWho 
                    == getIDFromUserTable(userID)).select().as_list())

    # Is their desired term of top tracks populated?
    # If it isn't, then the information from tracksList will be inserted.
    if (termEntry == None) or (termEntry == []):
        insertedID = getIDFromUserTable(userID)
        if term == 'short_term':
            db.shortTerm.insert(topTracks=topTracks, topArtists=topArtists,
                                imgList=imgList, trackLinks=trackLinks, 
                                artistLinks=artistLinks, topTracksOfWho=insertedID)
        elif term == 'medium_term':
            db.mediumTerm.insert(topTracks=topTracks, topArtists=topArtists, 
                                imgList=imgList, trackLinks=trackLinks, 
                                artistLinks=artistLinks, topTracksOfWho=insertedID)
        elif term == 'long_term':
            db.longTerm.insert(topTracks=topTracks, topArtists=topArtists, 
                                imgList=imgList, trackLinks=trackLinks, 
                                artistLinks=artistLinks, topTracksOfWho=insertedID)

    # If there are already tracks, then update the information
    else:
        insertedID = getIDFromUserTable(userID)
        # Finds the correct user entry
        if term == 'short_term':
            dbRow = db(db.shortTerm.topTracksOfWho == insertedID)
        elif term == 'medium_term':
            dbRow = db(db.mediumTerm.topTracksOfWho == insertedID)
        elif term == 'long_term':
            dbRow = db(db.longTerm.topTracksOfWho == insertedID)

        dbRow.update(topTracks=topTracks, topArtists=topArtists, 
        imgList=imgList, trackLinks=trackLinks, artistLinks=artistLinks)
    return

def getTopArtistsLen(userID, term):
    # Convert term passed in into something that the spotify API will
    # accept. 
    if term == 'shortArtists':
        spotifyTerm = 'short_term'
    elif term == 'mediumArtists':
        spotifyTerm = 'medium_term'
    elif term == 'longArtists':
        spotifyTerm = 'long_term'

    # A list containing information about the User's top tracks. 
    # "term" is a period passed in to select the songs from a desired time.
    artistList = getTopArtistsFunction(spotifyTerm)

    topArtists = artistList[0] # Names
    imgList = artistList[1] # URLs to images
    artistLinks = artistList[2] # URLs to artists
    genres = artistList[3] # Artist's genres
    
    followers = artistList[4] # Number of followers the artist has

    # Selects the correct user entry from the desired time period
    if term == 'shortArtists':
        termEntry = (db(db.shortArtists.topArtistsOfWho 
                    == getIDFromUserTable(userID)).select().as_list())
    elif term == 'mediumArtists':
        termEntry = (db(db.mediumArtists.topArtistsOfWho 
                    == getIDFromUserTable(userID)).select().as_list())
    elif term == 'longArtists':
        termEntry = (db(db.longArtists.topArtistsOfWho 
                    == getIDFromUserTable(userID)).select().as_list())

    # Is their desired term of top tracks populated?
    # If it isn't, then the information from tracksList will be inserted.
    if (termEntry == None) or (termEntry == []):
        insertedID = getIDFromUserTable(userID)
        if term == 'shortArtists':
            db.shortArtists.insert(topArtists=topArtists, imgList=imgList, artistLinks=artistLinks, 
            genres=genres, followers=followers, topArtistsOfWho=insertedID)
        elif term == 'mediumArtists':
            db.mediumArtists.insert(topArtists=topArtists, imgList=imgList, artistLinks=artistLinks, 
            genres=genres, followers=followers, topArtistsOfWho=insertedID)
        elif term == 'longArtists':
            db.longArtists.insert(topArtists=topArtists, imgList=imgList, artistLinks=artistLinks, 
            genres=genres, followers=followers, topArtistsOfWho=insertedID)

    # If there are already tracks, then update the information
    else:
        insertedID = getIDFromUserTable(userID)
        # Finds the correct user entry
        if term == 'shortArtists':
            dbRow = db(db.shortArtists.topArtistsOfWho == insertedID)
        elif term == 'mediumArtists':
            dbRow = db(db.mediumArtists.topArtistsOfWho == insertedID)
        elif term == 'longArtists':
            dbRow = db(db.longArtists.topArtistsOfWho == insertedID)

        dbRow.update(topArtists=topArtists, imgList=imgList, 
        artistLinks=artistLinks, genres=genres, followers=followers)
    return

# Profile tests (currently no difference between them)
# http://127.0.0.1:8000/AppLayout/user/1228586386           Ash's Main Account
# http://127.0.0.1:8000/AppLayout/user/wjmmbwcxcja7s2acm9clcydkb    Ash's Test Account

# Function that returns all the information needed for the user page. 
# userID that is passed into the function can be the logged in user, or 
# another user. 
@action('user/<userID>', method='GET')
@action.uses('user.html', session)
def getUserProfile(userID=None):
    # Function determines whether or not the current user can edit the profile
    print("Editable: ", editable_profile(userID))

    # If the user has not logged in, this forces them to login
    # This is an implementation decision that can change later.
    if (session.get("userID") == None) or (userID == None):
        return redirect(URL('index'))

    # Finds the entry inside dbUser of the logged in user.
    loggedInUserEntry = db(db.dbUser.userID == session.get("userID")).select().as_list()
    # Finds the entry inside dbUser of the profile the user wants to visit
    currentProfileEntry = db(db.dbUser.userID == userID).select().as_list()
    # If the profile they want to access does not exist, return userNotFound page
    if currentProfileEntry == []:
        return userNotFound(session.get("userID"))

    # Looks at the dbUser database to see what the chosen term of the top 10 songs are for
    # the profile the user wants to access

    # Obtains the album covers of the profile the user wants to vist
    squareEntries = db(db.squares.albumsOfWho == getIDFromUserTable(userID)).select().as_list()

    # A list of URLs which are used to display images of the covers
    coverList = squareEntries[0]["coverList"]
    # a list of URLs to redirect users to the albums in each box
    urlList = squareEntries[0]["urlList"]

    playlistEntry = (db(db.playlists.playlistsOfWho 
                        == getIDFromUserTable(userID)).select().as_list())
    # Remove this later, is here to make it so accessing users who haven't logged do not crash
    if playlistEntry == []:
        playlistNames = []
        playlistImages = []
        playlistURLs = []
        playlistDescriptions = []
    else:
        playlistNames = playlistEntry[0]["names"]
        playlistImages = playlistEntry[0]["images"]
        playlistURLs = playlistEntry[0]["links"]
        playlistDescriptions = playlistEntry[0]["descriptions"]
    # To see if the button "Unfollow" or "Follow" appears
    isFriend = False

    # Sets the user's profile pic
    profile_pic = ""
    if (currentProfileEntry != None) and (currentProfileEntry != []):
        # Setting profile pic variable to display on page
        profile_pic = currentProfileEntry[0]["profile_pic"]
    # Avoid the for loop errors in user.html that would occur if friendsList is None
    friendsList = []
    # The friends list shown will ALWAYS be of the user who is logged in
    userNumber = loggedInUserEntry[0]["id"]

    # Used to display yourself in the friend's navbar.
    loggedInPicture = loggedInUserEntry[0]["profile_pic"]
    loggedInName = loggedInUserEntry[0]["display_name"]
    loggedStatus = loggedInUserEntry[0]["active_stat"] 
 
    friendsList = db(db.dbFriends.friendToWhoID == userNumber).select \
    (orderby=db.dbFriends.display_name).as_list()
    # To see if the button "Unfollow" or "Follow" appears
    isFriend = db((db.dbFriends.friendToWhoID == getIDFromUserTable(session.get("userID")))
                 & (db.dbFriends.userID == userID)).select().as_list()
    if (isFriend != []):
        isFriend=True
    # get the current chosen theme in the db.user, and set 5 varibles to be passed to html
    # [background_bot, background_top, friend_tile, tile_color, text_color]
    theme_colors = return_theme((db.dbUser[getIDFromUserTable(userID)]).chosen_theme)
    dbUserEntry = (db(db.dbUser.userID == userID).select().as_list())
    display_name=dbUserEntry[0]["display_name"]
    bio_status=dbUserEntry[0]["bio_status"]
    return dict(session=session, 
                editable=editable_profile(userID), 
                friendsList=friendsList, 
                profile_pic=profile_pic,
                display_name=display_name,
                bio_status=bio_status,

                loggedInPicture=loggedInPicture,
                loggedInName=loggedInName,
                loggedStatus=loggedStatus,

                background_bot=theme_colors[0],
                background_top=theme_colors[1],
                friend_tile=theme_colors[2],
                tile_color=theme_colors[3],
                text_color=theme_colors[4],

                playlistNames=playlistNames,
                playlistImages=playlistImages,
                playlistURLs=playlistURLs,
                playlistDescriptions=playlistDescriptions,

                userID=userID, 
                isFriend=isFriend, 
                url_signer=url_signer, 
                urlList=urlList, 
                coverList=coverList,
                userBio=URL("userBio", userID), 
                getTopSongs=URL("getTopSongs", userID), 
                getPlaylists=URL("getPlaylists"),
                getTopArtists=URL("getTopArtists", userID), 
                userStat=URL("userStat", session.get("userID")))
        
@action('artists/<userID>', method=['GET'])	
@action.uses('artists.html', session, db)	
def artists_page(userID):	
    profileURL = (URL("user", userID))	
    theme_colors = return_theme((db.dbUser[getIDFromUserTable(userID)]).chosen_theme)	
    dbUserEntry = (db(db.dbUser.userID == userID).select().as_list())	
    display_name=dbUserEntry[0]["display_name"]	
    return dict(session=session, 	
    userID=userID, editable=False,	
    profileURL=profileURL,	
    	
    getTopArtists=URL("getTopArtists", userID),	
    	
    url_signer=url_signer,	
    	
    background_bot=theme_colors[0],	
    background_top=theme_colors[1],	
    friend_tile=theme_colors[2],	
    tile_color=theme_colors[3],	
    text_color=theme_colors[4],	
    user=getUserID(),	
    display_name=display_name)

@action('playlists/<userID>', method=['GET'])	
@action.uses('playlists.html', session, db)	
def playlists_page(userID):	
    profileURL = (URL("user", userID))	
    theme_colors = return_theme((db.dbUser[getIDFromUserTable(userID)]).chosen_theme)	
    dbUserEntry = (db(db.dbUser.userID == userID).select().as_list())	
    	
    display_name=dbUserEntry[0]["display_name"]	
    	
    playlistEntry = (db(db.playlists.playlistsOfWho == getIDFromUserTable(userID)).select().as_list())	
    # Remove this later, is here to make it so accessing users who haven't logged do not crash	
    if playlistEntry == []:	
        playlistNames = []	
        playlistImages = []	
        playlistURLs = []	
        playlistDescriptions = []	
    else:	
        playlistNames = playlistEntry[0]["names"]	
        playlistImages = playlistEntry[0]["images"]	
        playlistURLs = playlistEntry[0]["links"]	
        playlistDescriptions = playlistEntry[0]["descriptions"]	
        	
    return dict(session=session, 	
    userID=userID, editable=False,	
    profileURL=profileURL,	
    	
    getPlaylists=URL("getPlaylists", userID),	
    	
    url_signer=url_signer,	
    	
    playlistNames=playlistNames,	
    playlistImages=playlistImages,	
    playlistURLs=playlistURLs,	
    playlistDescriptions=playlistDescriptions,	
    	
    background_bot=theme_colors[0],	
    background_top=theme_colors[1],	
    friend_tile=theme_colors[2],	
    tile_color=theme_colors[3],	
    text_color=theme_colors[4],	
    user=getUserID(),	
    display_name=display_name)

# -----------------------------------Search Page-------------------------------------

# Many of these functions are split up versions of the old, very large search() function.

# After the user clicks on Edit Profile, this function is called. 
# It displays their banner, the search bar, and results of the search.
@action('user/<userID>/edit', method=["GET", "POST"])
@action.uses('search.html', session)
def editUserSquare(userID):
    profileURL = (URL("user", userID))
    
    # Because search.html extends layout.html, we must return the background colors
    # that layout.html demands.
    theme_colors = return_theme((db.dbUser[getIDFromUserTable(userID)]).chosen_theme)

    return dict(session=session, 
                editable=False, 
                url_signer=url_signer, userID=userID, 
                profileURL=profileURL,
                squares_url = URL('get_squares'),
                search_url = URL('do_search'),
                background_bot=theme_colors[0],
                background_top=theme_colors[1])

# URL to get user's albums
@action('get_squares')
@action.uses(db, session)
def get_squares():
    userID = session.get("userID")
    # Get squares (cover and url) from db
    user_squares = db(db.squares.albumsOfWho == getIDFromUserTable(userID)).select().as_list()
    #print(user_squares)
    coverList = user_squares[0]["coverList"]
    urlList = user_squares[0]["urlList"]
    # Return items for search.js
    return dict(session=session, 
                coverList=coverList, 
                urlList=urlList)

# URL to post new albums to server
@action('get_squares',  method="POST")
@action.uses(db, session)
def save_albums():
    # Get lists from search.js
    coverList = request.json.get('coverList')
    urlList = request.json.get('urlList')
    userID = session.get("userID")

    # Update db
    dbSquareEntry = db(db.squares.albumsOfWho == getIDFromUserTable(userID))
    squareEntries = dbSquareEntry.select().as_list()
    dbSquareEntry.update(coverList=coverList, urlList=urlList)
    return dict(session=session, coverList=coverList, urlList=urlList)

# URL to get Spotify search results
@action('do_search', method=["GET", "POST"])
@action.uses(session)
def do_search():
    # Initialize empty lists
    topAlbums = ""
    topArtists = ""
    imgList = ""
    trackLinks = ""
    artistLinks = ""   
    totalResults = 0
    # Get user input from search.js
    form_SearchValue = request.json.get("input")
    #print("FORM DATA:")
    #print(form_SearchValue)
    # If empty, return empty lists
    if form_SearchValue == "":
        return dict(session=session, topAlbums=topAlbums, topArtists=topArtists, imgList=imgList,
        trackLinks=trackLinks, artistLinks=artistLinks, totalResults=totalResults)
    
    # Get results from Spotify
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect(URL('login'))
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    results = spotify.search(form_SearchValue, type='album', limit=10)
    
    try:
        # If the search results yielded no results, then return nothing. 
        totalResults = results["albums"]["total"]
        if (totalResults == 0):
            return dict(session=session, topAlbums=topAlbums, topArtists=topArtists, imgList=imgList,
            trackLinks=trackLinks, artistLinks=artistLinks, totalResults=totalResults)
        # Else begin to parse the JSON by looking at the albums
        results = results["albums"]
    except:
        #print(results)
        return dict(session=session, topAlbums=topAlbums, topArtists=topArtists, imgList=imgList,
        trackLinks=trackLinks, artistLinks=artistLinks, totalResults=totalResults)

    # Parses through the JSON and returns a list of lists with the information we desire
    biglist = getAlbumResults(results)
    topAlbums = biglist[0]
    topArtists = biglist[1]
    imgList = biglist[2]
    trackLinks = biglist[3]
    artistLinks = biglist[4]
    # Return this information to display
    return dict(session=session, topAlbums=topAlbums, topArtists=topArtists, imgList=imgList,
    trackLinks=trackLinks, artistLinks=artistLinks, totalResults=totalResults)

# -----------------------------------End Search Page-------------------------------------

# Finds the row number of the userID inside of dbUser
def getIDFromUserTable(userID):
    insertedID = (db(db.dbUser.userID == userID).select().as_list())
    if (insertedID is not None) and (insertedID != []):
        return insertedID[0]["id"]
    return None

# When a user tries to see a profile that is not in our database, return this.
@action('userNotFound', method='GET')
@action.uses('userNotFound.html', session)
def userNotFound(userID):
    # Sets the userNotFound page's colors to the user's chosen theme.
    try:
        user_from_table = db.dbUser[getIDFromUserTable(session.get("userID"))]
        theme_colors = return_theme(user_from_table.chosen_theme)
    # If the user has no chosen theme, because they have never logged in or deleted
    # their profile, then the theme will be default.
    except:
        theme_colors = return_theme(0)
    # If the user has never logged in or deleted their profile, the user not found page 
    # will redirect them to the login page.
    loggedInUserEntry = db(db.dbUser.userID == session.get("userID")).select().as_list()
    if (loggedInUserEntry == []):
        return redirect(URL('index'))
    return dict(session=session, 
                editable=False, 
                userID=userID, 
                url_signer=url_signer, 
                background_bot=theme_colors[0], 
                background_top=theme_colors[1])

# When a user tries to see a profile that is not in our database, return this.
@action('nonPremiumUser', method='GET')
@action.uses('nonpremiumuser.html', session)
def nonPremiumUser(userID):
    loggedInUserEntry = db(db.dbUser.userID == session.get("userID")).select().as_list()
    # Sets the nonPremiumUser page's colors to the user's chosen theme.
    try:
        themeColors = return_theme(loggedInUserEntry.chosen_theme)
    # If the user has no chosen theme, because they have never logged in or deleted
    # their profile, then the theme will be default.
    except:
        themeColors = return_theme(0)
    # If the user has never logged in or deleted their profile, the user not found page 
    # will redirect them to the login page.
    if (loggedInUserEntry == []):
        return redirect(URL('index'))
    return dict(session=session, 
                editable=False, 
                userID=userID, 
                url_signer=url_signer, 
                background_bot=themeColors[0], 
                background_top=themeColors[1])

# When a user tries to see a profile that is not in our database, return this.
@action('hostIsNotInSession', method='GET')
@action.uses('hostIsNotInSession.html', session)
def hostIsNotInSession(userID):
    # Sets the nonPremiumUser page's colors to the user's chosen theme.
    try:
        user_from_table = db.dbUser[getIDFromUserTable(session.get("userID"))]
        theme_colors = return_theme(user_from_table.chosen_theme)
    # If the user has no chosen theme, because they have never logged in or deleted
    # their profile, then the theme will be default.
    except:
        theme_colors = return_theme(0)
    # If the user has never logged in or deleted their profile, the user not found page 
    # will redirect them to the login page.
    loggedInUserEntry = db(db.dbUser.userID == session.get("userID")).select().as_list()
    if (loggedInUserEntry == []):
        return redirect(URL('index'))
    return dict(session=session,
                editable=False, 
                userID=userID, 
                url_signer=url_signer, 
                background_bot=theme_colors[0], 
                background_top=theme_colors[1])

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

@action('user/<userID>/<theme_id:int>')
@action.uses(db, session)
def update_theme(userID=None, theme_id=None):
    assert theme_id is not None
    assert userID is not None
    user_data = db.dbUser[getIDFromUserTable(userID)]
    db(db.user_data.id == getIDFromUserTable(userID).update(chosen_theme=theme_id))

    profileURL = "user/" + userID
    redirect(profileURL)
    return dict(session=session)

# Make the spotify API call to get the user playlists
# Also calls parsePlaylistResults() to parse JSON from the API call
@action('getPlaylists')
def getPlaylists():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect(URL('login'))
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    # 14 is an estimate on how long the box is 
    results = spotify.current_user_playlists(limit=50)
    bigList = parsePlaylistResults(results)
    
    return bigList

# Stores the playlists in database tables
def storePlaylists(userID):
    # Function getPlaylists return session and a list containing lists
    # of information about the user's playlists. 
    bigList = getPlaylists()
    playlistNames = bigList[0]
    playlistImages = bigList[1]
    playlistURLs = bigList[2]
    descriptions = bigList[3]

    # Tries to find the entry of the user in the playlist table
    playlistEntry = (db(db.playlists.playlistsOfWho 
                    == getIDFromUserTable(userID)).select().as_list())

    # Is their playlist entry already populated?
    # If it isn't, then the playlists will be inserted
    if (playlistEntry == None) or (playlistEntry == []):
        insertedID = getIDFromUserTable(userID)
        if playlistNames == "":
            playlistNames = []
            playlistImages = []
            playlistURLs = []
            descriptions =[]
        db.playlists.insert(names=playlistNames, images=playlistImages,
                            links=playlistURLs, descriptions=descriptions, 
                            playlistsOfWho=insertedID)
    # If there are already playlists, then update the information
    else:
        insertedID = getIDFromUserTable(userID)
        if playlistNames == "":
            playlistNames = []
            playlistImages = []
            playlistURLs = []
            descriptions = []
        # Finds the correct user entry
        dbRow = db(db.playlists.playlistsOfWho == insertedID)
        dbRow.update(names=playlistNames, images=playlistImages,
                    links=playlistURLs, descriptions=descriptions)
    return 


# UNUSED, but perhaps will be soon
# Gets the information of songs from a search result
def getSearchResults(results):
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

# A slightly different version for specifically albums, higher res images
def getAlbumResults(results):
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
        trackInfo = item['artists'][0]['name']
        icon = item['images'][0]['url']
        trLink = item['external_urls']['spotify']
        artLink = item['artists'][0]['external_urls']['spotify']
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
    if ALinkList == []:
        ALinkList = ""
    # Add all to list to be returned
    BigList.append(TopSongsList)
    BigList.append(TopArtistsList)
    BigList.append(ImgLinkList)
    BigList.append(TLinkList)
    BigList.append(ALinkList)
    # Returned to the user profile
    return BigList  

def parsePlaylistResults(results):
    TopSongsList = []
    descriptionList = []
    #TopArtistsList = []
    ImgLinkList = []
    TLinkList = []
    #ALinkList = []
    BigList = []
    # Clean any potential HTML markings
    unescape = HTMLParser().unescape
    for idx, item in enumerate(results['items']):
        # Get items from correct place in given Spotipy dictionary
        playlistName = item['name']
        playlistName = unescape(playlistName)
        #trackInfo = item['artists'][0]['name']
        #print(item['images'])
        try:
            icon = item['images'][0]['url']
        except:
            icon = "https://bulma.io/images/placeholders/128x128.png"
        trLink = item['external_urls']['spotify']
        description = item['description']
        description = unescape(description)
        #print ("description is ", description, "\n")
        #artLink = item['artists'][0]['external_urls']['spotify']
        TopSongsList.append(playlistName)
        #TopArtistsList.append(trackInfo)
        ImgLinkList.append(icon)
        TLinkList.append(trLink)
        descriptionList.append(description)
        # Done so the descriptionList matches the length of the other lists
        # inside of BigList
        if description == "":
            descriptionList.append([])
        #ALinkList.append(artLink)
    # Avoid empty lists
    if TopSongsList == []:
        TopSongsList = ""
    #if TopArtistsList == []:
        #TopArtistsList= ""
    if ImgLinkList == []:
        ImgLinkList = ""
    if TLinkList == []:
        TLinkList = ""
    #if ALinkList == []:
        #ALinkList = ""
    if descriptionList == []:
        descriptionList = ""
    # Add all to list to be returned
    BigList.append(TopSongsList)
    #BigList.append(TopArtistsList)
    BigList.append(ImgLinkList)
    BigList.append(TLinkList)
    BigList.append(descriptionList)
    #BigList.append(ALinkList)
    # Returned to the user profile
    return BigList  

def getTopTracksFunction(term):
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect(URL('login'))
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    # long_term = all time
    # medium_term = 6 months
    # short_term = 4 weeks
    results = spotify.current_user_top_tracks(limit=50, offset=0, time_range=term)
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
        try:
            icon = item['album']['images'][2]['url']
        except:
            icon = "https://bulma.io/images/placeholders/128x128.png"
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
    if ALinkList == []:
        ALinkList = ""
    # Add all to list to be returned
    BigList.append(TopSongsList)
    BigList.append(TopArtistsList)
    BigList.append(ImgLinkList)
    BigList.append(TLinkList)
    BigList.append(ALinkList)
    # Returned to the user profile
    return BigList

def getTopArtistsFunction(term):
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect(URL('login'))
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    # long_term = all time
    # medium_term = 6 months
    # short_term = 4 weeks
    results = spotify.current_user_top_artists(limit=50, offset=0, time_range=term)    
    TopArtistsList = []
    ImgLinkList = []
    TLinkList = []
    ALinkList = []
    GenreList = []
    FollowersList = []
    BigList = []

    for idx, item in enumerate(results['items']):
        # Get items from correct place in given Spotipy dictionary
        artist = item['name']
        #print (artist)
        TopArtistsList.append(artist)
        try:
            icon = item['images'][2]['url']
        except:
            icon = "https://bulma.io/images/placeholders/128x128.png"
        ImgLinkList.append(icon)
        artistLink = item['external_urls']['spotify']
        ALinkList.append(artistLink)
        GenreList.append(item['genres'])
        # Adds command between thousands to make more readable
        followers = "{:,}".format(item['followers']['total'])
        
        #print (followers)
        FollowersList.append(followers)

    if TopArtistsList == []:
        TopArtistsList= ""
    if ImgLinkList == []:
        ImgLinkList = ""
    if ALinkList == []:
        ALinkList = ""
    if GenreList == []:
        GenreList = ""
    if FollowersList == []:
        FollowersList = ""
    # Add all to list to be returned
    BigList.append(TopArtistsList)
    BigList.append(ImgLinkList)
    BigList.append(ALinkList)
    BigList.append(GenreList)
    BigList.append(FollowersList)

    # Returned to the user profile
    return BigList

# Gives the amount of time between API calls. 
# Hidden in controllers.py so users cannot edit the value in their 
# javascript files.
@action('getAPICallTime', method=["GET"])
@action.uses(session)
def getAPICallTime():
    getAPICallTime = 4
    return dict(getAPICallTime=getAPICallTime)

# Returns the deviceID where the user is running Spotify. 
@action('getDevice', method=["GET"])
@action.uses(session)
def getDevice():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect(URL('login'))
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    try:
        results = spotify.devices()
        deviceID = results["devices"][0]["id"]
    except:
        deviceID = ""
    return dict(deviceID=deviceID)

@action('isGroupSessionHost/<userID>', method=["GET"])
@action.uses(session)
def isGroupSessionHost(userID=None):
    isHost = False
    if (session.get("userID") == userID):
        isHost = True
        print ("This person is the host")
    return dict(isHost=isHost)

@action('pauseOrPlayTrack/<userID>/<deviceID>', method=["GET"])
@action.uses(session)
def pauseOrPlayTrack(userID=None, deviceID=None):
    isPlaying = request.params.get('content')
    print("isPlaying = ", isPlaying)
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect(URL('login'))
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    if (isPlaying == "false"):
        spotify.pause_playback(deviceID)
    # If host, resume with function that checks what song you are playing.
    # Playing a track is MUCH more expensive than pausing a track
    else:
        #dbGroupSessionEntry = (db(db.groupSession.userID == userID).select().as_list())
        #timeWhenCallWasMade=dbGroupSessionEntry[0]["timeWhenCallWasMade"]
        #trackURI=dbGroupSessionEntry[0]["trackURI"]
        #trackNumber=dbGroupSessionEntry[0]["trackNumber"]
        #trackNumber = {"position": trackNumber}
        #curPosition=dbGroupSessionEntry[0]["curPosition"]
        #if ((trackURI != "") and (deviceID != "")):
            #spotify.start_playback(deviceID, trackURI, None, trackNumber, curPosition)
        if (deviceID != ""):
            spotify.start_playback(deviceID)
        #return getCurrentPlaying(userID)
    # If visitor, resume with function that checks what song the host is playing.
    #else:
        #print("is visitor")
        #synchronizeVisitor(userID, deviceID)
    return

@action('groupSession/<userID>')
@action.uses(db, auth, 'groupSession.html', session)
def groupSession(userID=None):
    # Makes user log in if they go to a group session link and have not logged in yet
    if (session.get("userID") == None):
        return redirect(URL('login'))
    try:
        # Getting the user table entry of the person calling this function. 
        loggedInProfileEntry = db(db.dbUser.userID == session.get("userID")).select().as_list()
        premiumStatus = loggedInProfileEntry[0]["premiumStatus"]
    except:
        return redirect(URL('login'))

    #if (premiumStatus != "premium"):
        #return nonPremiumUser(session.get("userID"))

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect(URL('login'))
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    # Try to get the deviceID of the instance of Spotify the user is listening on.
    try:
        results = spotify.devices()
        deviceID = results["devices"][0]["id"]
    except:
        deviceID = ""

    dbGroupSessionEntry = db(db.groupSession.userID == userID).select().as_list()
    # Creating the table for groupSession if it does not exist
    if ((dbGroupSessionEntry == None) or (dbGroupSessionEntry == [])):
        insertedID = getIDFromUserTable(userID)
        db.groupSession.insert(userID=userID, trackURI="", imageURL="", trackName="", 
        artistName = "", curPosition="", trackLength="", isPlaying=False,
        timeWhenCallWasMade=0, deviceID=deviceID, trackNumber="", groupSessionOfWho=insertedID)
        dbGroupSessionEntry = db(db.groupSession.userID == userID).select().as_list()

    dbGroupSessionPeople = db(db.groupSessionPeople.groupSessionReference 
                        == dbGroupSessionEntry[0]["id"]).select().as_list()
    loggedInProfilePicture = loggedInProfileEntry[0]["profile_pic"]
    # Stating that the user has no profile pic. A no profile icon is given to the user 
    # in groupSession.html
    if loggedInProfilePicture == "":
        loggedInProfilePicture = "no profile"
    loggedInUserID = loggedInProfileEntry[0]["userID"]
    loggedInUserDisplayName = loggedInProfileEntry[0]["display_name"]
    
    timeWhenCallWasMade =  time.time()
    print("timeWhenCallWasMade = ", timeWhenCallWasMade)

    
    # If the host doesn't have a group session people table, then create one and add the host user.
    if ((dbGroupSessionPeople == None) or (dbGroupSessionPeople == [])):
        # If it is a visitor creating the table, then the host is not on the page and therefore
        # the user should go to a page telling them the host is not online. 
        if (session.get("userID") != userID):
            return hostIsNotInSession(session.get("userID"))
        GroupSessionPeopleID = db.groupSessionPeople.insert(displayNames=[loggedInUserDisplayName],
                                    profilePictures=[loggedInProfilePicture],
                                    userIDs=[loggedInUserID], 
                                    timeLastActive=[timeWhenCallWasMade],
                                    groupSessionPeopleOfWho=loggedInProfileEntry[0]["id"],
                                    groupSessionReference=dbGroupSessionEntry[0]["id"])
    else:
        GroupSessionPeopleID = dbGroupSessionPeople[0]["id"]
        displayNames = dbGroupSessionPeople[0]["displayNames"]
        userIDs = dbGroupSessionPeople[0]["userIDs"]
        profilePictures = dbGroupSessionPeople[0]["profilePictures"]
        timeLastActive = dbGroupSessionPeople[0]["timeLastActive"]
        ownerOfTableEntry = db(db.dbUser.userID == userID).select().as_list()
        ownerID = ownerOfTableEntry[0]["userID"]
        # Checking to see if the host is in the session,
        # if not, do not let the visitor in the session.
        if (ownerID not in userIDs) and (loggedInUserID != ownerID):
            return hostIsNotInSession(session.get("userID"))
        elif loggedInUserID not in userIDs:
            displayNames.append(loggedInUserDisplayName)
            userIDs.append(loggedInUserID)
            profilePictures.append(loggedInProfilePicture)
            timeLastActive.append(timeWhenCallWasMade)
            # dbGroupSessionPeople is currently a list, the next line of code converts it
            # back to a database entry.
            dbGroupSessionPeople = db(db.groupSessionPeople.groupSessionReference 
                                == dbGroupSessionEntry[0]["id"])
            dbGroupSessionPeople.update(displayNames=displayNames, profilePictures=profilePictures,
                                        userIDs=userIDs, timeLastActive=timeLastActive)

    queues = db(db.queue.queueOfWho == userID).select().as_list()
    queueImage=""
    queueURL=""
    if queues != []:
        queueImage = queues[0]["queueListImage"]
        queueURL = queues[0]["queueListURL"]  
    
    profileURL = "http://shams.pythonanywhere.com"+(URL("groupSession", userID))

    dbUserEntry = (db(db.dbUser.userID == userID).select().as_list())
    host_name=dbUserEntry[0]["display_name"]


    if userID is not None:
        try:
            user_from_table = db.dbUser[getIDFromUserTable(session.get("userID"))]
            theme_colors = return_theme(user_from_table.chosen_theme)
        except:
            theme_colors = return_theme(0)
        return dict(session=session, 
                    editable=False,
                    background_bot=theme_colors[0],
                    background_top=theme_colors[1], 
                    profileURL = profileURL,
                    host_name=host_name, 
                    currentPlaying=URL("currentPlaying", userID),
                    squares_url = URL('get_squares'),
                    search_url = URL('group_search', userID), 
                    getAPICallTime = URL('getAPICallTime'),
                    isGroupSessionHost=URL("isGroupSessionHost", userID), 
                    synchronizeVisitor=URL("synchronizeVisitor", userID, deviceID),
                    pauseOrPlayTrack=URL("pauseOrPlayTrack", userID, deviceID),
                    getPeopleInSession=URL("getPeopleInSession", 
                                            GroupSessionPeopleID, loggedInUserID),
                    removePeopleInSession=URL("removePeopleInSession", 
                                           GroupSessionPeopleID, loggedInUserID),                    
                    shouldSynchronizeVisitor=URL("shouldSynchronizeVisitor", userID),
                    refreshGroupSession=URL("groupSession", userID),
                    getDevice=URL('getDevice'),
                    queueImage=queueImage,
                    queueURL=queueURL)
    else:
        return dict(session=session, 
                    editable=False, 
                    background_bot=None, 
                    background_top=None, 
                    profileURL = profileURL, 
                    host_name=host_name,
                    currentPlaying=URL("currentPlaying", userID),
                    squares_url = URL('get_squares'),
                    search_url = URL('group_search', userID), 
                    getAPICallTime = URL('getAPICallTime'),
                    isGroupSessionHost=URL("isGroupSessionHost", userID), 
                    synchronizeVisitor=URL("synchronizeVisitor", userID, deviceID),
                    pauseOrPlayTrack=URL("pauseOrPlayTrack", userID, deviceID),
                    getPeopleInSession=URL("getPeopleInSession", 
                                            GroupSessionPeopleID, loggedInUserID),
                    removePeopleInSession=URL("removePeopleInSession", 
                                            GroupSessionPeopleID, loggedInUserID),
                    shouldSynchronizeVisitor=URL("shouldSynchronizeVisitor", userID),
                    refreshGroupSession=URL("groupSession", userID),
                    getDevice=URL('getDevice'),
                    queueImage=queueImage,
                    queueURL=queueURL)

# Function that hosts run in groupSession
# Finds what song the host is listening to by making a Spotify API call
# Then updates the song information in the host's groupSession table in the database.
@action('currentPlaying/<userID>', method=["GET"])
@action.uses(session)
def getCurrentPlaying(userID=None):
    if (session.get("userID") != userID):
        return
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        print("ok epic 2")
        return redirect(URL('login'))
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    results = spotify.current_playback()
    try:
        deviceID = results["device"]["id"]
        item = results["item"]
        trackName = item["name"]
        artistName = item["album"]["artists"][0]["name"]
        isLocal = item["is_local"]
        trackURI = item["album"]["uri"]
        trackNumber = item["track_number"]
        # Album tracks start at index 0, but Spotify returns a value that starts at 1.
        trackNumber -= 1
        curPosition = results["progress_ms"]
        isPlaying = results["is_playing"]
        trackLength = item["duration_ms"]
    except:
        trackName = "None"
        isLocal = "False"
        artistName = "None"
        trackURI = ""
        curPosition = ""
        trackLength = ""
        isPlaying = "false"
        deviceID = ""
        trackNumber= ""
    # If song is None or has no image, put placeholder.
    try:
        imageURL = results["item"]["album"]["images"][1]["url"]
    except:
        imageURL = "https://i.pinimg.com/564x/74/b0/b4/74b0b4e5436c31adebdf7c5acbcac7dc.jpg"

    try:
        dbGroupSessionEntry = (db(db.groupSession.userID == userID))
    except:
        return dict(userID=userID, 
        trackName=trackName, 
        isLocal=isLocal, 
        artistName=artistName, 
        imageURL=imageURL, 
        trackURI=trackURI, 
        curPosition=curPosition, 
        trackLength=trackLength,
        isPlaying=isPlaying, 
        deviceID=deviceID, 
        trackNumber=trackNumber)

    now = datetime.now().time()
    timeWhenCallWasMade = int(now.strftime("%S")) + float("." + now.strftime("%f"))
    dbGroupSessionEntry.update(trackURI=trackURI, 
                               imageURL=imageURL,
                               trackName=trackName,
                               artistName=artistName,
                               curPosition=curPosition,
                               trackLength=trackLength,
                               isPlaying=isPlaying,
                               trackNumber=trackNumber,
                               timeWhenCallWasMade=timeWhenCallWasMade)

    # Returns these variables to update the information on groupSession page.
    return dict(userID=userID, 
                trackName=trackName, 
                isLocal=isLocal, 
                artistName=artistName, 
                imageURL=imageURL, 
                trackURI=trackURI, 
                curPosition=curPosition, 
                trackLength=trackLength,
                isPlaying=isPlaying, 
                deviceID=deviceID, 
                trackNumber=trackNumber,
                timeWhenCallWasMade=timeWhenCallWasMade)

@action('shouldSynchronizeVisitor/<userID>/', method=["GET"])
@action.uses(session)
def shouldSynchronizeVisitor(userID=None):
    dbGroupSessionEntry = (db(db.groupSession.userID == userID).select().as_list())
    timeWhenCallWasMade=dbGroupSessionEntry[0]["timeWhenCallWasMade"]
    return dict(timeWhenCallWasMade=timeWhenCallWasMade)

# Function that visitors run in groupSession
@action('synchronizeVisitor/<userID>/<deviceID>', method=["GET"])
@action.uses(session)
def synchronizeVisitor(userID=None, deviceID=None):
    dbGroupSessionEntry = (db(db.groupSession.userID == userID).select().as_list())
    if (dbGroupSessionEntry == []):
        print ("No groupSession table exists for ", userID)
        return dict(session=session)
    trackURI=dbGroupSessionEntry[0]["trackURI"]
    trackName=dbGroupSessionEntry[0]["trackName"]
    artistName=dbGroupSessionEntry[0]["artistName"]
    imageURL=dbGroupSessionEntry[0]["imageURL"]
    curPosition=dbGroupSessionEntry[0]["curPosition"]
    trackLength=dbGroupSessionEntry[0]["trackLength"]
    isPlaying=dbGroupSessionEntry[0]["isPlaying"]
    trackNumber=dbGroupSessionEntry[0]["trackNumber"]

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect(URL('login'))
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    # If host is playing the song, then play it. If it is paused, do not.
    if (isPlaying == True):
        try:
            # offset must be {“position”: <int>} or {“uri”: “<track uri>”}
            trackNumber = {"position": trackNumber}
            spotify.start_playback(deviceID, trackURI, None, trackNumber, curPosition)
        except:
            print ("Could not start playack")

    # elif statement to check whether or not playback should be paused.
    # This is to prevent visitors from hitting the synch button and having the song 
    # play when it should be paused. 
    #
    # Very expensive (2 API Calls if the visitor is playing a song), 
    # but synch button will probably not be hit but users too often. 
    elif (isPlaying == False and deviceID != None):
        # One call to the Spotify API to check if the visitor is currently playing a song.
        results = spotify.current_playback()
        try:
            if (results["is_playing"] == True):
                spotify.pause_playback(deviceID)
        except:
            print("User is not playing anything")

    # Returns these variable to update information on visitor's page.
    return dict(session=session, 
                trackName=trackName, 
                artistName=artistName, 
                imageURL=imageURL, 
                trackURI=trackURI, 
                curPosition=curPosition, 
                trackLength=trackLength,
                isPlaying=isPlaying)

# Retrieves the names and profile picture links of the people in the group session.
@action('getPeopleInSession/<groupSessionPeopleID>/<userID>', method=["GET"])
@action.uses(session)
def getPeopleInSession(groupSessionPeopleID=None, userID=None):
    print("in getPeopleInSession ")
    dbGroupSessionPeople = db(db.groupSessionPeople.id == groupSessionPeopleID).select().as_list()
    displayNames = dbGroupSessionPeople[0]["displayNames"]
    userIDs = dbGroupSessionPeople[0]["userIDs"]
    profilePictures = dbGroupSessionPeople[0]["profilePictures"]
    ownerOfTableEntry = db(db.dbUser.id == 
                        dbGroupSessionPeople[0]["groupSessionPeopleOfWho"]).select().as_list()
    ownerID = ownerOfTableEntry[0]["userID"]
    # Checking to see if the host is in the session,
    # if not, do not let the visitor in the session.
    redirect = False
    if (ownerID not in userIDs):
        print("Host is not here")
        redirect = True
    timeLastActive = dbGroupSessionPeople[0]["timeLastActive"]
    # Everytime the user asks for the people in the session, they are shown to be active, and
    # have the time ince they are last active updated.
    if userID in dbGroupSessionPeople[0]["userIDs"]:
        updateIndex = dbGroupSessionPeople[0]["userIDs"].index(userID)
        timeLastActive[updateIndex] = time.time()
        dbGroupSessionPeople = db(db.groupSessionPeople.id == groupSessionPeopleID)
        dbGroupSessionPeople.update(timeLastActive=timeLastActive)
    return dict(session=session, 
                displayNames=displayNames,
                profilePictures=profilePictures,
                redirect=redirect)

@action('removePeopleInSession/<groupSessionPeopleID>/<userID>', method=["POST"])
@action.uses(session)
def removePeopleInSession(groupSessionPeopleID=None, userID=None):
    print("in removePeopleInSession ")
    dbGroupSessionPeople = db(db.groupSessionPeople.id == groupSessionPeopleID).select().as_list()
    displayNames = dbGroupSessionPeople[0]["displayNames"]
    profilePictures = dbGroupSessionPeople[0]["profilePictures"]
    userIDs = dbGroupSessionPeople[0]["userIDs"]
    timeLastActive = dbGroupSessionPeople[0]["timeLastActive"]
    print("before, displayNames are ", displayNames)
    print("before, profilePictures are ", profilePictures)
    if userID in dbGroupSessionPeople[0]["userIDs"]:
        removalIndex = dbGroupSessionPeople[0]["userIDs"].index(userID)
        del userIDs[removalIndex]
        del displayNames[removalIndex]
        del profilePictures[removalIndex]
        del timeLastActive[removalIndex]
        dbGroupSessionPeople = db(db.groupSessionPeople.id == groupSessionPeopleID)
        dbGroupSessionPeople.update(displayNames=displayNames, profilePictures=profilePictures,
                                    userIDs=userIDs, timeLastActive=timeLastActive)
    print("after, displayNames are ", displayNames)
    print("after, profilePictures are ", profilePictures)
    return dict(session=session)

#Search element for group session
@action('group_search/<userID>', method=["GET", "POST"])
@action.uses(session)
def group_search(userID=None):
    # Initialize empty lists
    queueListImage = ""
    queueListURL = ""
    topTracks = ""
    topArtists = ""
    imgList = ""
    trackLinks = ""
    artistLinks = ""  
    totalResults = 0
    queues = ""
    queueImage=""
    queueURL=""
    # Get user input from search.js
    form_SearchValue = request.json.get("input2")

    if request.method == "POST":
        print('posty posty')
        queueListImage = request.json.get('queueListImage')
        queueListURL = request.json.get('queueListURL')

        if queueListImage and queueListURL:
            print(queueListImage)
            print(queueListURL)
            print("")

            entries = db(db.queue.queueOfWho == userID).select().as_list()
            #print(entries)
            # try to insert the list of songs into the database 
            if entries != []:
                    db(db.queue.queueOfWho == userID).update(
                        queueOfWho=userID,
                        queueListImage=queueListImage,
                        queueListURL=queueListURL,
                    )
            else:
                db.queue.insert(
                    queueOfWho=userID,
                    queueListImage=queueListImage,
                    queueListURL=queueListURL,
                )
            #entries = db(db.queue.queueOfWho == getUserID()).select().as_list()
            #print(queues)
    queues = db(db.queue.queueOfWho == userID).select().as_list()
    print(queues)
    if queues != []:
        queueImage = queues[0]["queueListImage"]
        queueURL = queues[0]["queueListURL"]      
    
    # If empty, return empty lists
    if form_SearchValue == "" or form_SearchValue == None:
        return dict(session=session, 
                    topTracks=topTracks, 
                    topArtists=topArtists, 
                    imgList=imgList, 
                    queues=queues,
                    trackLinks=trackLinks, 
                    artistLinks=artistLinks, 
                    totalResults=totalResults, 
                    queueListImage=queueListImage, 
                    queueListURL=queueListURL,
                    queueImage=queueImage,
                    queueURL=queueURL)
    
    
    # Get results from Spotify
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('login')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    results = spotify.search(form_SearchValue, type='track', limit=10)
    #print(results)
    try:
        # If the search results yielded no results, then return nothing.
        totalResults = results["tracks"]["total"]
        if (totalResults == 0):
            return dict(session=session, 
                        topTracks=topTracks, 
                        topArtists=topArtists, 
                        imgList=imgList,
                        trackLinks=trackLinks, 
                        artistLinks=artistLinks, 
                        totalResults=totalResults, 
                        queues=queues,
                        queueListImage=queueListImage, 
                        queueListURL=queueListURL,
                        queueImage=queueImage,
                        queueURL=queueURL)
        # Else begin to parse the JSON by looking at the albums
        results = results["tracks"]
    except:
        #print(results)
        return dict(session=session, 
                    topTracks=topTracks, 
                    topArtists=topArtists, 
                    imgList=imgList,
                    trackLinks=trackLinks, 
                    artistLinks=artistLinks, 
                    totalResults=totalResults,
                    queues=queues,
                    queueListImage=queueListImage, 
                    queueListURL=queueListURL,
                    queueImage=queueImage,
                    queueURL=queueURL)
    # Parses through the JSON and returns a list of lists with the information we desire
    biglist = getSearchResults(results)
    topTracks = biglist[0]
    topArtists = biglist[1]
    imgList = biglist[2]
    trackLinks = biglist[3]
    artistLinks = biglist[4]
    queueListImage = biglist[2]
    queueListURL = biglist[0]
    # Return this information to display
    return dict(session=session, 
                topTracks=topTracks, 
                topArtists=topArtists, 
                imgList=imgList,
                trackLinks=trackLinks, 
                artistLinks=artistLinks, 
                totalResults=totalResults, 
                queues=queues,
                queueListImage=queueListImage, 
                queueListURL=queueListURL,
                queueImage=queueImage,
                queueURL=queueURL)

@action('settings/<userID>')
@action.uses(db, auth, 'settings.html', session)
def getSettings(userID=None):
    profileURL = "http://shams.pythonanywhere.com"+(URL("user", userID))
    currentProfileEntry = db(db.dbUser.userID == userID).select().as_list()
    profile_pic = ""
    if (currentProfileEntry != None) and (currentProfileEntry != []):
       # Setting the top tracks and profile pic variables
       profile_pic = currentProfileEntry[0]["profile_pic"]
    if userID is not None:
        user_from_table = db.dbUser[getIDFromUserTable(session.get("userID"))]
        theme_colors = return_theme(user_from_table.chosen_theme)
        return dict(session=session, 
                    editable=False, 
                    userID=userID, 
                    url_signer=url_signer,
                    background_bot=theme_colors[0],
                    background_top=theme_colors[1],
                    profile_pic=profile_pic, 
                    profileURL = profileURL)
    else:
        return dict(session=session, 
                    editable=False, 
                    userID=userID, 
                    url_signer=url_signer,
                    background_bot=None, 
                    background_top=None,
                    profile_pic=profile_pic, 
                    profileURL=profileURL)

@action('deleteProfile/<userID>', method=['GET'])
@action.uses(session, db)
def delete_profile(userID=None):
    assert userID is not None
    db(db.dbUser.userID == userID).delete()
    db(db.dbFriends.userID == userID).delete()
    os.remove(session_cache_path())
    session.clear()
    redirect(URL('index'))

@action('add_friend', method=["GET", "POST"])
@action.uses(db, auth, 'add_friend.html', session)
def addFriend():
    loggedInUserEntry = db(db.dbUser.userID == session.get("userID")).select().as_list()
    userNumber = loggedInUserEntry[0]["id"]

    # [background_bot, background_top, friend_tile, tile_color, text_color]
    theme_colors = return_theme((db.dbUser[getIDFromUserTable(session.get("userID"))]).chosen_theme)
    # get database of all db users
    allusers = db(db.dbUser).select(orderby=db.dbUser.display_name).as_list()
    friendsList = db(db.dbFriends.friendToWhoID == userNumber) \
    .select(orderby=db.dbFriends.display_name).as_list()

    friend_ids = []
    for frand in friendsList:
        print(frand["display_name"])
        friend_ids.append(frand["userID"])
    # print(friend_ids)   
    if request.method == "GET":
        return dict(
            session=session, 
            editable=False, 
            nullError=False, 
            alreadyFriend=False, 
            CannotAddSelf=False, 
            background_bot=theme_colors[0], 
            background_top=theme_colors[1],
            friend_tile=theme_colors[2],
            tile_color=theme_colors[3],
            text_color=theme_colors[4],
            allusers = allusers,
            friendsList=friendsList,
            friend_ids=friend_ids,
            )

    else:
        loggedInUserId = session.get("userID")
        form_userID = request.params.get("userID")
        dbUserEntry = (db(db.dbUser.userID == form_userID).select().as_list())
        if dbUserEntry == []:
            return dict(
                session=session, 
                editable=False, 
                nullError=True, 
                alreadyFriend=False, 
                CannotAddSelf=False, 
                background_bot=theme_colors[0], 
                background_top=theme_colors[1],
                friend_tile=theme_colors[2],
                tile_color=theme_colors[3],
                text_color=theme_colors[4],
                allusers = allusers,
                friendsList=friendsList,
                friend_ids=friend_ids,
                )
        if (checkIfFriendDuplicate(form_userID)):
            return dict(
                session=session, 
                editable=False, 
                nullError=False, 
                alreadyFriend=True, 
                CannotAddSelf=False, 
                background_bot=theme_colors[0], 
                background_top=theme_colors[1],
                friend_tile=theme_colors[2],
                tile_color=theme_colors[3],
                text_color=theme_colors[4],
                allusers = allusers,
                friendsList=friendsList,
                friend_ids=friend_ids,
                )
        if (form_userID == loggedInUserId):
            return dict(
                session=session, 
                editable=False, 
                nullError=False, 
                alreadyFriend=False, 
                CannotAddSelf=True, 
                background_bot=theme_colors[0], 
                background_top=theme_colors[1],
                friend_tile=theme_colors[2],
                tile_color=theme_colors[3],
                text_color=theme_colors[4],
                allusers = allusers,
                friendsList=friendsList,
                friend_ids=friend_ids,
                )

        db.dbFriends.insert(
                userID=form_userID, 
                friendToWhoID=getIDFromUserTable(loggedInUserId), 
                profile_pic=dbUserEntry[0]["profile_pic"], 
                display_name=dbUserEntry[0]["display_name"], 
                bio_status=dbUserEntry[0]["bio_status"], 
                active_stat=dbUserEntry[0]["active_stat"]
            )
        return redirect(URL('add_friend'))

@action('addFriendFromProfile/<userID>', method=["GET"])
@action.uses(db, session)
def addFriendFromProfile(userID=None):
    loggedInUserId = session.get("userID")
    if (loggedInUserId == None) or (loggedInUserId == ""):
        return redirect(URL('index'))
    dbUserEntry = (db(db.dbUser.userID == userID).select().as_list())
    if dbUserEntry == []:
        return redirect(URL('user', userID))
    if (checkIfFriendDuplicate(userID)):
        return redirect(URL('user', userID))
    if (userID == loggedInUserId):
        return redirect(URL('user', userID))
    db.dbFriends.insert(userID=userID, 
                        friendToWhoID=getIDFromUserTable(loggedInUserId), 
                        profile_pic=dbUserEntry[0]["profile_pic"], 
                        display_name=dbUserEntry[0]["display_name"], 
                        bio_status=dbUserEntry[0]["bio_status"],
                         active_stat=dbUserEntry[0]["active_stat"])
    return redirect(URL('user', userID))

@action('unfollowProfile/<userID>', method=['GET'])
@action.uses(session, db)
def deleteFriend(userID=None):
    person = db((db.dbFriends.userID == userID) & (db.dbFriends.friendToWhoID == getIDFromUserTable(session.get("userID")))).select().as_list()
    if person is None or person == []:
        # Nothing to edit.  This should happen only if you tamper manually with the URL.
        return redirect(URL('add_friend'))
    else:
        person = person[0]
        friendToWhoID = person["friendToWhoID"]
        if friendToWhoID == getIDFromUserTable(session.get("userID")):
            db(db.dbFriends.id == person["id"]).delete()
            return redirect(URL('add_friend'))

@action('unfollowProfileFromProfile/<userID>', method=['GET'])
@action.uses(session, db)
def deleteFriend(userID=None):
    person = db((db.dbFriends.userID == userID) & 
    (db.dbFriends.friendToWhoID == getIDFromUserTable(session.get("userID")))).select().as_list()
    if person is None or person == []:
        # Nothing to edit.  This should happen only if you tamper manually with the URL.
        return redirect(URL('user', userID))
    else:
        person = person[0]
        friendToWhoID = person["friendToWhoID"]
        if friendToWhoID == getIDFromUserTable(session.get("userID")):
            db(db.dbFriends.id == person["id"]).delete()
            return redirect(URL('user', userID))

# Function used by seeTerm() in user.js to extract the top song information
# from the correct table in the database. 
@action('getTopSongs/<userID>', method=["GET"])
@action.uses(session)
def getTopSongs(userID=None):
    # Finds the value of the term chosen by the user. 
    # This "term" is about what period of top songs to display on 
    # a user's profile.

    # This is populated if a person who is not the owner wants to see a different term
    term = request.params.get('term')
    #print ("1term is ", term)

    # This is populated if by default
    if term == None:
        term = (db.dbUser[getIDFromUserTable(userID)]).chosen_term    # Obtains the whole entry of the user in the correct table.
    #print ("term is ", term)
    # Also sets the term string to display on the dropdown menu.
    if term == '1':	
        term_str = 'last 4 weeks'	
        termList = db(db.shortTerm.topTracksOfWho == getIDFromUserTable(userID)).select().as_list()	
    elif term == '2':	
        term_str = 'last 6 months'	
        termList = db(db.mediumTerm.topTracksOfWho == getIDFromUserTable(userID)).select().as_list()	
    elif term == '3':	
        term_str = 'of all time'	
        termList = db(db.longTerm.topTracksOfWho == getIDFromUserTable(userID)).select().as_list()	
    else:	
        term_str = 'last 4 weeks'	
        termList = db(db.shortTerm.topTracksOfWho == getIDFromUserTable(userID)).select().as_list()

    # Get the fields from the termList, but only if they have a reference in it 
    if termList != []:
        topTracks = termList[0]["topTracks"]
        topArtists = termList[0]["topArtists"]
        imgList = termList[0]["imgList"]
        trackLinks = termList[0]["trackLinks"]
        artistLinks = termList[0]["artistLinks"]

    # This handles if a user hasn't listened to any songs or has less than 10 songs listened to.
    if (topTracks == None) or len(topTracks) < 10:
        fillerTopTracks = ["", "",  "",  "", "", "",  "",  "", "",  "",  ""]
        topTracks = fillerTopTracks
        topArtists = fillerTopTracks
        imgList = fillerTopTracks
        trackLinks = fillerTopTracks
        artistLinks = fillerTopTracks

    return dict(term_str=term_str, topTracks=topTracks, topArtists=topArtists,
    imgList=imgList, trackLinks=trackLinks, artistLinks=artistLinks, session=session)

# NEEDS SECURITY CHECK
# Changes the chosen term for top tracks of the user. Posts the change
# immediately to the user page
@action('getTopSongs/<userID>', method=["POST"])
@action.uses(session)
def getTopSongsPost(userID=None):
    # Gets the term selected by the user, which is currently in user.js 
    # in the changeTerm() function
    term = request.params.get('term')
    #print("postTerm ", term)
    db(db.dbUser.id == getIDFromUserTable(userID)).update(chosen_term=term)	
    return dict(session=session)	

# Function used by seeTerm() in user.js to extract the top song information
# from the correct table in the database. 
@action('getTopArtists/<userID>', method=["GET"])
@action.uses(session)
def getTopArtists(userID=None):
    # Finds the value of the term chosen by the user. 
    # This "term" is about what period of top songs to display on 
    # a user's profile.
    
    # This is populated if a person who is not the owner wants to see a different term
    term = request.params.get('term')
    # This is populated if by default
    if term == None:
        term = (db.dbUser[getIDFromUserTable(userID)]).artist_term
    #print("term is ", term)
    # Obtains the whole entry of the user in the correct table.
    # Also sets the term string to display on the dropdown menu.
    if term == '1':	
        term_str = 'last 4 weeks'	
        termList = db(db.shortArtists.topArtistsOfWho == getIDFromUserTable(userID)).select().as_list()	
    elif term == '2':	
        term_str = 'last 6 months'	
        termList = db(db.mediumArtists.topArtistsOfWho == getIDFromUserTable(userID)).select().as_list()	
    elif term == '3':	
        term_str = 'of all time'	
        termList = db(db.longArtists.topArtistsOfWho == getIDFromUserTable(userID)).select().as_list()	
    else:	
        term_str = 'last 4 weeks'	
        termList = db(db.shortArtists.topArtistsOfWho == getIDFromUserTable(userID)).select().as_list()

    # Get the fields from the termList, but only if they have a reference in it 
    if termList != []:
        topArtists = termList[0]["topArtists"]
        imgList = termList[0]["imgList"]
        artistLinks = termList[0]["artistLinks"]
        genres = termList[0]["genres"]
        followers = termList[0]["followers"]

    # This handles if a user hasn't listened to any songs or has less than 10 songs listened to.
    if (topArtists == None) or len(topArtists) < 5:
        fillerTopArtists = ["", "",  "",  "", ""]
        topArtists = fillerTopArtists
        imgList = fillerTopArtists
        artistLinks = fillerTopArtists
        genres = [[""], [""], [""], [""], [""]]
        followers = fillerTopArtists

    return dict(term_str=term_str, topArtists=topArtists, imgList=imgList,
    artistLinks=artistLinks, genres=genres, followers=followers, session=session)

# NEEDS SECURITY CHECK
# Changes the chosen term for top tracks of the user. Posts the change
# immediately to the user page
@action('getTopArtists/<userID>', method=["POST"])
@action.uses(session)
def getTopArtistsPost(userID=None):
    # Gets the term selected by the user, which is currently in user.js 
    # in the changeTerm() function
    term = request.params.get('term')
    db(db.dbUser.id == getIDFromUserTable(userID)).update(artist_term=term)	
    return dict(session=session)	

# Retrieves the bio of the user, used in user.js to display the bio
@action('userBio/<userID>', method=["GET"])
@action.uses(session)
def getUserBio(userID=None):
    currentProfileEntry = db(db.dbUser.userID == userID).select().as_list()
    return dict(session=session, userBio=currentProfileEntry[0]["bio_status"])

# Makes a request to user.js for the content in the text area after a user hits the save button
# Then updates the bio in the database
# ASH: WARNING -- MAY BE UNSAFE/EDITABLE BY OTHERS -- NEEDS TESTING
@action('userBio/<userID>', method=["POST"])
@action.uses(session)
def postUserBio(userID=None):
    dbBioEntry = db(db.dbUser.userID == userID)
    content = request.params.get('content')
    dbBioEntry.update(bio_status=content)
    return dict(session=session, 
                content=content)

# Retrieves the status of the user, used in user.js to display the bio
@action('userStat/<userID>', method=["GET"])
@action.uses(session)
def getUserStat(userID=None):
    currentProfileEntry = db(db.dbUser.userID == userID).select().as_list()
    return dict(session=session, 
                userStat=currentProfileEntry[0]["active_stat"])

# Makes a request to user.js for the content in the text area after a user hits the save button
# Then updates the bio in the database
@action('userStat/<userID>', method=["POST"])
@action.uses(session)
def postUserStat(userID=None):
    dbStatEntry = db(db.dbUser.userID == userID)
    content = request.params.get('content')
    dbStatEntry.update(active_stat=content)

    # This takes all the instances of the logged in user in the friends database. 	
    # This is so we can update their information.
    friendsEntries = (db(db.dbFriends.userID == userID).select().as_list())

    # Updates the information in friends database so the friends NAV bar is up to date. 
    if (friendsEntries != None) and (friendsEntries != []):
        # If active status has changed, update it.
        for row in friendsEntries:
            dbRow = db(db.dbFriends.id == row["id"])
            dbRow.update(active_stat=content)

    return dict(session=session, 
                content=content)

# change the db.user's perfered theme
@action('user/<userID>/theme/<theme_id:int>')
@action.uses(db, session)
def update_db_theme(userID=None, theme_id=None):
    assert theme_id is not None
    assert userID is not None
    # print(theme_id)
    # print(userID)
    user_data = db.dbUser[getIDFromUserTable(userID)]
    db(db.dbUser.id == getIDFromUserTable(userID)).update(chosen_theme=theme_id)

    redirect(URL('user/'+userID))
    dict(session=session)

# returns the 4 color values for db.user's selected mode
def return_theme(chosen_theme=None):
    # assert chosen_theme is not None

    # will return an array of strings representing the color hex 
    # values of each theme in a format reflecting the following 
    # [background_bot, background_top, friend_tile, tile_color, text_color]

    # countryTheme brown, yellow, soft brown, soft yellow, white
    if chosen_theme == "2": 
        return ['#420d09', '#f8e473', '#A07E54', '#FFFDD6', '#FFFFFF']
    # rapTheme black, red, soft red, metal gray, white
    if chosen_theme == "3": 
        return ['#191414', '#800000', '#993333', '#919191', '#FFFFFF']
    # popTheme pink, blue, pink, white, black
    if chosen_theme == "4": 
        return ['#ffaff6', '#72d3fe', '#ffaff6', '#FFFFFF', '#221B1B']
    # rnbTheme dark purple, light purple, soft purple, soft gray, white
    if chosen_theme == "5": 
        return ['#12006e', '#942ec8', '#8961d8', '#d9dddc', '#FFFFFF']
    # lofiTheme blue, mint, soft gray, soft purple, black
    if chosen_theme == "6": 
        return ['#89cfef', '#d0f0c0', '#F5F5F5', '#E5DAFB', '#221B1B']
    # metalTheme black, gray, black, gray, white
    if chosen_theme =="7":
        return ['#191414', '#B3B3B3', '#191414', '#B3B3B3', "#FFFFFF"]
    # defaultTheme black, green, green, soft gray, black
    else: 
        return ['#191414', '#4FE383', '#4FE383', '#f0f0f0', '#221B1B']

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

def checkIfFriendDuplicate(inputID):
    friendsEntries = (db(db.dbFriends.userID == inputID).select().as_list())
    friendtowhoID = getIDFromUserTable(session.get("userID"))
    for entry in friendsEntries:
        if (entry["friendToWhoID"] == friendtowhoID):
            return True
    return False
