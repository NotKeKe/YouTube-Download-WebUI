from __future__ import annotations

from .types import DownloadType
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import ExtractInfo

class AbstractDownloader:
    def __init__(self, url: str, req_type: DownloadType, abr: int = -1, resolution: int = -1, fps: int = -1, to_h264: bool = False, download_to_server: bool = False):
        self.url = url
        self.req_type = req_type
        self.abr = abr
        self.resolution = resolution
        self.fps = fps
        self.to_h264 = to_h264
        self.download_to_server = download_to_server

        self.already_downloaded: bool = False
        self.download_sub_type: str = ''

    @property
    def required_download(self):
        return self.req_type != 'meta'

    async def _run(self) -> ExtractInfo:
        '''在此處放上判斷 req_type 的邏輯，以及執行下載的邏輯'''
        raise NotImplementedError