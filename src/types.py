from pydantic import BaseModel, Field
from typing import Optional, Any, Literal

DownloadType = Literal['video', 'audio', 'video+audio', 'meta']

class API:
    '''some types for fastapi'''
    class Quality(BaseModel):
        url: str

    class Download(BaseModel):
        url: str
        type: DownloadType = 'video+audio'
        # -1 代表 best
        abr: int = -1 
        resolution: int = -1
        fps: int = -1

    class AddDownloadUrl(BaseModel):
        file_path: str

class VideoMeta(BaseModel):
    title: str = ''
    thumbnail_url: str = ''
    duration: int = 0
    resolution: list[int] = Field(default_factory=list)
    abr: list[int] = Field(default_factory=list)
    fps: list[int] = Field(default_factory=list)

class ExtractInfo(BaseModel):
    download_url: str = ''
    thumbnail_url: str = ''
    title: str = ''
    duration: int = 0
    subtitles: dict[str, list[str]] = Field(default_factory=dict)
    meta: Optional[VideoMeta] = None
    requested_formats: list[dict[str, Any]] = Field(default_factory=list)