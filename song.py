from artist import Artist

class Song:
    def __init__(
        self,
        id: str,
        album: str,
        artists: list[Artist],
        duration_ms: int,
        explicit: bool,
        title: str,
    ):
        self.id = id
        self.album = album
        self.artists = artists
        self.duration_ms = duration_ms
        self.explicit = explicit
        self.title = title

    @property
    def duration_seconds(self) -> int:
        return int(self.duration_ms / 1000)

    def __str__(self) -> str:
        explicit_tag = "[E]" if self.explicit else ""
        artist_names = [artist.name for artist in self.artists]
        return f"'{self.title}' {explicit_tag} by {', '.join(artist_names)} from '{self.album}' ({self.duration_seconds:.2f}s)"

    def __repr__(self) -> str:
        return (f"Song(id='{self.id}', title='{self.title}', artists={self.artists}, "
                f"album='{self.album}', duration_ms={self.duration_ms}, explicit={self.explicit})")