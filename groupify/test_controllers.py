import unittest
import requests
from . import controllers

#F.I.R.S.T = Fast Independent Repeatable Self-validating Thorough 
class TestGroupify(unittest.TestCase):

    localURL = 'http://127.0.0.1:8000/groupify'
    hostedURL = 'http://shams.pythonanywhere.com/groupify'

    #def setUp(self):
        #print('setUp')

    #def tearDown(self):
        #print('tearDown')

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