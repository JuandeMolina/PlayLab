import spotipy
from spotipy.oauth2 import SpotifyOAuth
import logging
import time
from song import Song
from artist import Artist
from playlist_analyzer import Playlist

# Configuración de logging
logging.basicConfig(
    filename="playlab.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Autenticación del usuario (credenciales, scope y redirección)
CLIENT_ID = "83e88610af8d4c299b486ea277cc6f6f"
CLIENT_SECRET = (
    "ec2ec1784d664a9e8baf24dae4a9a457"
)
REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPE = "playlist-read-private playlist-read-collaborative"

sp_user = None
try:
    sp_user = spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE,
            open_browser=True,
            cache_path=".cache-playlab",
        )
    )
    sp_user.me()
    logging.info("Autenticación con Spotify exitosa.")
except Exception as e:
    logging.error(f"Error durante la autenticación de Spotify: {e}")
    sp_user = None


def get_playlist_tracks(sp_client: spotipy.Spotify, playlist_id: str) -> list[Song]:
    if not sp_client:
        logging.error(
            "Cliente de Spotify no inicializado. No se pueden obtener pistas."
        )
        return []

    songs = []
    offset = 0
    try:
        while True:
            response = sp_client.playlist_items(
                playlist_id,
                offset=offset,
                fields="items.track(id,name,artists(id,name),album(name),duration_ms,explicit),total",
                additional_types=["track"],
            )
            items = response["items"]
            if not items:
                break
            for item in items:
                track_data = item.get("track")
                if track_data and track_data.get("id"):

                    artists_data_raw = track_data.get("artists", [])
                    artists = [
                        Artist(
                            id=artist_info.get("id", "unknown"),
                            name=artist_info.get("name", "Unknown Artist"),
                        )
                        for artist_info in artists_data_raw
                    ]

                    song = Song(
                        id=track_data["id"],
                        title=track_data["name"],
                        artists=artists,  # Ahora pasamos una lista de objetos Artist
                        album=track_data.get("album", {}).get(
                            "name", "Álbum Desconocido"
                        ),
                        duration_ms=track_data.get("duration_ms", 0),
                        explicit=track_data.get("explicit", False),
                    )
                    songs.append(song)
            offset += len(items)
    except spotipy.SpotifyException as e:
        logging.error(
            f"Error de Spotify al obtener pistas de la playlist {playlist_id}: {e}"
        )
        raise
    except Exception as e:
        logging.error(
            f"Error inesperado al obtener pistas de la playlist {playlist_id}: {e}"
        )
        raise

    logging.info(f"Se obtuvieron {len(songs)} pistas de la playlist.")
    return songs


def get_playlist_data(sp_client: spotipy.Spotify, playlist_id: str) -> Playlist:
    """
    Obtiene los datos de la playlist y sus canciones, y devuelve un objeto Playlist.
    """
    if not sp_client:
        raise Exception(
            "El cliente de Spotify no se pudo inicializar. Verifica tus credenciales o conexión."
        )

    try:
        playlist_info = sp_client.playlist(playlist_id, fields="name")
        playlist_name = playlist_info.get("name", "Nombre desconocido")
    except spotipy.SpotifyException as e:
        logging.error(
            f"Error de Spotify al obtener información de la playlist {playlist_id}: {e}"
        )
        raise
    except Exception as e:
        logging.error(
            f"Error inesperado al obtener información de la playlist {playlist_id}: {e}"
        )
        raise

    songs = get_playlist_tracks(sp_client, playlist_id)

    playlist_object = Playlist(id=playlist_id, name=playlist_name, songs=songs)

    return playlist_object