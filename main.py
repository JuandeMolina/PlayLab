from spotify_api import sp, get_playlist_data, analyze_playlist

def extract_playlist_id(url):
    if "playlist/" in url:
        return url.split("playlist/")[1].split("?")[0]
    else:
        raise ValueError("URL invalida. Asegurate de pegar el enlace de una playlist de Spotify")

def main():
    print("Bienvenido a PlayLab (Modo Terminal)")
    playlist_url = input("Pega la URL de tu playlist: ").strip()

    try:
        playlist_id = extract_playlist_id(playlist_url)
    except ValueError as e:
        print("Error: ", e)
        return
    
    print("Extrayendo datos de la playlist")

    try:
        tracks, audio_features = get_playlist_data(sp, playlist_id)
        analysis = analyze_playlist(tracks, audio_features)

        print("\n✅ Analisis de la playlist completado:\n")
        print(f"🎶 Numero de pistas: {analysis['num_tracks']}")
        print(f"👥 Numero de artistas: {analysis['num_artists']}")
        print(f"⏱️ Duracion: {analysis['duration_minutes']} minutes")
        print(f"⚡ Energia: {analysis['avg_energy']}")
        print(f"💃 Bailable: {analysis['avg_danceability']}")
        print(f"😊 Positividad: {analysis['avg_valence']}")
        print(f"🎼 Tempo: {analysis['avg_tempo']} BPM")

    except Exception as e:
        print("Ha ocurrido un error mientras analizabamos tu playlist: ", e)

if __name__ == "__main__":
    main()