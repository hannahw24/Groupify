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
from py4web.utils.url_signer import URLSigner
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
scopes = "user-library-read user-read-private user-follow-read user-follow-modify user-top-read streaming user-read-email"

url_signer = URLSigner(session)

def getUserID():
    return session.get("userID")

@action('index', method='GET')
@action.uses('index.html', session)
def getIndex(userID=None):
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
@action.uses('login.html', session)
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
        return redirect('login')

    # Necessary to make a call to the API.
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    # "sp.current_user()" returns: display name, email
    # url to user, id, images (profile pic), and premium status
    results = spotify.current_user()

    display_name = results["display_name"]
    userID = results["id"]
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
        db.dbUser.insert(userID=userID, display_name=display_name, profile_pic=profile_pic)
        insertedID = getIDFromUserTable(userID)
    # If it is in the database, update its top tracks
    else:
        # Update all info
        db(db.dbUser.userID == userID).update(display_name=display_name)
        db(db.dbUser.userID == userID).update(profile_pic=profile_pic)
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

    # Stores/updates user playlists
    storePlaylists(userID)

    # If the album covers table is empty, we insert it here
    if (squareEntries == None) or (squareEntries == []):
        insertedID = getIDFromUserTable(userID)
        db.squares.insert(albumsOfWho=insertedID)
    # After inserting/updating user information, send them to their 
    # profile page
    return redirect(profileURL)

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
        termEntry = (db(db.shortTerm.topTracksOfWho == getIDFromUserTable(userID)).select().as_list())
    elif term == 'medium_term':
        termEntry = (db(db.mediumTerm.topTracksOfWho == getIDFromUserTable(userID)).select().as_list())
    elif term == 'long_term':
        termEntry = (db(db.longTerm.topTracksOfWho == getIDFromUserTable(userID)).select().as_list())

    # Is their desired term of top tracks populated?
    # If it isn't, then the information from tracksList will be inserted.
    if (termEntry == None) or (termEntry == []):
        insertedID = getIDFromUserTable(userID)
        if term == 'short_term':
            db.shortTerm.insert(topTracks=topTracks, topArtists=topArtists, imgList=imgList, 
                            trackLinks=trackLinks, artistLinks=artistLinks, topTracksOfWho=insertedID)
        elif term == 'medium_term':
            db.mediumTerm.insert(topTracks=topTracks, topArtists=topArtists, imgList=imgList, 
                            trackLinks=trackLinks, artistLinks=artistLinks, topTracksOfWho=insertedID)
        elif term == 'long_term':
            db.longTerm.insert(topTracks=topTracks, topArtists=topArtists, imgList=imgList, 
                            trackLinks=trackLinks, artistLinks=artistLinks, topTracksOfWho=insertedID)

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
    friendsList = db(db.dbFriends.friendToWhoID == userNumber).select(orderby=db.dbFriends.display_name).as_list()
    # To see if the button "Unfollow" or "Follow" appears
    isFriend = db((db.dbFriends.friendToWhoID == getIDFromUserTable(session.get("userID"))) & (db.dbFriends.userID == userID)).select().as_list()
    if (isFriend != []):
        isFriend=True
    
    # get the current chosen theme in the db.user, and set 5 varibles to be passed to html
    # [background_bot, background_top, friend_tile, tile_color, text_color]
    theme_colors = return_theme((db.dbUser[getIDFromUserTable(userID)]).chosen_theme)
    dbUserEntry = (db(db.dbUser.userID == userID).select().as_list())
    display_name=dbUserEntry[0]["display_name"]
    bio_status=dbUserEntry[0]["bio_status"]

    return dict(
        session=session, 
        editable=editable_profile(userID), 
        friendsList=friendsList, 
        profile_pic=profile_pic,
        display_name=display_name,
        bio_status=bio_status,

        background_bot=theme_colors[0],
        background_top=theme_colors[1],
        friend_tile=theme_colors[2],
        tile_color=theme_colors[3],
        text_color=theme_colors[4],

        playlistNames=playlistNames,
        playlistImages=playlistImages,
        playlistURLs=playlistURLs,
        playlistDescriptions=playlistDescriptions,

        userID=userID, isFriend=isFriend, url_signer=url_signer, urlList=urlList, coverList=coverList,
        userBio=URL("userBio", userID), getTopSongs=URL("getTopSongs", userID), getPlaylists=URL("getPlaylists"),
        userStat=URL("userStat", userID))

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

    return dict(session=session, editable=False, 
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
    userID = getUserID()
    print(userID)
    # Get squares (cover and url) from db
    user_squares = db(db.squares.albumsOfWho == getIDFromUserTable(userID)).select().as_list()
    print(user_squares)
    coverList = user_squares[0]["coverList"]
    urlList = user_squares[0]["urlList"]
    # Return items for search.js
    return dict(coverList=coverList, urlList=urlList)

# URL to post new albums to server
@action('get_squares',  method="POST")
@action.uses(db)
def save_albums():
    # Get lists from search.js
    coverList = request.json.get('coverList')
    urlList = request.json.get('urlList')
    userID = getUserID()
    # Update db
    dbSquareEntry = db(db.squares.albumsOfWho == getIDFromUserTable(userID))
    squareEntries = dbSquareEntry.select().as_list()
    dbSquareEntry.update(coverList=coverList, urlList=urlList)
    return dict(coverList=coverList, urlList=urlList)

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
    print("FORM DATA:")
    print(form_SearchValue)
    # If empty, return empty lists
    if form_SearchValue == "":
        return dict(topAlbums=topAlbums, topArtists=topArtists, imgList=imgList,
        trackLinks=trackLinks, artistLinks=artistLinks, totalResults=totalResults)
    
    # Get results from Spotify
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('login')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    results = spotify.search(form_SearchValue, type='album', limit=10)
    
    try:
        # If the search results yielded no results, then return nothing. 
        totalResults = results["albums"]["total"]
        if (totalResults == 0):
            return dict(topAlbums=topAlbums, topArtists=topArtists, imgList=imgList,
            trackLinks=trackLinks, artistLinks=artistLinks, totalResults=totalResults)
        # Else begin to parse the JSON by looking at the albums
        results = results["albums"]
    except:
        print(results)
        return dict(topAlbums=topAlbums, topArtists=topArtists, imgList=imgList,
        trackLinks=trackLinks, artistLinks=artistLinks, totalResults=totalResults)

    # Parses through the JSON and returns a list of lists with the information we desire
    biglist = getAlbumResults(results)
    topAlbums = biglist[0]
    topArtists = biglist[1]
    imgList = biglist[2]
    trackLinks = biglist[3]
    artistLinks = biglist[4]
    # Return this information to display
    return dict(topAlbums=topAlbums, topArtists=topArtists, imgList=imgList,
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
@action.uses('user_not_found.html', session)
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
    return dict(session=session, editable=False, userID=userID, url_signer=url_signer, 
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
    print(theme_id)
    print(userID)
    user_data = db.dbUser[getIDFromUserTable(userID)]
    db(db.user_data.id == getIDFromUserTable(userID).update(chosen_theme=theme_id))

    profileURL = "user/" + userID
    redirect(profileURL)
    return dict(session=session)

# UNUSED
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

# Make the spotify API call to get the user playlists
# Also calls parsePlaylistResults() to parse JSON from the API call
@action('getPlaylists')
def getPlaylists():
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)
    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        return redirect('login')
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    # 14 is an estimate on how long the box is 
    results = spotify.current_user_playlists(limit=14)
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
    playlistEntry = (db(db.playlists.playlistsOfWho == getIDFromUserTable(userID)).select().as_list())

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
    for idx, item in enumerate(results['items']):
        # Get items from correct place in given Spotipy dictionary
        playlistName = item['name']
        #trackInfo = item['artists'][0]['name']
        icon = item['images'][0]['url']
        trLink = item['external_urls']['spotify']
        description = item['description']
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
        return redirect('login')
    spotify = spotipy.Spotify(auth_manager=auth_manager)

    # long_term = all time
    # medium_term = 6 months
    # short_term = 4 weeks
    results = spotify.current_user_top_tracks(limit=10, offset=0, time_range=term)    #Taken from the quick start of Spotipy authorization flow
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

@action('groupSession/<userID>')
@action.uses(db, auth, 'groupSession.html', session)
def groupSession(userID=None):
    # Ash: set editable to False for now, not sure if setting the theme
    #      on the groupSession page will change it for everyone
    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = spotipy.oauth2.SpotifyClientCredentials(cache_handler=cache_handler)
    try:
        token = auth_manager.get_access_token()
    except:
        return redirect('login')
    print ("TOKEN IS ", token["access_token"])
    profileURL = (URL("user", userID))
    currentProfileEntry = db(db.dbUser.userID == userID).select().as_list()
    profile_pic = ""
    if (currentProfileEntry != None) and (currentProfileEntry != []):
       # Setting the top tracks and profile pic variables
       profile_pic = currentProfileEntry[0]["profile_pic"]
    if userID is not None:
        try:
            user_from_table = db.dbUser[getIDFromUserTable(session.get("userID"))]
            theme_colors = return_theme(user_from_table.chosen_theme)
        except:
            theme_colors = return_theme(0)
        return dict(session=session, editable=False,
            background_bot=theme_colors[0],background_top=theme_colors[1], token=token["access_token"], 
            profile_pic=profile_pic, profileURL = profileURL)
    else:
        return dict( session=session, editable=False, 
            background_bot=None, background_top=None, token=token["access_token"],
            profile_pic=profile_pic, profileURL = profileURL)

@action('settings/<userID>')
@action.uses(db, auth, 'settings.html', session)
def getSettings(userID=None):
    profileURL = "http://127.0.0.1:8000"+(URL("user", userID))
    currentProfileEntry = db(db.dbUser.userID == userID).select().as_list()
    profile_pic = ""
    if (currentProfileEntry != None) and (currentProfileEntry != []):
       # Setting the top tracks and profile pic variables
       profile_pic = currentProfileEntry[0]["profile_pic"]
    if userID is not None:
        user_from_table = db.dbUser[getIDFromUserTable(session.get("userID"))]
        theme_colors = return_theme(user_from_table.chosen_theme)
        return dict( session=session, editable=False, userID=userID, url_signer=url_signer,
            background_bot=theme_colors[0],background_top=theme_colors[1],profile_pic=profile_pic, profileURL = profileURL)
    else:
        return dict( session=session, editable=False, userID=userID, url_signer=url_signer,
            background_bot=None, background_top=None,profile_pic=profile_pic, profileURL=profileURL)

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
    theme_colors = return_theme((db.dbUser[getIDFromUserTable(session.get("userID"))]).chosen_theme)
    if request.method == "GET":
        return dict(session=session, editable=False, nullError=False, alreadyFriend=False, CannotAddSelf=False, background_bot=theme_colors[0], 
                background_top=theme_colors[1])
    else:
        loggedInUserId = session.get("userID")
        form_userID = request.params.get("userID")
        dbUserEntry = (db(db.dbUser.userID == form_userID).select().as_list())
        if dbUserEntry == []:
            return dict(session=session, editable=False, nullError=True, alreadyFriend=False, CannotAddSelf=False, background_bot=theme_colors[0], 
                background_top=theme_colors[1])
        if (checkIfFriendDuplicate(form_userID)):
            return dict(session=session, editable=False, nullError=False, alreadyFriend=True, CannotAddSelf=False, background_bot=theme_colors[0], 
                background_top=theme_colors[1])
        if (form_userID == loggedInUserId):
            return dict(session=session, editable=False, nullError=False, alreadyFriend=False, CannotAddSelf=True, background_bot=theme_colors[0], 
                background_top=theme_colors[1])
        db.dbFriends.insert(userID=form_userID, friendToWhoID=getIDFromUserTable(loggedInUserId), 
                            profile_pic=dbUserEntry[0]["profile_pic"], display_name=dbUserEntry[0]["display_name"], bio_status=dbUserEntry[0]["bio_status"],
                            active_stat=dbUserEntry[0]["active_stat"])
        return redirect(URL('user', session.get("userID")))

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
    db.dbFriends.insert(userID=userID, friendToWhoID=getIDFromUserTable(loggedInUserId), 
                            profile_pic=dbUserEntry[0]["profile_pic"], display_name=dbUserEntry[0]["display_name"], bio_status=dbUserEntry[0]["bio_status"],
                            active_stat=dbUserEntry[0]["active_stat"])
    return redirect(URL('user', userID))

# Function used by seeTerm() in user.js to extract the top song information
# from the correct table in the database. 
@action('getTopSongs/<userID>', method=["GET"])
@action.uses(session)
def getTopSongs(userID=None):
    # Finds the value of the term chosen by the user. 
    # This "term" is about what period of top songs to display on 
    # a user's profile.
    term = (db.dbUser[getIDFromUserTable(userID)]).chosen_term
    # Obtains the whole entry of the user in the correct table.
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
    db(db.dbUser.id == getIDFromUserTable(userID)).update(chosen_term=term)	
    return dict(session=session)	

# Retrieves the bio of the user, used in user.js to display the bio
@action('userBio/<userID>', method=["GET"])
@action.uses(session)
def getUserBio(userID=None):
    currentProfileEntry = db(db.dbUser.userID == userID).select().as_list()
    return dict(userBio=currentProfileEntry[0]["bio_status"])

# Makes a request to user.js for the content in the text area after a user hits the save button
# Then updates the bio in the database
# ASH: WARNING -- MAY BE UNSAFE/EDITABLE BY OTHERS -- NEEDS TESTING
@action('userBio/<userID>', method=["POST"])
@action.uses(session)
def postUserBio(userID=None):
    dbBioEntry = db(db.dbUser.userID == userID)
    content = request.params.get('content')
    dbBioEntry.update(bio_status=content)
    return dict(content=content)

# Retrieves the status of the user, used in user.js to display the bio
@action('userStat/<userID>', method=["GET"])
@action.uses(session)
def getUserStat(userID=None):
    currentProfileEntry = db(db.dbUser.userID == userID).select().as_list()
    return dict(userStat=currentProfileEntry[0]["active_stat"])

# Makes a request to user.js for the content in the text area after a user hits the save button
# Then updates the bio in the database
@action('userStat/<userID>', method=["POST"])
@action.uses(session)
def postUserStat(userID=None):
    dbStatEntry = db(db.dbUser.userID == userID)
    content = request.params.get('content')
    dbStatEntry.update(active_stat=content)
    return dict(content=content)

@action('unfollowProfile/<userID>', method=['GET'])
@action.uses(session, db)
def delete_contact(userID=None):
    person = db((db.dbFriends.userID == userID) & (db.dbFriends.friendToWhoID == getIDFromUserTable(session.get("userID")))).select().as_list()
    if person is None or person == []:
        # Nothing to edit.  This should happen only if you tamper manually with the URL.
        redirect(URL('user', userID))
    else:
        person = person[0]
        friendToWhoID = person["friendToWhoID"]
        if friendToWhoID == getIDFromUserTable(session.get("userID")):
            db(db.dbFriends.id == person["id"]).delete()
        redirect(URL('user', userID))

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
        return ['#ffaff6', '#0080fe', '#ffaff6', '#FFFFFF', '#221B1B']
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
