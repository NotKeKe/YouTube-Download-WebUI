from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import hashlib
from pathlib import Path

from src.types import API
from src.downloader import Downloader
from src.utils import HttpxAsyncClient, safe_filename
from src import close_event

async def lifespan(app: FastAPI):
    # 啟動
    yield
    # 關閉
    await close_event()

app = FastAPI(lifespan=lifespan) # type: ignore
# css, js
# 攔截 /assets 路徑請求
app.mount('/assets', StaticFiles(directory='./front/dist/assets'))
# html
tmplates = Jinja2Templates(directory='./front/dist')

download_tokens: dict[str, Path] = {} # [hash token, path]

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return tmplates.TemplateResponse('index.html', {'request': request})

@app.get('/icon.png')
async def icon():
    return FileResponse('./front/dist/icon.png')

@app.post('/quality', response_class=JSONResponse)
async def quality(quality: API.Quality):
    '''得到一個 url 的資訊，包含解析度、音質等等......'''
    url = quality.url
    try:
        downloader = Downloader(url, 'meta')
        await downloader.run()
        assert downloader.data and downloader.data.meta
        downloader.data.meta.abr.reverse()
        downloader.data.meta.fps.reverse()
        downloader.data.meta.resolution.reverse()
        meta = downloader.get_meta()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return meta

@app.post('/download')
async def download(download: API.Download):
    '''給前端用的 API，測試時也可以用這個'''
    url = download.url
    abr = download.abr
    resolution = download.resolution
    fps = download.fps
    req_type = download.type

    downloader = Downloader(url, req_type, abr, resolution, fps)

    try:
        await downloader.run()
        assert downloader.data
        download_url = downloader.data.download_url
    except Exception as e:
        raise HTTPException(status_code=500, detail='Error running downloader: ' + str(e))
    
    # 是 pytube 回傳的連結
    if download_url.startswith('/download'):
        token = download_url.split('/')[-1]
        file_path = download_tokens.get(token)
        if not file_path:
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(file_path, filename=file_path.name)

    # get media type
    if not download_url:
        raise HTTPException(status_code=500, detail=f"I don't know what happened, but I can't find the download url.\nIt's the url I got: `{download_url}`")
    
    head_resp = await HttpxAsyncClient.head(download_url)
    if head_resp.status_code >= 400:
        raise HTTPException(status_code=404, detail="File not found")

    media_type = head_resp.headers.get("Content-Type", "application/octet-stream")

    async def stream():
        async with HttpxAsyncClient.stream("GET", download_url) as resp:
            resp.raise_for_status()
            async for chunk in resp.aiter_bytes():
                yield chunk

    headers = {
        "Content-Disposition": f'attachment; filename="{safe_filename(downloader.data.title)}"',
    }

    return StreamingResponse(stream(), media_type=media_type, headers=headers)


@app.get('/download/{token}', response_class=FileResponse)
async def download_by_token(request: Request, token: str):
    '''這是用來下載本地檔案用的，如果用到 pytubefix 下載 video+audio 才會產生'''
    file_path = download_tokens.get(token)
    if not file_path:
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path, filename=file_path.name)

@app.post('/add_download_url', response_class=JSONResponse)
async def add_download_url(add_download_url: API.AddDownloadUrl, request: Request):
    '''這是用 pytubefix 下載完檔案到本地後要用的，如果用到 pytubefix 下載 video+audio 才會產生'''
    file_path = add_download_url.file_path
    token = hashlib.sha256(file_path.encode()).hexdigest()
    download_tokens[token] = Path(file_path)
    return {'download_url': f'/download/{token}'}