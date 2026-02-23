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
    # grab unique artist ids and batch them — 50 per request is the limit
    artist_ids = list(set([t['artist_id'] for t in tracks if t['artist_id']]))
    genres = []
    for i in range(0, len(artist_ids), 50):
        batch = artist_ids[i:i + 50]
        result = sp.artists(batch)
        for artist in result['artists']:
            genres.extend(artist['genres'])

    if not genres:
        print("  No genre data found for this playlist.")
        return

    counts = Counter(genres).most_common(10)
    print("  Top genres in this playlist:\n")
    for genre, count in counts:
        bar = "█" * count
        print(f"  {genre:<30} {bar} ({count})")

    return counts

sp = connect()
playlists = get_playlists(sp)

print("\nEnter playlist number to analyse: ", end="")
choice = int(input()) - 1
tracks = get_tracks(sp, playlists[choice])
features = get_audio_features(sp, tracks)
get_genre_breakdown(sp, tracks)
