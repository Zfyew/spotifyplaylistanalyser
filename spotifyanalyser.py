# Spotify Playlist Analyser
# v1: connect to Spotify API and authenticate

import spotipy
from spotipy.oauth2 import SpotifyOAuth

# swap these out for your own credentials from the Spotify developer dashboard
CLIENT_ID = "f5b45838eb4b4e008f461f2bd6c54bbc"
CLIENT_SECRET = "7cf4d6f251ca49b791a784e6b929c4fe"
REDIRECT_URI = "http://127.0.0.1:8888/callback"

# scope defines what we're asking permission to access
SCOPE = "playlist-read-private user-library-read"

def connect():
    print("\n[*] Connecting to Spotify...\n")
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    ))
    user = sp.current_user()
    print(f"[+] Connected as: {user['display_name']}")
    return sp

sp = connect()