import unittest
import requests
from pydal import DAL, Field
import sys
from .common import db, session
from . import controllers

#F.I.R.S.T = Fast Independent Repeatable Self-validating Thorough 

db = DAL("sqlite:memory")
db.define_table(
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
db.define_table(
    'playlists',
    #Change this to one big field with 1 list with 6 index [0][1]...
    #Also just return the albumsOfWho ID for albumInput because it should be unique. 
    Field('names', 'list:string'), 
    Field('images', 'list:string'),
    Field('links', 'list:string'), 
    Field('descriptions', 'list:string'),
    Field('playlistsOfWho', db.dbUser)
    )

class TestUserProfileResponses(unittest.TestCase):

    localURL = 'http://127.0.0.1:8000/groupify'
    hostedURL = 'http://shams.pythonanywhere.com/groupify'

    def testExistingProfileReturnsOK(self):
        print('testExistingProfileReturnsOK\n')
        # URL to non existent user. 
        localGroupSessionURL = self.localURL + "/user/122858386"
        response = requests.head(localGroupSessionURL)
        self.assertEqual(response.ok, True)
        hostedGroupSessionURL = self.hostedURL + "/user/122858386"
        response = requests.head(hostedGroupSessionURL)
        self.assertEqual(response.ok, True)

    # Checks if user is redirected to a "user does not exist" page when placing an incorrect userID
    def testProfileRedirectOnNonExistentUser(self):
        print('testProfileRedirectOnNonExistentUser\n')
        # URL to non existent user. 
        localGroupSessionURL = self.localURL + "/user/1"
        response = requests.head(localGroupSessionURL)
        self.assertEqual(response.is_redirect, True)
        hostedGroupSessionURL = self.hostedURL + "/user/1"
        response = requests.head(hostedGroupSessionURL)
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
        hostedGroupSessionURL = self.hostedURL + "/groupSession/122858386"
        response = requests.head(hostedGroupSessionURL)
        self.assertEqual(response.ok, True)


    def testGroupSessionRedirectOnNonExistentUser(self):
        print('testGroupSessionRedirectOnNonExistentUser\n')
        # URL to non existent group session. 
        localGroupSessionURL = self.localURL + "/groupSession/1"
        response = requests.head(localGroupSessionURL)
        self.assertEqual(response.is_redirect, True)
        hostedGroupSessionURL = self.hostedURL + "/groupSession/122858386"
        response = requests.head(hostedGroupSessionURL)
        self.assertEqual(response.is_redirect, True)

class TestPlaylistParsingAndStorage(unittest.TestCase):

    # Creates a dbUser entry
    @classmethod
    def setUpClass(self):
        self.insertionID = db.dbUser.insert(userID=1, display_name="tester", profile_pic="")
        db.commit()
        self.dbUser = (db(db.dbUser.id == self.insertionID).select().as_list())
        return
    
    # Deletes the user entry stored in the database, along with any references to it.
    @classmethod
    def tearDownClass(self):
        db(db.dbUser.userID == self.insertionID).delete()
        db.commit()
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

    # Tests if the parsed information is correctly stored in the database. 
    def testParsedAlbumsAreStoredInDatabase(self):
        print ("testParsedAlbumsAreStoredInDatabase")
        results = self.testParseAlbumResultsReturnsCorrectPlaylistInformation()

        ############################################################################################
        # The following code is emulating storePlaylists() from controllers.py
        # The function in its current state cannot accept a constructor injection giving it the 
        # parsed playlist information that is tested in 
        # testParseAlbumResultsReturnsCorrectPlaylistInformation()
        playlistNames = results[0]
        playlistImages = results[1]
        playlistURLs = results[2]
        descriptions = results[3]

        # Tries to find the entry of the user in the playlist table
        playlistEntry = (db(db.playlists.playlistsOfWho 
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
            insertPlaylistID = db.playlists.insert(names=playlistNames, images=playlistImages,
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
            dbRow = db(db.playlists.playlistsOfWho == insertedID)
            insertPlaylistID = dbRow.update(names=playlistNames, images=playlistImages,
                        links=playlistURLs, descriptions=descriptions)
        db.commit()
        ############################################################################################
        
        # Getting the table entry where the playlist information is stored.
        insertPlaylistEntry = (db(db.playlists.id == insertPlaylistID).select().as_list())
        
        # Checking that the table entry has the correct playlist information stored.
        self.assertEqual(insertPlaylistEntry[0]["names"], ["West coast"])
        self.assertEqual(insertPlaylistEntry[0]["images"], 
                        ['https://i.scdn.co/image/ab67706c0000bebb6f4e8d14163c77eaaaa49463'])
        self.assertEqual(insertPlaylistEntry[0]["links"], 
                        ['https://open.spotify.com/playlist/37u7PP4U5ay6j4v7qZYYIB'])
        self.assertEqual(insertPlaylistEntry[0]["descriptions"], 
                        ['MUSC 80P forced me to listen to this'])


class TestDeleteProfile(unittest.TestCase):
    # Creates a dbUser and playlists entry
    @classmethod
    def setUpClass(self):
        self.dbuserInsertionID = db.dbUser.insert(userID=1, display_name="tester", profile_pic="")
        self.insertPlaylistID = db.playlists.insert(names=["test name"], images=["none"],
                                links=["ucsc.edu"], descriptions=["test description"], 
                                playlistsOfWho=self.dbuserInsertionID)        
        db.commit()

    # Tests if deleting a dbUser table entry will also delete the reference to it in 
    # the playlists table.
    def testDeleteProfileActionDeletesAllInstancesFromDatabase(self):
        print("testDeleteProfileActionDeletesAllInstancesFromDatabase")
        dbUser = (db(db.dbUser.id == self.dbuserInsertionID)).select().as_list()
        playlists = (db(db.playlists.playlistsOfWho == self.dbuserInsertionID)).select().as_list()
        # Assert that the entry has been filled with something, and therefore is not an empty list
        self.assertNotEqual(dbUser, [])
        self.assertNotEqual(playlists, [])
        db(db.dbUser.userID == 1).delete()
        # Assert that the entry has been deleted, and therefore the list is empty.
        dbUser = (db(db.dbUser.id == self.dbuserInsertionID)).select().as_list()
        playlists = (db(db.playlists.playlistsOfWho == self.dbuserInsertionID)).select().as_list()
        self.assertEqual(dbUser, [])
        self.assertEqual(playlists, [])
        db.commit()
        return

if __name__ == '__main__':
    unittest.main()