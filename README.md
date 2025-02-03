# Music Downloader Project

Bu proje, Spotify çalma listelerinden şarkıları çekip YouTube üzerinden indirmenizi sağlayan bir Python uygulamasıdır.

## Kurulum

1. Python 3.11 veya üzeri sürümü yükleyin
2. Sanal ortam oluşturun:
```bash
uv venv --python 3.11
```

3. Sanal ortamı aktifleştirin:
- Mac/Linux için:
```bash
source .venv/bin/activate
```
- Windows için:
```bash
.venv\Scripts\activate
```

4. Gerekli paketleri yükleyin:
```bash
uv pip install spotipy python-dotenv browser-use langchain-google-genai yt_dlp
playwright install
```

5. `.env` dosyası oluşturun ve gerekli API anahtarlarını ekleyin:
```
GOOGLE_API_KEY=your_google_api_key
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
```

## Spotify API Kurulumu

1. [Spotify Developer Dashboard](https://developer.spotify.com/dashboard) adresine gidin
2. Giriş yapın veya hesap oluşturun
3. "Create an App" butonuna tıklayın
4. Uygulama adı ve açıklaması girin
5. Oluşturulan uygulamanın Client ID ve Client Secret bilgilerini `.env` dosyasına ekleyin

## Kullanım

Proje üç ana bileşenden oluşur:

### 1. Spotify Playlist Parser (`spotify_playlist_parser.py`)
- Spotify çalma listesinden şarkıları çeker
- Çalma listesi URL'sini kullanarak şarkı isimlerini alır
- Şarkı listesini `download-song-list.txt` dosyasına kaydeder
- Her satırda "Sanatçı - Şarkı Adı" formatında kayıt oluşturur

Çalıştırmak için:
```bash
python spotify_playlist_parser.py
```

Playlist URL'sini `spotify_playlist_parser.py` dosyasında `playlist_url` değişkenine atayın:
```python
playlist_url = "https://open.spotify.com/playlist/your_playlist_id"
```

### 2. YouTube Downloader (`app.py`)
- `download-song-list.txt` dosyasından şarkı listesini okur
- Her şarkı için YouTube'da arama yapar
- Bulunan URL'leri `song_urls.txt` dosyasına kaydeder
- Şarkıları `downloads` klasörüne MP3 formatında indirir
- Hata durumlarını `error.txt` dosyasına loglar

### 3. Direct URL Downloader (`song_urls_downloader.py`)
- `song_urls.txt` dosyasından şarkı URL'lerini okur
- Her şarkıyı doğrudan YouTube'dan indirir
- Daha önce indirilmiş şarkıları atlar
- İndirilen şarkıları `downloads` klasörüne MP3 formatında kaydeder
- Hata durumlarını `error.txt` dosyasına loglar

Çalıştırmak için:
```bash
python song_urls_downloader.py
```

## Dosya Yapısı

- `download-song-list.txt`: İndirilecek şarkıların listesi
- `song_urls.txt`: Bulunan YouTube URL'leri
- `error.txt`: Hata logları
- `downloads/`: İndirilen MP3 dosyalarının klasörü

## Çalışma Akışı

1. Spotify çalma listesinden şarkıları çekmek için:
   ```bash
   python spotify_playlist_parser.py
   ```

2. Şarkıların YouTube URL'lerini bulmak için:
   ```bash
   python app.py
   ```

3. URL'lerden şarkıları indirmek için:
   ```bash
   python song_urls_downloader.py
   ```

Ya da doğrudan `song_urls.txt` dosyanız varsa, 3. adımı tek başına kullanabilirsiniz.

## Notlar

- FFmpeg yüklü olmalıdır (ses dönüşümü için gerekli)
- İndirme işlemi sırasında rate-limit'e takılmamak için rastgele beklemeler eklenmiştir
- Hata durumunda program durmaz, diğer şarkılara devam eder ve hataları loglar
- Spotify API rate limitlerine dikkat edin
- Çalma listesi public (herkese açık) olmalıdır
- Var olan dosyalar tekrar indirilmez