import src as _ # 先 init log
import config as _

from app import app
import uvicorn
import webbrowser


if __name__ == '__main__':
    from config import PORT, PUBLIC, RUNNING_IN_DOCKER
    
    host = '0.0.0.0' if PUBLIC else '127.0.0.1'

    if not RUNNING_IN_DOCKER:
        webbrowser.open(f'http://localhost:{PORT}/')
    
    uvicorn.run(app, host=host, port=PORT)