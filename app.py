from langchain_openai import ChatOpenAI
from browser_use import Agent
from dotenv import load_dotenv
import asyncio
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import yt_dlp
import re

load_dotenv()

# API anahtarını ortam değişkenlerinden al
google_api_key = os.getenv("GOOGLE_API_KEY")

def extract_url_from_result(result):
    # URL'yi bulmak için regex kullan
    url_pattern = r'https://www\.youtube\.com/watch\?v=[\w-]+'
    match = re.search(url_pattern, str(result))
    if match:
        return match.group(0)
    return None

def download_audio(url, output_filename):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f"{output_filename}.mp3"  # Doğrudan .mp3 uzantısı ekle
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
            print(f"Şarkı başarıyla indirildi: {output_filename}.mp3")
            return True
        except Exception as e:
            print(f"İndirme hatası: {str(e)}")
            return False

# API anahtarını llm oluştururken kullan
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    temperature=0,
    max_tokens=None,
    timeout=None,
    google_api_key=google_api_key
)

async def main():
    # Önce şarkıyı bulmak için agent'ı kullan
    search_agent = Agent(
        task="""Search for 'Dedüblüman Çözemessin' song on YouTube. 
        1. Find a working video URL (make sure the video is available)
        2. Verify that it's the official music video
        3. Return only the verified video URL
        """,
        llm=llm,
    )
    
    # Agent'dan gelen sonucu al
    result = await search_agent.run()
    print(f"Agent'dan gelen sonuç: {result}")
    
    # URL'yi çıkar
    url = extract_url_from_result(result)
    if url:
        print(f"Bulunan URL: {url}")
        try:
            # Şarkıyı indir
            if download_audio(url, "Dedubluman-Cozemessin"):
                print("İşlem tamamlandı!")
            else:
                print("İndirme işlemi başarısız oldu.")
        except Exception as e:
            print(f"Bir hata oluştu: {str(e)}")
    else:
        print("URL bulunamadı!")

asyncio.run(main())