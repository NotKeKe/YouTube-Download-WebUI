import sys
from pathlib import Path
curr_dir = Path(__file__).parent
sys.path.append(str(curr_dir.parent))

from src.downloader.downloader import PyTubeDownloader
import asyncio
from pprint import pp

async def main():
    downloader = PyTubeDownloader(
        url='https://youtu.be/X6K1cHQNs-I?si=94gHgyS60Idquz3y',
        req_type='video+audio',
        to_h264=False
    )   
    resp = await downloader._run()
    pp(resp)

if __name__ == '__main__':
    asyncio.run(main())