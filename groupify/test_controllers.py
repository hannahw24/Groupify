import unittest
import requests
from pydal import DAL, Field
from . import controllers
import json


#F.I.R.S.T = Fast Independent Repeatable Self-validating Thorough 
class TestUserProfileResponses(unittest.TestCase):

    localURL = 'http://127.0.0.1:8000/groupify'
    hostedURL = 'http://shams.pythonanywhere.com/groupify'

    #def setUp(self):
        #print('setUp')

    #def tearDown(self):
        #print('tearDown')

    def testExistingProfileReturnsOK(self):
        print('testExistingProfileReturnsOK\n')
        # URL to non existent user. 
        localGroupSessionURL = self.localURL + "/user/122858386"
        response = requests.head(localGroupSessionURL)
        self.assertEqual(response.ok, True)

    # Checks if user is redirected to a "user does not exist" page when placing an incorrect userID
    def testProfileRedirectOnNonExistentUser(self):
        print('testProfileRedirectOnNonExistentUser\n')
        # URL to non existent user. 
        localGroupSessionURL = self.localURL + "/user/1"
        response = requests.head(localGroupSessionURL)
        self.assertEqual(response.is_redirect, True)

class TestGroupSessionResponses(unittest.TestCase):

    localURL = 'http://127.0.0.1:8000/groupify'
    hostedURL = 'http://shams.pythonanywhere.com/groupify'
    
    def testGroupSessionReturnsOK(self):
        print('testGroupSessionReturnsOK\n')
        # Ash's groupSession URL
        localGroupSessionURL = self.localURL + "/groupSession/122858386"
        response = requests.head(localGroupSessionURL)
        self.assertEqual(response.ok, True)

    def testGroupSessionRedirectOnNonExistentUser(self):
        print('testGroupSessionRedirectOnNonExistentUser\n')
        # URL to non existent group session. 
        localGroupSessionURL = self.localURL + "/groupSession/1"
        response = requests.head(localGroupSessionURL)
        self.assertEqual(response.is_redirect, True)

class TestPlaylistParsingAndStorage(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.db = DAL("sqlite:memory")
        self.db.define_table(
            'dbUser',
            Field('userID', notnull=True, unique=True),
            Field('display_name'),
            Field('chosen_theme'),
            Field('bio_status'),
            Field('active_stat'),
            Field('profile_pic'),
            Field('chosen_term'),
            Field('artist_term'),
            Field('premiumStatus'),
        )
        self.db.define_table(
            'playlists',
            #Change this to one big field with 1 list with 6 index [0][1]...
            #Also just return the albumsOfWho ID for albumInput because it should be unique. 
            Field('names', 'list:string'), 
            Field('images', 'list:string'),
            Field('links', 'list:string'), 
            Field('descriptions', 'list:string'),
            Field('playlistsOfWho', self.db.dbUser)
        )
        self.insertionID = self.db.dbUser.insert(userID=1, display_name="tester", profile_pic="")
        self.db.commit()
        self.dbUser = (self.db(self.db.dbUser.id == self.insertionID).select().as_list())
        print (self.dbUser)
        return
    
    @classmethod
    def tearDownClass(self):
        return

    fullPlaylistVariablesJSON = \
    {"href":"https://api.spotify.com/v1/users/1228586386/playlists?offset=0&limit=50", 
        "items":[
        {
        "collaborative":False,
        "description":"MUSC 80P forced me to listen to this",
        "external_urls":{
        "spotify":"https://open.spotify.com/playlist/37u7PP4U5ay6j4v7qZYYIB"
        },
        "href":"https://api.spotify.com/v1/playlists/37u7PP4U5ay6j4v7qZYYIB",
        "id":"37u7PP4U5ay6j4v7qZYYIB",
        "images":[
        {
        "height":"None",
        "url":"https://i.scdn.co/image/ab67706c0000bebb6f4e8d14163c77eaaaa49463",
        "width":"None"
        }
        ],
        "name":"West coast",
        "owner":{
        "display_name":"Ash",
        "external_urls":{
        "spotify":"https://open.spotify.com/user/1228586386"
        },
        "href":"https://api.spotify.com/v1/users/1228586386",
        "id":"1228586386",
        "type":"user",
        "uri":"spotify:user:1228586386"
        },
        "primary_color":"None",
        "public":True,
        "snapshot_id":"MTQsYjNlMTQxMzNlOGVmODlmZDA4NmRkMjI3NWI1MTY0OWE4NWZlNWU1Nw==",
        "tracks":{
        "href":"https://api.spotify.com/v1/playlists/37u7PP4U5ay6j4v7qZYYIB/tracks",
        "total":10
        },
        "type":"playlist",
        "uri":"spotify:playlist:37u7PP4U5ay6j4v7qZYYIB"
        },
        ],
        "limit":50,
        "next":"None",
        "offset":0,
        "previous":"None",
        "total":9}

    emptyImageAndDescriptionJSON = \
    {"href":"https://api.spotify.com/v1/users/1228586386/playlists?offset=0&limit=50", 
        "items":[
        {
        "collaborative":False,
        "description":"",
        "external_urls":{
        "spotify":"https://open.spotify.com/playlist/37u7PP4U5ay6j4v7qZYYIB"
        },
        "href":"https://api.spotify.com/v1/playlists/37u7PP4U5ay6j4v7qZYYIB",
        "id":"37u7PP4U5ay6j4v7qZYYIB",
        "name":"West coast",
        "owner":{
        "display_name":"Ash",
        "external_urls":{
        "spotify":"https://open.spotify.com/user/1228586386"
        },
        "href":"https://api.spotify.com/v1/users/1228586386",
        "id":"1228586386",
        "type":"user",
        "uri":"spotify:user:1228586386"
        },
        "primary_color":"None",
        "public":True,
        "snapshot_id":"MTQsYjNlMTQxMzNlOGVmODlmZDA4NmRkMjI3NWI1MTY0OWE4NWZlNWU1Nw==",
        "tracks":{
        "href":"https://api.spotify.com/v1/playlists/37u7PP4U5ay6j4v7qZYYIB/tracks",
        "total":10
        },
        "type":"playlist",
        "uri":"spotify:playlist:37u7PP4U5ay6j4v7qZYYIB"
        },
        ],
        "limit":50,
        "next":"None",
        "offset":0,
        "previous":"None",
        "total":9}

    # Test if the function parsePlaylistResults() returns a list of lists containing the information
    # of the playlist in the class fullPlaylistVariablesJSON variable
    def testParseAlbumResultsReturnsCorrectPlaylistInformation(self):
        print('testParseAlbumResultsReturnsCorrectPlaylistInformation\n')
        results = controllers.parsePlaylistResults(self.fullPlaylistVariablesJSON)
        playlistName = results[0]
        self.assertEqual(playlistName, ['West coast'])
        imgLinkList = results[1]
        self.assertEqual(
            imgLinkList, ['https://i.scdn.co/image/ab67706c0000bebb6f4e8d14163c77eaaaa49463'])
        playlistLinkList = results[2]
        self.assertEqual(
            playlistLinkList, ['https://open.spotify.com/playlist/37u7PP4U5ay6j4v7qZYYIB'])
        descriptionList = results[3]
        self.assertEqual(descriptionList, ['MUSC 80P forced me to listen to this'])
        return results

    # Tests if the function parsePlaylistResults() correctly handles playlists without a 
    # description or image by using the emptyImageAndDescriptionJSON variable.
    def testParseAlbumResultsHandlesEmptyImageAndDescription(self):
        print('testParseAlbumResultsHandlesEmptyImageAndDescription\n')
        results = controllers.parsePlaylistResults(self.emptyImageAndDescriptionJSON)
        playlistName = results[0]
        self.assertEqual(playlistName, ['West coast'])
        imgLinkList = results[1]
        # If the function cannot find the playlsit image, 
        # it inserts this placeholder image in its place.
        self.assertEqual(
            imgLinkList, ['https://bulma.io/images/placeholders/128x128.png'])
        playlistLinkList = results[2]
        self.assertEqual(
            playlistLinkList, ['https://open.spotify.com/playlist/37u7PP4U5ay6j4v7qZYYIB'])
        descriptionList = results[3]
        # An empty description has an opening and closing bracket put in its place. This
        # is because inserting "" is problematic as the database will not insert an empty
        # string.
        self.assertEqual(descriptionList, [[]])

    def testParsedAlbumsAreStoredInDatabase(self):
        print ("testParsedAlbumsAreStoredInDatabase")
        results = self.testParseAlbumResultsReturnsCorrectPlaylistInformation()
        playlistNames = results[0]
        playlistImages = results[1]
        playlistURLs = results[2]
        descriptions = results[3]

        # Tries to find the entry of the user in the playlist table
        playlistEntry = (self.db(self.db.playlists.playlistsOfWho 
                        == self.insertionID).select().as_list())

        # Is their playlist entry already populated?
        # If it isn't, then the playlists will be inserted
        if (playlistEntry == None) or (playlistEntry == []):
            insertedID = self.insertionID
            if playlistNames == "":
                playlistNames = []
                playlistImages = []
                playlistURLs = []
                descriptions = []
            insertPlaylistID = self.db.playlists.insert(names=playlistNames, images=playlistImages,
                                links=playlistURLs, descriptions=descriptions, 
                                playlistsOfWho=insertedID)
        # If there are already playlists, then update the information
        else:
            insertedID = self.insertionID
            if playlistNames == "":
                playlistNames = []
                playlistImages = []
                playlistURLs = []
                descriptions = []
            # Finds the correct user entry
            dbRow = self.db(self.db.playlists.playlistsOfWho == insertedID)
            insertPlaylistID = dbRow.update(names=playlistNames, images=playlistImages,
                        links=playlistURLs, descriptions=descriptions)
        print((self.db(self.db.playlists.id == insertPlaylistID).select().as_list()))
        self.db.commit()

        insertPlaylistEntry = (self.db(self.db.playlists.id == insertPlaylistID).select().as_list())
        
        self.assertEqual(insertPlaylistEntry[0]["names"], ["West coast"])
        self.assertEqual(insertPlaylistEntry[0]["images"], 
                        ['https://i.scdn.co/image/ab67706c0000bebb6f4e8d14163c77eaaaa49463'])
        self.assertEqual(insertPlaylistEntry[0]["links"], 
                        ['https://open.spotify.com/playlist/37u7PP4U5ay6j4v7qZYYIB'])
        self.assertEqual(insertPlaylistEntry[0]["descriptions"], 
                        ['MUSC 80P forced me to listen to this'])


class TestAlbumParsingAndStorage(unittest.TestCase):
    def testParseAlbumResults(self):
        return
        #results = controllers.parseAlbumResults("")
        #self.assertEqual(results, None)

    # Constructor Injection into a parse functions
    # Put a mock object in these functions 

    # May need to add dummy objects, things that aren't needed but need to be supplied to the function
    # for it to run.

    #Try synch button or pause button but need device ID :(
    
    # Test the speed of functions that use time.time() to see if it's acceptable window

    # We don't have enough information about the internal state of the functions because they were not designed with unit testing in mind. 
    # As we learned in lecture we could maybe encapsulate methods or refactor our code to suit the tests but there wasn't enough time to 
    # ensure all functions would work the same way as before. 
    # I also didn't want to intermengle testing code with product code. 

    # Integration tests check the interactions between already unit tested components. 

    # Selenium 
    # easymock
if __name__ == '__main__':
    unittest.main()