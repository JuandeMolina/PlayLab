# playlist_analyzer.py

from song import Song
from artist import Artist
from collections import Counter
from utils import format_duration_ms


class Playlist:
    def __init__(self, id: str, name: str, songs: list[Song]):
        self.id = id
        self.name = name
        self.songs = songs
        self._calculate_stats()

    def _calculate_stats(self):
        """
        Calcula varias estadísticas sobre la playlist y las almacena como atributos.
        No incluye estadísticas basadas en audio_features.
        """
        self.num_songs = len(self.songs)
        unique_artists = set()
        self.total_duration_ms = 0  # Inicialización correcta de total_duration_ms
        all_artists_names = []

        # Inicialización de estadísticas de colaboración y explícitas
        self.num_explicit_songs = 0
        self.num_collaborative_songs = 0
        self.artist_collaboration_counts = Counter()

        # Inicialización de nuevas estadísticas solicitadas
        self.album_counts = Counter()  # Para contar frecuencias de álbumes

        # Inicialización de shortest_song y longest_song directamente con MS
        self.shortest_song = {"title": "N/A", "duration_ms": float("inf")}
        self.longest_song = {"title": "N/A", "duration_ms": 0}

        for song in self.songs:
            self.total_duration_ms += song.duration_ms  # Acumula aquí

            # Estadísticas de canciones explícitas
            if song.explicit:
                self.num_explicit_songs += 1

            # Estadísticas de canciones colaborativas
            if (
                len(song.artists) > 1
            ):  # Una canción es colaborativa si tiene más de un artista
                self.num_collaborative_songs += 1
                for artist in song.artists:
                    self.artist_collaboration_counts[artist.name] += 1

            # Conteo de artistas para frecuencias
            for artist in song.artists:
                unique_artists.add(artist.name)
                all_artists_names.append(artist.name)

            # Conteo de álbumes
            self.album_counts[song.album] += 1

            # Determinación de la canción más corta y más larga usando duration_ms
            # Solo consideramos canciones con duración > 0 para evitar duraciones "infinitas" o errores
            if (
                song.duration_ms > 0
                and song.duration_ms < self.shortest_song["duration_ms"]
            ):
                self.shortest_song["duration_ms"] = song.duration_ms
                self.shortest_song["title"] = song.title

            if song.duration_ms > self.longest_song["duration_ms"]:
                self.longest_song["duration_ms"] = song.duration_ms
                self.longest_song["title"] = song.title

        # Finalización de cálculos basados en iteraciones
        self.num_non_collaborative_songs = self.num_songs - self.num_collaborative_songs
        self.num_artists = len(unique_artists)
        self.duration_minutes = round(
            self.total_duration_ms / 60000, 2
        )  # Esta variable se puede mantener para un resumen general si se desea
        self.artist_frequencies = Counter(all_artists_names)

        # Nuevas estadísticas derivadas de album_counts
        self.num_unique_albums = len(self.album_counts)
        # most_common(1) devuelve una lista de una tupla, ej: [('Album A', 10)]
        self.most_represented_album = (
            self.album_counts.most_common(1)[0] if self.album_counts else ("N/A", 0)
        )

    def get_summary(self) -> dict:
        """
        Retorna un resumen de las estadísticas de la playlist.
        """
        return {
            "name": self.name,
            "num_songs": self.num_songs,
            "num_artists": self.num_artists,
            "duration_minutes": self.duration_minutes,
            "total_duration_ms": self.total_duration_ms,  # Añadir total_duration_ms al summary
            "artist_frequencies": self.artist_frequencies,
            "num_explicit_songs": self.num_explicit_songs,
            "num_collaborative_songs": self.num_collaborative_songs,  # Corregido: Ahora devuelve el número, no el Counter
            "num_non_collaborative_songs": self.num_non_collaborative_songs,
            "artist_collaboration_counts": self.artist_collaboration_counts,
            "num_unique_albums": self.num_unique_albums,
            "most_represented_album": self.most_represented_album,
            "shortest_song": self.shortest_song,  # Ya tienen duration_ms
            "longest_song": self.longest_song,  # Ya tienen duration_ms
        }

    def __str__(self) -> str:
        """
        Representación en cadena de la playlist.
        """
        return (
            f"Playlist: '{self.name}' (ID: {self.id})\n"
            f"  Número de canciones: {self.num_songs}\n"
            f"  Número de artistas únicos: {self.num_artists}\n"
            f"  Duración total: {format_duration_ms(self.total_duration_ms)}\n"
            f"  Canciones explícitas: {self.num_explicit_songs}\n"
            f"  Canciones colaborativas: {self.num_collaborative_songs}\n"
            f"  Canciones no colaborativas: {self.num_non_collaborative_songs}\n"
            f"  Canción más corta: '{self.shortest_song['title']}' ({format_duration_ms(self.shortest_song['duration_ms'])})\n"
            f"  Canción más larga: '{self.longest_song['title']}' ({format_duration_ms(self.longest_song['duration_ms'])})\n"
            f"  Número de álbumes únicos: {self.num_unique_albums}\n"
            f"  Álbum más representado: '{self.most_represented_album[0]}' ({self.most_represented_album[1]} canciones)\n"
        )

    def __repr__(self) -> str:
        return (
            f"Playlist(id='{self.id}', name='{self.name}', num_songs={self.num_songs})"
        )
