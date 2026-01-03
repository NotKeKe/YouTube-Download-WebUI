from __future__ import annotations

from ast import type_ignore
import asyncio
from typing import TYPE_CHECKING, Optional
import logging

from .pytubefix_downloader import PyTubeDownloader
from .yt_dlp_downloader import YtDlpDownloader

from ..utils import check_url_alive, download_item, DOWNLOAD_DIR, safe_filename

if TYPE_CHECKING:
    from ..types import DownloadType, ExtractInfo, DownloadStats
    from ..module import AbstractDownloader
    from pathlib import Path

logger = logging.getLogger(__name__)

class Downloader:
    def __init__(self, url: str, req_type: DownloadType, abr: int = -1, resolution: int = -1, fps: int = -1, to_h264: bool = False, download_to_server: bool = False):
        self._downloader: Optional[AbstractDownloader] = None
        self.url = url
        self.req_type = req_type
        self.abr = abr
        self.resolution = resolution
        self.fps = fps
        self.to_h264 = to_h264
        self.download_to_server = download_to_server

        self.data: Optional[ExtractInfo] = None # 用 downloader 透過 _run 所得到的資料

        self.ran: bool = False
        self.is_pytube: bool = False

        self.download_stats: DownloadStats = 'none'

    def get_meta(self) -> dict:
        if not self.ran: raise Exception('Downloader.run() must be called before get_meta()')
        if not self.data or not self.data.meta: return {}

        return self.data.meta.model_dump()

    def download(self):
        '''Download to server side'''
        if self._downloader and self._downloader.already_downloaded: return
        if not self.data or not self.data.download_url: raise Exception('Downloader.run() must be called before download()')
        
        filename = safe_filename(self.data.title)
        sub_type = self._downloader.download_sub_type # type: ignore
        if not sub_type: raise Exception('Unknown sub_type') 
        dir = DOWNLOAD_DIR / f'{filename}.{sub_type}'

        async def download_task(client: Downloader, download_url: str, dir: Path):
            await download_item(download_url, dir)
            client.already_downloaded = True # type: ignore
            client.download_stats = 'completed'

        task = download_task(self, self.data.download_url, dir)
        asyncio.create_task(task)   
        self.download_stats = 'downloading'

    async def run(self) -> dict:
        self.ran = True
        self._downloader = YtDlpDownloader(self.url, self.req_type, self.abr, self.resolution, self.fps, self.to_h264, download_to_server=self.download_to_server) # type: ignore
        try:
            self.data = await self._downloader._run()
            if self.data.download_url and not self.data.download_url.startswith('/download') and not await check_url_alive(self.data.download_url): # 之前遇到過 yt-dlp 給我不能用的連結過
                raise Exception('yt-dlp returned a broken url')
        except Exception as e:
            logger.error('yt-dlp Download failed, reverting to PyTube...', exc_info=True)

            self._downloader = PyTubeDownloader(self.url, self.req_type, self.abr, self.resolution, self.fps, self.to_h264, download_to_server=self.download_to_server) # type: ignore
            try:
                self.is_pytube = True
                self.data = await self._downloader._run()
            except Exception as e:
                logger.error('pytubefix Download failed, ', exc_info=True)
                raise

        if self.download_to_server:
            self.download()   

        return self.data.model_dump()