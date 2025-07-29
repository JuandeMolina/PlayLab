from song import Song
from artist import Artist
from collections import Counter

class Playlist:
    def __init__(self, id: str, name: str, songs: list[Song]):
        self.id = id
        self.name = name
        self.songs = songs
        self._calculate_stats()

    def _calculate_stats(self):
        self.num_songs = len(self.songs)
        unique_artists = set()
        total_duration_ms = 0
        all_artists_names = []

        for song in self.songs:
            total_duration_ms += song.duration_ms
            for artist in song.artists:
                unique_artists.add(artist.name)
                all_artists_names.append(artist.name)

        self.num_artists = len(unique_artists)
        self.duration_minutes = round(total_duration_ms / 60000, 2)
        self.artist_frequencies = Counter(all_artists_names)

    def get_summary(self) -> dict:
        return {
            "name": self.name,
            "num_songs": self.num_songs,
            "num_artists": self.num_artists,
            "duration_minutes": self.duration_minutes,
            "artist_frequencies": self.artist_frequencies
        }

    def __str__(self):
        return (
            f"Playlist: '{self.name}' (ID: {self.id})\n"
            f"  Número de canciones: {self.num_songs}\n"
            f"  Artistas únicos: {self.num_artists}\n"
            f"  Duración total: {self.duration_minutes} minutos"
        )

    def __repr__(self):
        return f"Playlist(id='{self.id}', name='{self.name}', num_songs={self.num_songs})"
