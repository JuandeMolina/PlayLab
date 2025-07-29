import re
from spotify_api import sp_user, get_playlist_data
from playlist_analyzer import Playlist
from song import Song
from artist import Artist


def extract_playlist_id(url: str) -> str:
    """
    Extrae el ID de la playlist de una URL de Spotify.
    """
    match = re.search(r"playlist/([a-zA-Z0-9]+)", url)
    if match:
        return match.group(1)
    else:
        raise ValueError(
            "URL inválida. Asegúrate de pegar un enlace de playlist de Spotify válido."
        )


def main():
    print("Bienvenido a PlayLab (Modo Terminal)")

    if not sp_user:
        print(
            "Error: No se pudo conectar con Spotify. Por favor, revisa tu conexión a internet o las credenciales de la API."
        )
        return

    playlist_url = input("Pega la URL de tu playlist: ").strip()

    try:
        playlist_id = extract_playlist_id(playlist_url)
    except ValueError as e:
        print("Error: ", e)
        return

    print("Extrayendo datos de la playlist...")

    try:
        playlist: Playlist = get_playlist_data(sp_user, playlist_id)

        if not playlist.songs:
            print("No se encontraron pistas en la playlist o la playlist está vacía.")
            return

        print(f"\n--- Análisis de la playlist '{playlist.name}' completado ---\n")
        print(f"Número de pistas: {playlist.num_songs}")
        print(f"Número de artistas: {playlist.num_artists}")
        print(f"Duración: {playlist.duration_minutes} minutos")

        print("\n--- Primeras 5 canciones de la playlist (con detalles) ---")
        for i, song in enumerate(playlist.songs[:5]):  # Muestra solo las primeras 5
            print(
                f"{i+1}. {song}"
            )
        if playlist.artist_frequencies:
            print("\n--- Artistas con mas apariciones en la lista ---")
            for i, (artist, count) in enumerate(playlist.artist_frequencies.most_common(5)):
                print(f"{i+1}. {artist}: {count} canciones")
        else:
            print("No hemos encontrado a ningun artista repetido")

    except Exception as e:
        print(f"\nHa ocurrido un error mientras analizábamos tu playlist: {e}")


if __name__ == "__main__":
    main()
