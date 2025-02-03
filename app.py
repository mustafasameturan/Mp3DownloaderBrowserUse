from browser_use import Agent
from dotenv import load_dotenv
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import yt_dlp
import re
from datetime import datetime
import random

load_dotenv()

# API anahtarını ortam değişkenlerinden al
google_api_key = os.getenv("GOOGLE_API_KEY")

def log_error(song_name, error_type, error_message):
    """Hataları error.txt dosyasına kaydeder, ffmpeg hatalarını es geçer"""
    # ffmpeg hatalarını kontrol et
    if "ffprobe and ffmpeg not found" in str(error_message):
        print("FFmpeg hatası: Lütfen FFmpeg'i yükleyin")
        return
        
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_line = f"[{timestamp}] {song_name} | {error_type} | {error_message}\n"
    
    with open("error.txt", "a", encoding="utf-8") as f:
        f.write(error_line)

def extract_url_from_result(result):
    # URL'yi bulmak için regex kullan
    url_pattern = r'https://www\.youtube\.com/watch\?v=[\w-]+'
    match = re.search(url_pattern, str(result))
    if match:
        return match.group(0)
    return None

def download_audio(url, output_filename):
    # downloads klasörünü oluştur
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f"downloads/{output_filename}.mp3"  # downloads klasörüne kaydet
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            print(f"Şarkı başarıyla indirildi: downloads/{output_filename}.mp3")
            return True
    except Exception as e:
        error_msg = str(e)
        print(f"İndirme hatası: {error_msg}")
        log_error(output_filename, "DOWNLOAD_ERROR", error_msg)
        return False

async def find_song_url(song_name, llm):
    try:
        search_agent = Agent(
            task=f"""Search for '{song_name}' song on YouTube. 
            1. Find a working video URL (make sure the video is available)
            2. Verify that it's the official music video
            3. Return only the verified video URL
            """,
            llm=llm,
        )
        
        result = await search_agent.run()
        url = extract_url_from_result(result)
        
        if not url:
            error_msg = "URL bulunamadı veya geçersiz format"
            log_error(song_name, "URL_EXTRACTION_ERROR", error_msg)
            return None
            
        return url
    except Exception as e:
        error_msg = str(e)
        log_error(song_name, "SEARCH_ERROR", error_msg)
        return None

async def read_song_list():
    """download-song-list.txt dosyasından şarkı listesini okur"""
    try:
        if not os.path.exists('download-song-list.txt'):
            print("Hata: download-song-list.txt dosyası bulunamadı!")
            print("Lütfen her satıra bir şarkı adı gelecek şekilde download-song-list.txt dosyası oluşturun.")
            return []
            
        with open('download-song-list.txt', 'r', encoding='utf-8') as f:
            # Boş satırları ve baştaki/sondaki boşlukları temizle
            songs = [line.strip() for line in f if line.strip()]
            
        if not songs:
            print("Uyarı: download-song-list.txt dosyası boş!")
            return []
            
        print(f"Toplam {len(songs)} şarkı bulundu.")
        return songs
    except Exception as e:
        print(f"Dosya okuma hatası: {str(e)}")
        return []

async def main():
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0,
            max_tokens=None,
            timeout=None,
            google_api_key=google_api_key
        )
        
        songs = await read_song_list()
        if not songs:
            print("Program sonlandırılıyor: Şarkı listesi boş!")
            return
            
        failed_songs = []
        urls_file = "song_urls.txt"
        
        # URLs dosyasını temizle
        open(urls_file, 'w', encoding='utf-8').close()
        
        print("1. Aşama: URL'ler bulunuyor...")
        
        for i, song in enumerate(songs):
            try:
                if i > 0:
                    wait_time = random.randint(4, 7)
                    print(f"\nBir sonraki arama için {wait_time} saniye bekleniyor...")
                    await asyncio.sleep(wait_time)
                
                print(f"\nAranan şarkı: {song}")
                url = await find_song_url(song, llm)
                if url:
                    print(f"URL bulundu: {url}")
                    # URL'yi hemen dosyaya ekle
                    with open(urls_file, "a", encoding='utf-8') as f:
                        f.write(f"{song}|||{url}\n")
                else:
                    print(f"'{song}' için URL bulunamadı!")
                    failed_songs.append(song)
            except Exception as e:
                error_msg = str(e)
                print(f"Arama hatası: {error_msg}")
                log_error(song, "UNEXPECTED_SEARCH_ERROR", error_msg)
                failed_songs.append(song)
        
        # URL'ler zaten kaydedildi, direkt indirme aşamasına geç
        if os.path.exists(urls_file) and os.path.getsize(urls_file) > 0:
            print("\n2. Aşama: Şarkılar indiriliyor...")
            download_failed = []
            
            with open(urls_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        song_name, url = line.strip().split("|||")
                        print(f"\nİndiriliyor: {song_name}")
                        # Dosya adından geçersiz karakterleri temizle
                        safe_filename = "".join(c for c in song_name if c.isalnum() or c in (' ', '-', '_')).strip()
                        
                        if not download_audio(url, safe_filename):
                            download_failed.append(song_name)
                    except Exception as e:
                        error_msg = str(e)
                        print(f"İndirme işlemi hatası: {error_msg}")
                        log_error(song_name, "DOWNLOAD_PROCESS_ERROR", error_msg)
                        download_failed.append(song_name)
            
            # Sonuç raporu
            print("\n=== İşlem Raporu ===")
            print(f"Toplam şarkı sayısı: {len(songs)}")
            print(f"URL bulunamayan şarkılar: {len(failed_songs)}")
            print(f"İndirilemeyenler: {len(download_failed)}")
            
            if failed_songs:
                print("\nURL bulunamayan şarkılar:")
                for song in failed_songs:
                    print(f"- {song}")
            
            if download_failed:
                print("\nİndirilemeyen şarkılar:")
                for song in download_failed:
                    print(f"- {song}")
        else:
            print("\nHiçbir URL bulunamadı!")
            
    except Exception as e:
        error_msg = str(e)
        print(f"Program hatası: {error_msg}")
        log_error("PROGRAM", "CRITICAL_ERROR", error_msg)

if __name__ == "__main__":
    asyncio.run(main())