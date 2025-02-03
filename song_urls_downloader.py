import yt_dlp
import os
from datetime import datetime

def log_error(song_name, error_type, error_message):
    """Hataları error.txt dosyasına kaydeder"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_line = f"[{timestamp}] {song_name} | {error_type} | {error_message}\n"
    
    with open("error.txt", "a", encoding="utf-8") as f:
        f.write(error_line)

def download_audio(url, output_filename):
    """YouTube URL'sinden ses dosyası indirir"""
    # downloads klasörünü oluştur
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    
    # Dosya zaten varsa indirme
    if os.path.exists(f"downloads/{output_filename}.mp3"):
        print(f"Dosya zaten mevcut: downloads/{output_filename}.mp3")
        return True
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f"downloads/{output_filename}.mp3"
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            print(f"Şarkı başarıyla indirildi: downloads/{output_filename}.mp3")
            return True
    except Exception as e:
        error_msg = str(e)
        # ffmpeg hatalarını kontrol et
        if "ffprobe and ffmpeg not found" in str(error_msg):
            print("FFmpeg hatası: Lütfen FFmpeg'i yükleyin")
            return False
        
        print(f"İndirme hatası: {error_msg}")
        log_error(output_filename, "DOWNLOAD_ERROR", error_msg)
        return False

def main():
    # song_urls.txt dosyasını kontrol et
    if not os.path.exists('song_urls.txt'):
        print("Hata: song_urls.txt dosyası bulunamadı!")
        return
    
    # Dosyadan şarkı listesini oku
    with open('song_urls.txt', 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    total_songs = len(lines)
    print(f"Toplam {total_songs} şarkı bulundu.")
    
    success_count = 0
    failed_count = 0
    skipped_count = 0
    
    for i, line in enumerate(lines, 1):
        try:
            song_name, url = line.split('|||')
            print(f"\n[{i}/{total_songs}] İşleniyor: {song_name}")
            
            # Dosya adından geçersiz karakterleri temizle
            safe_filename = "".join(c for c in song_name if c.isalnum() or c in (' ', '-', '_')).strip()
            
            # Dosya zaten varsa atla
            if os.path.exists(f"downloads/{safe_filename}.mp3"):
                print(f"Atlandı (zaten mevcut): {safe_filename}")
                skipped_count += 1
                continue
            
            if download_audio(url, safe_filename):
                success_count += 1
            else:
                failed_count += 1
                
        except Exception as e:
            error_msg = str(e)
            print(f"Hata: {error_msg}")
            log_error(song_name if 'song_name' in locals() else "UNKNOWN", "PROCESS_ERROR", error_msg)
            failed_count += 1
    
    # Sonuç raporu
    print("\n=== İndirme Raporu ===")
    print(f"Toplam şarkı: {total_songs}")
    print(f"Başarılı: {success_count}")
    print(f"Başarısız: {failed_count}")
    print(f"Atlanan: {skipped_count}")

if __name__ == "__main__":
    main()
