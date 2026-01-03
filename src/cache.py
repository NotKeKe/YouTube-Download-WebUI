from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

from .types import DownloadType
from .utils import get_video_id, check_url_alive 

if TYPE_CHECKING:
    from .downloader import Downloader

CACHE: dict[str, list[Downloader]] = defaultdict(list) # url, [Downloader]

def add_to_cache(downloader: Downloader):
    if not downloader.data: return
    key = get_video_id(downloader.url)
    if not key: return
    CACHE[key].append(downloader)

async def get_from_cache(url: str, req_type: DownloadType, abr: int | None = None, resolution: int | None = None, fps: int | None = None, to_h264: bool | None = None) -> Downloader | None:
    key = get_video_id(url)
    if not key: return None
    datas = CACHE.get(key, [])
    for downloader in datas.copy():
        if downloader.data and downloader.req_type == req_type and downloader.abr == abr and downloader.resolution == resolution and downloader.fps == fps and downloader.to_h264 == to_h264:
            url = downloader.data.download_url
            
            # check it
            if await check_url_alive(url):
                return downloader
            else:
                CACHE[key].remove(downloader)   

    return None