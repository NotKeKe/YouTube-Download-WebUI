import yt_dlp
from collections import defaultdict
import logging
import asyncio

from .ffmpeg_merge import merge_video_audio

from ..utils import YTDL_OPTIONS, MultiExecutor, HttpxAsyncClient, HttpxSyncClient, download_item, TMP_DIR, DOWNLOAD_DIR, safe_filename
from ..types import ExtractInfo, DownloadType, VideoMeta
from ..module import AbstractDownloader

from config import PORT

logger = logging.getLogger(__name__)

def _run_it(yt_dlp_options: dict, url: str, req_type: DownloadType) -> ExtractInfo | None:
    try:
        with yt_dlp.YoutubeDL(yt_dlp_options) as ydl: # type: ignore
            info = ydl.extract_info(url, download=False)

            # get metas
            meta = {
                'title': info.get('title', ''),
                'thumbnail_url': info.get('thumbnail', ''),
                'duration': info.get('duration', 0),
                'resolution': set(),
                'abr': set(),
                'fps': set(),
            }

            for f in info['formats']: # type: ignore
                if f['vcodec'] == 'none' and f['acodec'] == 'none': continue
                height = f.get('height')
                abr = f.get('abr')
                fps = f.get('fps')  

                if f['vcodec'] != 'none' and f['acodec'] != 'none': # video + audio
                    meta['resolution'].add(height)
                    meta['fps'].add(fps)
                    meta['abr'].add(abr)
                elif f['vcodec'] != 'none' and f['acodec'] == 'none': # video
                    meta['resolution'].add(height)
                    meta['fps'].add(fps)

                elif f['vcodec'] == 'none' and f['acodec'] != 'none': # audio
                    meta['abr'].add(abr)

            for item in ('resolution', 'abr', 'fps'):
                new_ls = [int(x) for x in meta[item] if x]
                new_ls.sort()
                meta[item] = new_ls

            # early return
            if req_type == 'meta':
                return ExtractInfo.model_validate({
                    'meta': VideoMeta.model_validate(meta)
                })

            # get subtitle
            subtitles = defaultdict(list)
            if 'subtitles' in info:
                for lang, subs in info['subtitles'].items(): # type: ignore
                    for sub in subs:
                        ext = sub['ext']
                        if ext != 'srt': continue 

                        url = sub['url']

                        resp = HttpxSyncClient.get(url)
                        if resp.status_code != 200: continue

                        subtitles[lang].append(resp.text) # must be srt

            return ExtractInfo.model_validate({
                "download_url": info.get("url", ''),
                "thumbnail_url": info.get("thumbnail", ''),
                "title": info.get("title", ''),
                "duration": info.get("duration", 0),
                'subtitles': subtitles,
                'meta': VideoMeta.model_validate(meta),
                'requested_formats': info.get('requested_formats', []),
            })
        
    except Exception as e:
        logger.error('yt-dlp Download failed, ', exc_info=True)

class YtDlpDownloader(AbstractDownloader):
    def __init__(self, url: str, req_type: DownloadType, abr: int = -1, resolution: int = -1, fps: int = -1, to_h264: bool = False):
        super().__init__(url, req_type, abr, resolution, fps, to_h264)

    def _decide_format(self) -> str:
        if self.req_type == 'meta': return "best"
        base_req = 'Not supported output'
        extra_req = 'Not supported output'
        combine = None

        if self.req_type == 'video': 
            base_req = 'bestvideo'
            extra_req = ''

            if self.resolution != -1:
                extra_req += f'[height<={self.resolution}]'
            if self.fps != -1:
                extra_req += f'[fps<={self.fps}]'

            combine = base_req + extra_req + '/best' + extra_req
        
        elif self.req_type == 'audio':
            base_req = 'bestaudio'
            extra_req = ''

            if self.abr != -1:
                extra_req += f'[abr<={self.abr}]'

            combine = base_req + extra_req + '/best' + extra_req

        elif self.req_type == 'video+audio':
            base_vid_req = 'bestvideo'
            base_aud_req = 'bestaudio'

            extra_vid_req = ''
            extra_aud_req = ''

            # video request
            if self.resolution != -1:
                extra_vid_req += f'[height<={self.resolution}]'
            if self.fps != -1:
                extra_vid_req += f'[fps<={self.fps}]'

            # audio request
            if self.abr != -1:
                extra_aud_req += f'[abr<={self.abr}]'

            combine = base_vid_req + extra_vid_req + '+' + base_aud_req + extra_aud_req + '/best'


        logger.info(f'format: {combine} | original formats: base: {base_req}, extra: {extra_req} | download {self.req_type}')
        if not combine:
            raise Exception(base_req + extra_req + ' cannot be found')
        return combine

    async def _run(self) -> ExtractInfo:
        new_option = YTDL_OPTIONS.copy()
        new_option['format'] = self._decide_format()
        if not new_option['format']: raise Exception('WTF where is yt-dlp format')
        logger.info(f'yt-dlp option-format: {new_option}')
            
        loop = asyncio.get_running_loop()
        data = await loop.run_in_executor(MultiExecutor, _run_it, new_option, self.url, self.req_type) # type: ignore
        if not data:
            raise

        # bestvideo+bestaudio 會回傳兩個連結
        if '+' in new_option['format']:
            # find video and audio subtype
            vid_subtype = ''
            aud_subtype = ''

            for item in data.requested_formats:
                if item['resolution'].startswith('audio'):
                    aud_subtype = item['ext']
                else:
                    vid_subtype = item['ext']


            stem = safe_filename(data.title)

            # download both
            task1 = download_item(data.requested_formats[0]['url'], str(TMP_DIR / f'{stem}.{data.requested_formats[0]["ext"]}'))
            task2 = download_item(data.requested_formats[1]['url'], str(TMP_DIR / f'{stem}.{data.requested_formats[1]["ext"]}'))

            try:
                await asyncio.gather(task1, task2)
            except Exception as e:
                # 如果其中一個失敗，就停止下載
                task1.cancel()
                task2.cancel()
                try: await asyncio.gather(task1, task2)
                except asyncio.CancelledError: ...
                raise

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

            data.download_url = resp.json()['download_url']

        assert isinstance(data, ExtractInfo)
        return data