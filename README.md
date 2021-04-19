You have to install something new
1. go to your /py4web folder
2. conda activate cse183
3. pip3 install spotipy 

To launch the app correctly 
1. cd into your py4web/apps/AppLayout folder
2. If on windows **run** **these following** **commands** on the commandline 

    a. SET SPOTIPY_CLIENT_ID=f4cfb74420ed4bcaab8408922adb5820 
    
    b. SET SPOTIPY_CLIENT_SECRET=d9ff6b1b8e0d4dd3a421f0c1e4f70e67
    
    c. SET SPOTIPY_REDIRECT_URI=http://127.0.0.1:8000/AppLayout/callback
    
3. cd back to /py4web
4. conda activate cse183
5. python py4web.py run apps
