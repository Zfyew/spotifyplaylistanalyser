# Spotify Playlist Analyser
# v5: energy and mood pattern analysis

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from collections import Counter

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
                    'artist_id': track['artists'][0]['id'],
                    'id': track['id']
                })
        response = sp.next(response) if response['next'] else None
    return tracks

def get_audio_features(sp, tracks):
    print("\n[*] Pulling audio features...\n")
    ids = [t['id'] for t in tracks if t['id']]
    features = []
    for i in range(0, len(ids), 100):
        batch = ids[i:i + 100]
        result = sp.audio_features(batch)
        if result:
            features.extend([f for f in result if f])
    return features

def get_genre_breakdown(sp, tracks):
    print("\n[*] Analysing genres...\n")
    artist_ids = list(set([t['artist_id'] for t in tracks if t['artist_id']]))
    genres = []
    for i in range(0, len(artist_ids), 50):
        batch = artist_ids[i:i + 50]
        result = sp.artists(batch)
        for artist in result['artists']:
            genres.extend(artist['genres'])

    if not genres:
        print("  No genre data found for this playlist.")
        return []

    counts = Counter(genres).most_common(10)
    print("  Top genres:\n")
    for genre, count in counts:
        bar = "█" * count
        print(f"  {genre:<30} {bar} ({count})")
    return counts

def analyse_mood(features):
    print("\n[*] Mood and energy analysis...\n")
    if not features:
        print("  No audio features available.")
        return

    avg_energy = sum(f['energy'] for f in features) / len(features)
    avg_valence = sum(f['valence'] for f in features) / len(features)
    avg_dance = sum(f['danceability'] for f in features) / len(features)
    avg_tempo = sum(f['tempo'] for f in features) / len(features)
    avg_acoustic = sum(f['acousticness'] for f in features) / len(features)

    print(f"  Average energy:       {avg_energy:.2f} / 1.0")
    print(f"  Average mood:         {avg_valence:.2f} / 1.0  (higher = happier)")
    print(f"  Average danceability: {avg_dance:.2f} / 1.0")
    print(f"  Average tempo:        {avg_tempo:.0f} BPM")
    print(f"  Average acousticness: {avg_acoustic:.2f} / 1.0")

    if avg_energy > 0.7 and avg_valence > 0.6:
        vibe = "High energy and upbeat"
    elif avg_energy > 0.7 and avg_valence <= 0.6:
        vibe = "Intense but darker in tone"
    elif avg_energy <= 0.4 and avg_valence <= 0.4:
        vibe = "Low energy and melancholic"
    elif avg_energy <= 0.4 and avg_valence > 0.4:
        vibe = "Calm and relaxed"
    else:
        vibe = "Mixed energy and mood"

    print(f"\n  Playlist vibe: {vibe}")

def top_artists(tracks):
    print("\n[*] Top artists in this playlist...\n")
    # count how many tracks each artist has
    counts = Counter([t['artist'] for t in tracks]).most_common(10)
    print(f"  {'Artist':<30} {'Tracks':>6}")
    print(f"  {'-'*38}")
    for artist, count in counts:
        bar = "█" * count
        print(f"  {artist:<30} {count:>4}  {bar}")

sp = connect()
playlists = get_playlists(sp)

print("\nEnter playlist number to analyse: ", end="")
choice = int(input()) - 1
tracks = get_tracks(sp, playlists[choice])
features = get_audio_features(sp, tracks)
get_genre_breakdown(sp, tracks)
analyse_mood(features)
top_artists(tracks)