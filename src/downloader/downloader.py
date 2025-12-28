from __future__ import annotations

from typing import TYPE_CHECKING, Optional
import logging

from .pytubefix_downloader import PyTubeDownloader
from .yt_dlp_downloader import YtDlpDownloader

from ..utils import check_url_alive

if TYPE_CHECKING:
    from ..types import DownloadType, ExtractInfo

logger = logging.getLogger(__name__)

class Downloader:
    def __init__(self, url: str, req_type: DownloadType, abr: int = -1, resolution: int = -1, fps: int = -1, to_h264: bool = False):
        self.url = url
        self.req_type = req_type
        self.abr = abr
        self.resolution = resolution
        self.fps = fps
        self.to_h264 = to_h264

        self.data: Optional[ExtractInfo] = None # 用 downloader 透過 _run 所得到的資料

        self.ran: bool = False
        self.is_pytube: bool = False

    def get_meta(self) -> dict:
        if not self.ran: raise Exception('Downloader.run() must be called before get_meta()')
        if not self.data or not self.data.meta: return {}

        return self.data.meta.model_dump()

    async def run(self) -> dict:
        self.ran = True
        downloader = YtDlpDownloader(self.url, self.req_type, self.abr, self.resolution, self.fps, self.to_h264) # type: ignore
        try:
            self.data = await downloader._run()
            if self.data.download_url and not self.data.download_url.startswith('/download') and not await check_url_alive(self.data.download_url): # 之前遇到過 yt-dlp 給我不能用的連結過
                raise Exception('yt-dlp returned a broken url')
        except Exception as e:
            logger.error('yt-dlp Download failed, reverting to PyTube...', exc_info=True)

            downloader = PyTubeDownloader(self.url, self.req_type, self.abr, self.resolution, self.fps, self.to_h264) # type: ignore
            try:
                self.is_pytube = True
                self.data = await downloader._run()
            except Exception as e:
                logger.error('pytubefix Download failed, ', exc_info=True)
                raise

        return self.data.model_dump()