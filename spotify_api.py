import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Authentication
CLIENT_ID = "28f342cc048c4d8f875db384073098b0"
CLIENT_SECRET = "6277680d1aa44030b56abc7aa08e3475"
REDIRECT_URI = "http://localhost:8888/callback"
SCOPE = "playlist-read-private playlist-read-collaborative"

# Create an authentified Spotipy instance
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
    )
)

# Get playlist data
def get_playlist_tracks(sp, playlist_id):
    tracks = []
    offset = 0
    while True:
        response = sp.playlist_items(
            playlist_id,
            offset=offset,
            fields="items.track(id,name,artists(name),duration_ms),total",
            additional_types=["track"],
        )
        items = response["items"]
        if not items:
            break

        for item in items:
            track = item.get("track")
            if track:
                tracks.append(track)
        offset += len(items)

    return tracks


def get_audio_features_in_batches(sp, track_ids):
    all_features = []
    for i in range(0, len(track_ids), 100):
        batch = track_ids[i : i + 100]
        features_batch = sp.audio_features(batch)
        features_batch = [f for f in features_batch if f]
        all_features.extend(features_batch)
    return all_features


def get_playlist_data(sp, playlist_id):
    tracks = get_playlist_tracks(sp, playlist_id)
    track_ids = [track["id"] for track in tracks if track["id"]]
    audio_features = get_audio_features_in_batches(sp, track_ids)
    return tracks, audio_features


# Playlist analysis
def analyze_playlist(tracks, audio_features):
    num_tracks = len(tracks)
    unique_artists = set()
    total_duration_ms = 0

    for track in tracks:
        total_duration_ms += track.get("duration_ms", 0)
        for artist in track.get("artists", []):
            unique_artists.add(artist["name"])

    duration_minutes = round(total_duration_ms / 60000, 2)
    num_artists = len(unique_artists)

    total_energy = 0
    total_danceability = 0
    total_valence = 0
    total_tempo = 0
    count = 0

    for f in audio_features:
        if f:
            total_energy += f.get("energy", 0)
            total_danceability += f.get("danceability", 0)
            total_valence += f.get("valence", 0)
            total_tempo += f.get("tempo", 0)
            count += 1

    if count > 0:
        avg_energy = round(total_energy / count, 3)
        avg_danceability = round(total_danceability / count, 3)
        avg_valence = round(total_valence / count, 3)
        avg_tempo = round(total_tempo / count, 1)
    else:
        avg_energy = avg_danceability = avg_valence = avg_tempo = 0

    return {
        "num_tracks": num_tracks,
        "num_artists": num_artists,
        "duration_minutes": duration_minutes,
        "avg_energy": avg_energy,
        "avg_danceability": avg_danceability,
        "avg_valence": avg_valence,
        "avg_tempo": avg_tempo,
    }
