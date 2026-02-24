# Spotify Playlist Analyser
# v8: cleaner output, better error handling throughout

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from collections import Counter

CLIENT_ID = "your_client_id_here"
CLIENT_SECRET = "your_client_secret_here"
REDIRECT_URI = "http://127.0.0.1:8888/callback"

SCOPE = "playlist-read-private user-library-read"

DIVIDER = "=" * 50

def connect():
    print(f"\n{DIVIDER}")
    print("  SPOTIFY PLAYLIST ANALYSER")
    print(DIVIDER)
    print("\n[*] Connecting to Spotify...\n")
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE
        ))
        user = sp.current_user()
        print(f"[+] Connected as: {user['display_name']}\n")
        return sp
    except Exception as e:
        print(f"[-] Connection failed: {e}")
        exit()

def get_playlists(sp):
    print("[*] Fetching your playlists...\n")
    try:
        playlists = sp.current_user_playlists()
        results = []
        for i, playlist in enumerate(playlists['items']):
            print(f"  {i + 1}. {playlist['name']} ({playlist['tracks']['total']} tracks)")
            results.append(playlist)
        return results
    except Exception as e:
        print(f"[-] Could not fetch playlists: {e}")
        exit()

def get_tracks(sp, playlist):
    print(f"\n[*] Fetching tracks from: {playlist['name']}...\n")
    tracks = []
    try:
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
        print(f"[+] {len(tracks)} tracks loaded.")
    except Exception as e:
        print(f"[-] Could not fetch tracks: {e}")
    return tracks

def get_audio_features(sp, tracks):
    ids = [t['id'] for t in tracks if t['id']]
    features = []
    try:
        for i in range(0, len(ids), 100):
            batch = ids[i:i + 100]
            result = sp.audio_features(batch)
            if result:
                features.extend([f for f in result if f])
    except Exception as e:
        print(f"[-] Could not fetch audio features: {e}")
    return features

def get_genre_breakdown(sp, tracks):
    artist_ids = list(set([t['artist_id'] for t in tracks if t['artist_id']]))
    genres = []
    try:
        for i in range(0, len(artist_ids), 50):
            batch = artist_ids[i:i + 50]
            result = sp.artists(batch)
            for artist in result['artists']:
                genres.extend(artist['genres'])
    except Exception as e:
        print(f"[-] Could not fetch genre data: {e}")
    return Counter(genres).most_common(10)

def analyse_mood(features):
    if not features:
        return None
    avg_energy = sum(f['energy'] for f in features) / len(features)
    avg_valence = sum(f['valence'] for f in features) / len(features)
    avg_dance = sum(f['danceability'] for f in features) / len(features)
    avg_tempo = sum(f['tempo'] for f in features) / len(features)
    avg_acoustic = sum(f['acousticness'] for f in features) / len(features)

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

    return {
        'energy': avg_energy,
        'valence': avg_valence,
        'danceability': avg_dance,
        'tempo': avg_tempo,
        'acousticness': avg_acoustic,
        'vibe': vibe
    }

def top_artists(tracks):
    return Counter([t['artist'] for t in tracks]).most_common(10)

def print_report(playlist, tracks, genres, mood, artists):
    print(f"\n{DIVIDER}")
    print(f"  REPORT: {playlist['name']}")
    print(DIVIDER)
    print(f"  Total tracks: {len(tracks)}")

    print(f"\n  TOP ARTISTS")
    print(f"  {'-'*40}")
    for artist, count in artists:
        print(f"  {artist:<30} {count} tracks")

    print(f"\n  TOP GENRES")
    print(f"  {'-'*40}")
    if genres:
        for genre, count in genres:
            print(f"  {genre:<30} ({count})")
    else:
        print("  No genre data available.")

    print(f"\n  MOOD AND ENERGY")
    print(f"  {'-'*40}")
    if mood:
        print(f"  Energy:       {mood['energy']:.2f} / 1.0")
        print(f"  Mood:         {mood['valence']:.2f} / 1.0  (higher = happier)")
        print(f"  Danceability: {mood['danceability']:.2f} / 1.0")
        print(f"  Tempo:        {mood['tempo']:.0f} BPM")
        print(f"  Acousticness: {mood['acousticness']:.2f} / 1.0")
        print(f"\n  Vibe: {mood['vibe']}")
    else:
        print("  No audio feature data available.")
        print("  Note: audio features require Spotify Premium.")

    print(f"\n{DIVIDER}\n")

sp = connect()
playlists = get_playlists(sp)

print("\nEnter playlist number to analyse: ", end="")
try:
    choice = int(input()) - 1
    if choice < 0 or choice >= len(playlists):
        print("[-] Invalid selection.")
        exit()
except ValueError:
    print("[-] Enter a number.")
    exit()

selected = playlists[choice]
tracks = get_tracks(sp, selected)
features = get_audio_features(sp, tracks)
genres = get_genre_breakdown(sp, tracks)
mood = analyse_mood(features)
artists = top_artists(tracks)

print_report(selected, tracks, genres, mood, artists)