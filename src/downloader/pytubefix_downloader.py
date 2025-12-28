from pytubefix import AsyncYouTube, StreamQuery
from collections import defaultdict
import logging
import asyncio
import re

from .ffmpeg_merge import merge_video_audio

from ..utils import MultiExecutor, HttpxAsyncClient, download_item, TMP_DIR, DOWNLOAD_DIR, safe_filename
from ..types import ExtractInfo, DownloadType, VideoMeta
from ..module import AbstractDownloader

from config import PORT

logger = logging.getLogger(__name__)

class PyTubeDownloader(AbstractDownloader):
    def __init__(self, url: str, req_type: DownloadType, abr: int = -1, resolution: int = -1, fps: int = -1, to_h264: bool = False):
        super().__init__(url, req_type, abr, resolution, fps, to_h264)

    async def _get_meta(self, yt: AsyncYouTube, streams: StreamQuery) -> dict:
        meta = {
            'title': await yt.title(),
            'thumbnail_url': await yt.thumbnail_url(),
            'duration': await yt.length(),
            'resolution': set(),
            'abr': set(),
            'fps': set(),
        }

        for item in streams:
            fps = item.fps if hasattr(item, 'fps') else None

            resolution = item.resolution
            if resolution:
                resolution = resolution.replace('p', '')
                try: resolution = int(resolution)
                except: resolution = None

            abr = item.abr
            if abr:
                abr = abr.replace('kbps', '')
                try: abr = int(abr)
                except: abr = None

            meta['fps'].add(fps)
            meta['abr'].add(abr)
            meta['resolution'].add(resolution)

        for item in ('resolution', 'abr', 'fps'):
            new_ls = [int(x) for x in meta[item] if x]
            new_ls.sort()
            meta[item] = new_ls

        return meta
    

    async def _run(self) -> ExtractInfo:
        yt = AsyncYouTube(self.url)
        streams = await yt.streams()

        # get meta
        meta = await self._get_meta(yt, streams)
        if self.req_type == 'meta':
            return ExtractInfo.model_validate({
                'meta': VideoMeta.model_validate(meta)
            })

        # get subtitle
        subtitles = defaultdict(list)
        for caption in ( await yt.captions() ):
            lang = caption.code
            srt = caption.generate_srt_captions()

            # clean
            srt = re.sub(r'<font[^>]*>', '', srt)  
            srt = re.sub(r'</font>', '', srt)  
            srt = re.sub(r'<[^>]+>', '', srt)  

            subtitles[lang].append(srt)

        # start get video / audio
        download_url = ''

        # 取得 影片 + 音訊
        if self.req_type == 'video+audio':
            # 使用者指定畫質 or 最高畫質
            req_resolution = self.resolution if self.resolution != -1 else max(meta['resolution'])
            # 因為已經有畫質的指定了，所以再匹配 fps，sort fps first
            vids = streams.filter(
                only_video=True, 
                res=f'{req_resolution}p', 
                **({'fps': self.fps} if self.fps != -1 else {}) # 判斷使用者有沒有指定 fps
            ).order_by('fps').desc()

            vid = vids.first()
            if not vid:
                # 找不到就回退，找符合畫質的影片
                streams.filter(only_video=True, res=f'{req_resolution}p').order_by('fps').desc().first()

                
            vid_url = vid.url if vid else ''
            vid_subtype = vid.subtype if vid else ''

            aud = streams.filter(only_audio=True, **({'abr': self.abr} if self.abr != -1 else {})).order_by('abr').desc().first()
            aud_url = aud.url if aud else ''
            aud_subtype = aud.subtype if aud else ''
            
            # download both in order to combine
            stem = safe_filename(meta['title'])

            task1 = download_item(vid_url, str(TMP_DIR / f'{stem}.{vid_subtype}'))
            task2 = download_item(aud_url, str(TMP_DIR / f'{stem}.{aud_subtype}'))

            try:
                await asyncio.gather(task1, task2)
            except:
                # 如果其中一個失敗，就停止下載
                task1.cancel()
                task2.cancel()
                try: await asyncio.gather(task1, task2)
                except asyncio.CancelledError: ...
                raise

            # combine both to a file, use ffmpeg
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                MultiExecutor,
                merge_video_audio,
                TMP_DIR / f'{stem}.{vid_subtype}',
                TMP_DIR / f'{stem}.{aud_subtype}',
                DOWNLOAD_DIR / f'{stem}.mp4',
                self.to_h264
            )

            # 發給 api，讓他創建一個下載連結
            resp = await HttpxAsyncClient.post(
                f'http://localhost:{PORT}/add_download_url',
                json={
                    'file_path': str(DOWNLOAD_DIR / f'{stem}.mp4')
                }
            )

            download_url = resp.json()['download_url']

        elif self.req_type == 'video':
            stream = streams.filter(only_video=True)

            if self.fps != -1 and self.resolution != -1: # find best video
                tofind_fps = max(meta['fps'])
                tofind_res = max(meta['resolution'])

                # 這樣寫是因為 fps 好像有可能不存在，但我上面那個 video + audio 的沒改，出錯再說w
                _item = next(filter(lambda x: (
                    (hasattr(x, 'fps') and hasattr(x, 'resolution'))  # 有 fps 和 resolution
                    and 
                    (x.fps and x.resolution) # fps 和 resolution 不為 None
                    and 
                    (x.fps == tofind_fps and x.resolution == tofind_res) # 符合條件
                ), stream), None)

                if not _item:
                    _item = next(filter(lambda x: (
                        (hasattr(x, 'resolution'))  # 有 resolution
                        and 
                        x.resolution # resolution 不為 None
                        and 
                        x.resolution == tofind_res # 符合條件
                    ), stream), None)

                download_url = _item.url if _item else ''
            elif self.fps != -1: # find best video by fps
                stream = stream.filter(fps=self.fps)
                vid = stream.order_by('resolution').desc().first()

                download_url = vid.url if vid else ''
            elif self.resolution != -1: # find best video by resolution
                stream = stream.filter(res=f'{self.resolution}p')
                vid = stream.order_by('fps').desc().first()

                download_url = vid.url if vid else ''

        elif self.req_type == 'audio':
            stream = streams.filter(only_audio=True)

            if self.abr != -1: # find best audio by abr
                stream = stream.filter(abr=self.abr)
                aud = stream.first()

            else: # find best audio
                aud = stream.order_by('abr').desc().first()

            download_url = aud.url if aud else ''

        return ExtractInfo.model_validate({
            "download_url": download_url,
            "thumbnail_url": await yt.thumbnail_url(),
            "title": await yt.title(),
            "duration": await yt.length(),
            'subtitles': subtitles,
            'meta': VideoMeta.model_validate(meta)
        })

