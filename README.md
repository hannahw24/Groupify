# Groupify
This project uses the py4web web framework. Learn how to install py4web here https://py4web.com/
To add Groupify to your py4web apps folder, one can add the groupify folder manually by copy and pasting, 
or use py4web's _dashboard interface to copy the folder. Then follow the requirements below. 

Requirements: 
In addition to all the py4web requirements, **a module named spotipy must also be installed.** 
To do this, navigate to where your /py4web folder is located. 
In a terminal, spotipy can be installed with the command `pip3 install spotipy`
To make calls to the Spotify API, an application must be registerd in https://developer.spotify.com/
After registering, the client ID, secret ID, and callback URL must be set inside of groupify. 

The safest way is to export these variables to the application. 

If on windows **run** **these following** **commands** on the commandline 

    a. SET SPOTIPY_CLIENT_ID=client id
    
    b. SET SPOTIPY_CLIENT_SECRET=secret id
    
    c. SET SPOTIPY_REDIRECT_URI=callback URL
    
If on Mac/Linux **run** **these following** **commands** on the commandline 

    a. export SPOTIPY_CLIENT_ID='client id'
    
    b. export SPOTIPY_CLIENT_SECRET='secret id'
    
    c. export SPOTIPY_REDIRECT_URI='callback URL'
