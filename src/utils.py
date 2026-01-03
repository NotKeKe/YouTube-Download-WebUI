from urllib.parse import urlparse, parse_qs
import httpx
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import os
import aiofiles
import logging
import asyncio
import re

from .import scrapetube

logger = logging.getLogger(__name__)

# paths
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

TMP_DIR = DATA_DIR / Path("tmp")
TMP_DIR.mkdir(exist_ok=True)

DOWNLOAD_DIR = DATA_DIR / Path("download")
DOWNLOAD_DIR.mkdir(exist_ok=True)


# 多進程, 因為 yt-dlp 我之前測試的時候 cpu使用率會飆高，我不知道為什麼
MultiExecutor = ProcessPoolExecutor(max_workers=os.cpu_count())

# global httpx client
_limit = httpx.Limits(max_keepalive_connections=20, max_connections=20)
HttpxAsyncClient = httpx.AsyncClient(limits=_limit)
HttpxSyncClient = httpx.Client(limits=_limit)

YTDL_OPTIONS = {
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

async def get_all_video_ids_from_playlist(playlist_id: str) -> list:
    '''用 playlist id 取得所有 video id'''
    results = scrapetube.get_playlist(playlist_id=playlist_id, limit=100) # async generator
    return [result['videoId'] async for result in results]

def get_video_id(url: str):
    '''用 url 取得 video id'''
    parsed = urlparse(url)

    if parsed.netloc == "youtu.be": # 因為連結中可能包含 ?t=...
        video_id = parsed.path.lstrip("/")
    else: # 處理 youtube.com or other urls
        query = parse_qs(parsed.query)
        video_id = query.get("v", [None])[0]

    return video_id

def convert_to_short_url(url: str) -> str:
    '''將 youtube url 轉為 youtu.be 的短網址'''
    video_id = get_video_id(url)
    if not video_id: return ''
    return f'https://youtu.be/{video_id}'

def video_id_to_url(video_id: str) -> str:
    '''用 video_id 去組合成 youtu.be 短網址'''
    return f'https://youtu.be/{video_id}'

async def check_url_alive(audio_url: str) -> bool:
    '''用 head 的方式取檢查 url 是否還活著'''
    try:
        if not audio_url: return False
        resp = await HttpxAsyncClient.head(audio_url, timeout=5)
        return resp.status_code == 200
    except:
        return False

def safe_filename(title: str) -> str:
    # 替換掉 Windows 不允許的字元
    safe = re.sub(r'[\\/*?:"<>|]', "_", title)
    # 去掉前後空白
    safe = safe.strip()
    # 避免 Windows 保留字
    reserved = {"CON", "PRN", "AUX", "NUL",
                *(f"COM{i}" for i in range(1, 10)),
                *(f"LPT{i}" for i in range(1, 10))}
    if safe.upper() in reserved:
        safe = f"_{safe}"
    return safe

async def _download_item(url: str, path: str | Path, max_retries: int = 3, retry_delay: int = 5):
    if not url: return

    path_obj = Path(path)
    new_name = safe_filename(path_obj.stem)

    path = str(path_obj.parent / f'{new_name}{path_obj.suffix}')

    if os.path.exists(path):
        os.remove(path)

    logger.info(f'Start download {url} to {path}...')

    attempt = 0
    downloaded_size = 0 # 本地已經下載的大小
    while attempt < max_retries:
        try:
            downloaded_size = os.path.getsize(path) if os.path.exists(path) else 0

            headers = {}
            if downloaded_size > 0:
                headers["Range"] = f"bytes={downloaded_size}-"
                logger.info(f"續傳 {url} 從 {downloaded_size} bytes")

            async with HttpxAsyncClient.stream("GET", url, headers=headers) as resp:
                resp.raise_for_status()

                mode = "ab" if downloaded_size > 0 else "wb"
                async with aiofiles.open(path, mode) as f:
                    async for chunk in resp.aiter_bytes():
                        await f.write(chunk)

            final_size = os.path.getsize(path)
            logger.info(f"Downloaded {url} to {path}, size: {final_size / (1024 * 1024):.2f} MB")
            return

        except (httpx.ReadError, httpx.HTTPError, httpx.ConnectError) as e:
            attempt += 1
            logger.warning(f"下載失敗: {e}, {retry_delay}s 後重試 ({attempt}/{max_retries})")
            await asyncio.sleep(retry_delay)

    raise RuntimeError(f"Download failed after {max_retries} attempts for {url}")


def download_item(url: str, path: str | Path) -> asyncio.Task:
    return asyncio.create_task(_download_item(url, path))