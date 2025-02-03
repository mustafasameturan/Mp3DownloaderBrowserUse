import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv

load_dotenv()

def get_playlist_tracks(playlist_url):
    """Spotify çalma listesindeki şarkıları çeker"""
    try:
        # Spotify API kimlik bilgileri
        client_credentials_manager = SpotifyClientCredentials(
            client_id=os.getenv('SPOTIFY_CLIENT_ID'),
            client_secret=os.getenv('SPOTIFY_CLIENT_SECRET')
        )
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
        # Playlist ID'sini URL'den çıkar
        if "?" in playlist_url:
            playlist_id = playlist_url.split('/')[-1].split('?')[0]
        else:
            playlist_id = playlist_url.split('/')[-1]
            
        print(f"Playlist ID: {playlist_id}")
        
        # Çalma listesi bilgilerini al
        results = sp.playlist_tracks(playlist_id)
        tracks = results['items']
        
        # Sonraki sayfaları da al (100'den fazla şarkı varsa)
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])
        
        print(f"Toplam {len(tracks)} şarkı bulundu.")
        
        # Şarkı listesini oluştur
        song_list = []
        for track in tracks:
            try:
                # Şarkı bilgilerini al
                track_info = track['track']
                if track_info is None:  # Bazen silinen şarkılar None olabilir
                    continue
                    
                # Sanatçı isimlerini al
                artists = [artist['name'] for artist in track_info['artists']]
                artist_names = artists[0]  # İlk sanatçıyı al
                
                # Şarkı adını al
                song_name = track_info['name']
                
                # Formatı oluştur: "Sanatçı - Şarkı"
                song_entry = f"{artist_names} - {song_name}"
                song_list.append(song_entry)
                print(f"Eklendi: {song_entry}")
                
            except Exception as e:
                print(f"Şarkı işlenirken hata: {str(e)}")
                continue
        
        return song_list
        
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")
        return []

def save_to_file(songs, filename="download-song-list.txt"):
    """Şarkı listesini dosyaya kaydeder"""
    try:
        # Dosyayı UTF-8 ile yaz
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(songs))
        print(f"\nToplam {len(songs)} şarkı {filename} dosyasına kaydedildi.")
    except Exception as e:
        print(f"Dosya kaydetme hatası: {str(e)}")

def main():
    # Spotify çalma listesi URL'si
    playlist_url = "https://open.spotify.com/playlist/4qG0WL2FYL3j88jW9qf37F"
    
    print("Spotify çalma listesi işleniyor...")
    songs = get_playlist_tracks(playlist_url)
    
    if songs:
        save_to_file(songs)
        print("\nİşlem başarıyla tamamlandı!")
    else:
        print("\nHata: Şarkı listesi boş veya bir hata oluştu!")

if __name__ == "__main__":
    main() 