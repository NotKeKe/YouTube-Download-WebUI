from pytubefix import AsyncYouTube
import yt_dlp
import asyncio
from pprint import pp
from pathlib import Path
import json

CURR_DIR = Path(__file__).parent
url = 'https://youtu.be/X6K1cHQNs-I?si=94gHgyS60Idquz3y'

YTDL_OPTIONS = {
    'format': 'bestvideo+bestaudio/best',
    'noplaylist': True,          # 如果輸入是播放清單，只下載當前影片
    'quiet': True,               # 禁止在 console 輸出大量訊息
    'no_warnings': True,         # 禁止輸出警告
    'default_search': 'auto',    # 允許輸入關鍵字搜尋 (例如: "play 告白氣球")
    'source_address': '0.0.0.0', # 強制使用 IPv4 (解決某些 YouTube 阻擋 IPv6 的問題)
    
    # 以下選項是為了讓機器人運作更穩定
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    
    # 這裡雖然設了 output template，但因為我們不會實際下載，所以只是備用
    'restrictfilenames': True,
}

async def main():
    with yt_dlp.YoutubeDL(YTDL_OPTIONS) as ydl: # type: ignore
        info = ydl.extract_info(url, download=False)

        with open(CURR_DIR / 'test.json', 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2, ensure_ascii=False)

        print(f"url: '{info.get('url')}'")

asyncio.run(main())