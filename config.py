from dotenv import load_dotenv
import os
import logging

load_dotenv()
logger = logging.getLogger(__name__)

PORT = os.getenv("PORT") # 用於 uvicorn 啟動的 port
if PORT is None:
    PORT = 8127
else:
    try:
        PORT = int(PORT)
    except:
        logger.warning("PORT is not a number, use 8127 instead")
        PORT = 8127
logger.info(f'PORT: {PORT}')


RUNNING_IN_DOCKER = bool(os.getenv('RUNNING_IN_DOCKER')) # 判斷使用者是否在 docker 內，因為用 docker compose 會新增這個 env
logger.info(f"I'm {'not ' if not RUNNING_IN_DOCKER else ''}running in docker.")


PUBLIC = bool(os.getenv('PUBLIC'))
if RUNNING_IN_DOCKER: # force public for docker
    PUBLIC = True
if PUBLIC:
    logger.info(f'I\'m public. You can visit me at http://localhost:{PORT}')
else:
    logger.info(f'I\'m not public. You can visit me at http://127.0.0.1:{PORT}')

FFMPEG_PRESET = os.getenv('FFMPEG_PRESET') or 'ultrafast'