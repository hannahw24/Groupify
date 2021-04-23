You have to install something new

go to your /py4web folder
conda activate cse183
pip3 install spotipy
-------------------------------------

To launch the app correctly

cd into your py4web/apps/AppLayout folder

If on windows run these following commands on the commandline

a. SET SPOTIPY_CLIENT_ID=f4cfb74420ed4bcaab8408922adb5820

On Mac/Linux:
export SPOTIPY_CLIENT_ID='f4cfb74420ed4bcaab8408922adb5820'
b. SET SPOTIPY_CLIENT_SECRET=d9ff6b1b8e0d4dd3a421f0c1e4f70e67

On Mac/Linux:
export SPOTIPY_CLIENT_SECRET='d9ff6b1b8e0d4dd3a421f0c1e4f70e67'
c. SET SPOTIPY_REDIRECT_URI=http://127.0.0.1:8000/AppLayout/callback

On Mac/Linux:
export SPOTIPY_REDIRECT_URI='http://127.0.0.1:8000/AppLayout/callback'
cd back to /py4web

conda activate cse183

python py4web.py run apps

TO MAKE RUNNING THE APP EASIER, PUT THESE INSTRUCTIONS ON A NOTEPAD AND COPY AND PASTE INTO ANACONDA

Your path to py4web/apps/AppLayout here

export SPOTIPY_CLIENT_ID='f4cfb74420ed4bcaab8408922adb5820'

export SPOTIPY_CLIENT_SECRET='d9ff6b1b8e0d4dd3a421f0c1e4f70e67'

export SPOTIPY_REDIRECT_URI='http://127.0.0.1:8000/AppLayout/callback'

cd ..

cd ..

conda activate cse183

python py4web.py run apps