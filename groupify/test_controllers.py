import unittest
import requests
from . import controllers

class TestGroupify(unittest.TestCase):

    localURL = 'http://127.0.0.1:8000/groupify'
    hostedURL = 'http://shams.pythonanywhere.com/groupify'

    #def setUp(self):
        #print('setUp')

    #def tearDown(self):
        #print('tearDown\n')

    def test_existingProfileReturnsOK(self):
        print('test_existingProfileReturnsOK\n')
        # URL to non existent user. 
        localGroupSessionURL = self.localURL + "/user/122858386"
        response = requests.head(localGroupSessionURL)
        self.assertEqual(response.ok, True)

    # Checks if user is redirected to a "user does not exist" page when placing an incorrect userID
    def test_profileRedirectOnNonExistentUser(self):
        print('test_profileRedirectOnNonExistentUser\n')
        # URL to non existent user. 
        localGroupSessionURL = self.localURL + "/user/1"
        response = requests.head(localGroupSessionURL)
        self.assertEqual(response.is_redirect, True)

    def test_groupSessionReturnsOK(self):
        print('test_local_groupSessionReturnsOK\n')
        # Ash's groupSession URL
        localGroupSessionURL = self.localURL + "/groupSession/122858386"
        response = requests.get(localGroupSessionURL)
        self.assertEqual(response.ok, True)

    # Currently fails
    def test_groupSessionRedirectOnNonExistentUser(self):
        print('test_groupSessionRedirectOnNonExistentUser\n')
        # URL to non existent group session. 
        localGroupSessionURL = self.localURL + "/groupSession/1"
        response = requests.get(localGroupSessionURL)
        self.assertEqual(response.is_redirect, True)


if __name__ == '__main__':
    unittest.main()