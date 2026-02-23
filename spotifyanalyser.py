# Spotify Playlist Analyser
# v1: connect to Spotify API and authenticate

import spotipy
from spotipy.oauth2 import SpotifyOAuth

# swap these out for your own credentials from the Spotify developer dashboard
CLIENT_ID = "f5b45838eb4b4e008f461f2bd6c54bbc"
CLIENT_SECRET = "7cf4d6f251ca49b791a784e6b929c4fe"
REDIRECT_URI = "http://127.0.0.1:8888/callback"

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

def get_playlists(sp):
    print("\n[*] Fetching your playlists...\n")
    playlists = sp.current_user_playlists()
    results = []
    for i, playlist in enumerate(playlists['items']):
        print(f"  {i + 1}. {playlist['name']} ({playlist['tracks']['total']} tracks)")
        results.append(playlist)
    return results

def get_tracks(sp, playlist):
    print(f"\n[*] Fetching tracks from: {playlist['name']}...\n")
    tracks = []
    response = sp.playlist_tracks(playlist['id'])
    while response:
        for item in response['items']:
            track = item.get('track')
            if track:
                tracks.append({
                    'name': track['name'],
                    'artist': track['artists'][0]['name'],
                    'id': track['id']
                })
        response = sp.next(response) if response['next'] else None
    return tracks

def get_audio_features(sp, tracks):
    print("\n[*] Pulling audio features for each track...\n")
    # spotify limits to 100 ids per request so we batch them
    ids = [t['id'] for t in tracks if t['id']]
    features = []
    for i in range(0, len(ids), 100):
        batch = ids[i:i + 100]
        result = sp.audio_features(batch)
        if result:
            features.extend([f for f in result if f])

    print(f"[+] Got audio features for {len(features)} tracks\n")

    if features:
        sample = features[0]
        print("  Sample track features:")
        print(f"    Danceability: {sample['danceability']}")
        print(f"    Energy:       {sample['energy']}")
        print(f"    Valence:      {sample['valence']}  (higher = happier)")
        print(f"    Tempo:        {sample['tempo']} BPM")
        print(f"    Acousticness: {sample['acousticness']}")

    return features

sp = connect()
playlists = get_playlists(sp)

print("\nEnter playlist number to analyse: ", end="")
choice = int(input()) - 1
tracks = get_tracks(sp, playlists[choice])
features = get_audio_features(sp, tracks)