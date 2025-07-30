import re
from spotify_api import sp_user, get_playlist_data
from playlist_analyzer import Playlist
from song import Song
from artist import Artist
from utils import format_duration_ms
import sys


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
        print(f"Número de artistas únicos: {playlist.num_artists}")
        print(f"Duración total: {format_duration_ms(playlist.total_duration_ms)}")
        print(
            f"Canción más corta: '{playlist.shortest_song['title']}' ({format_duration_ms(playlist.shortest_song['duration_ms'])})"
        )
        print(
            f"Canción más larga: '{playlist.longest_song['title']}' ({format_duration_ms(playlist.longest_song['duration_ms'])})"
        )
        print(f"Canciones explícitas: {playlist.num_explicit_songs}")

        # Nuevas estadísticas de canciones colaborativas
        print(f"Canciones colaborativas: {playlist.num_collaborative_songs}")
        print(f"Canciones no colaborativas: {playlist.num_non_collaborative_songs}")

        print("\n--- Primeras 5 canciones de la playlist (con detalles) ---")
        for i, song in enumerate(playlist.songs[:5]):
            print(f"{i+1}. {song}")

        if playlist.artist_frequencies:
            print("\n--- Artistas con más apariciones en la lista ---")
            for i, (artist, count) in enumerate(
                playlist.artist_frequencies.most_common(5)
            ):
                print(f"{i+1}. {artist}: {count} canciones")
        else:
            print("No hemos encontrado a ningún artista.")

        # TOP 5 ARTISTAS CON MÁS COLABORACIONES
        top_collaborators = [
            (artist, count)
            for artist, count in playlist.artist_collaboration_counts.most_common(5)
            if count > 0
        ]

        if top_collaborators:
            print("\n--- Top 5 Artistas con más Colaboraciones ---")
            for i, (artist, count) in enumerate(top_collaborators):
                print(f"{i+1}. {artist}: {count} colaboraciones")
        else:
            print(
                "\nNo se encontraron colaboraciones por artistas individuales en la playlist."
            )

        option: str = input("\n¿Quieres una lista de todos los artistas de tu playlist, ordenados por número de apariciones? (Y/n): ").strip().lower()
        if option.lower() == "n":
            print(
                "Has elegido no mostrar la lista completa de artistas. Saliendo del programa."
            )
            sys.exit()
        elif option == "y":
            if playlist.artist_frequencies:
                print(
                    "\n--- Todos los artistas de la playlist (por número de apariciones) ---"
                )
                for i, (artist, count) in enumerate(
                    playlist.artist_frequencies.most_common()
                ):
                    print(
                        f"{i+1}. {artist}: {count} canci{'ones' if count > 1 else 'ón'}"
                    )
            else:
                print("\nNo se encontraron artistas en la playlist para listar.")
        else:
            print("\nOpción no válida. Continuando con el resto del análisis.")

    except Exception as e:
        print(f"\nHa ocurrido un error mientras analizábamos tu playlist: {e}")


if __name__ == "__main__":
    main()
