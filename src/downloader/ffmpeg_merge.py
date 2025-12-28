from typing import Optional
from pathlib import Path
import subprocess
import logging

from ..utils import DOWNLOAD_DIR

from config import FFMPEG_PRESET

logger = logging.getLogger(__name__)

def merge_video_audio(video_file: Path, audio_file: Path, output_file: Optional[Path] = None, to_h264: bool = False) -> Optional[Path]:
    """
    針對大檔案的記憶體優化版本
    """
    if not output_file:
        video_file.name
        output_file = DOWNLOAD_DIR / (video_file.stem + "_merged.mp4")
    else:
        output_file = Path(output_file)

    if not video_file.exists():
        raise FileNotFoundError(f"找不到影片檔案: {video_file}")

    if not audio_file.exists():
        raise FileNotFoundError(f"找不到音訊檔案: {audio_file}")
    
    if output_file.exists():
        output_file.unlink()
        logger.info(f'{output_file.name} (output path) exists, removed...')
    
    
    # 使用 subprocess.run
    try:
        cmd = [
            'ffmpeg',
            '-i', str(video_file.resolve()),
            '-i', str(audio_file.resolve()),
            '-c:v', 'copy',
            '-c:a', 'aac',
            '-y',
            str(output_file.resolve())
        ]
        logger.info(f'Combining video and audio: {video_file} and {audio_file}')
        result = subprocess.run(
            cmd,
            capture_output=True,
            check=True,
            encoding='utf-8',
        )
    except subprocess.CalledProcessError as e:
        logger.error(f'Failed to combine video and audio: {e.stderr}')
        return None
    
    if to_h264:
        try:
            cmd = [
                "ffmpeg",
                "-i", str(output_file.resolve()),
                "-c:v", "libx264",
                "-preset", FFMPEG_PRESET, # 用 slow 的話，在我電腦上都會看到 cpu 使用率 100%
                "-crf", "28",
                "-c:a", "aac",
                "-b:a", "192k",
                str((output_file.parent / (f"{output_file.stem}_h264.mp4")).resolve()),
            ]
            logger.info(f'Converting to h264: {output_file}')
            result = subprocess.run(
                cmd,
                capture_output=True,
                check=True,
                encoding='utf-8',
            )

            output_file.unlink()
            output_file = output_file.parent / (f"{output_file.stem}_h264.mp4")

        except subprocess.CalledProcessError as e:
            logger.error(f'Failed to convert to h264: {e.stderr}')
            return None

    
    video_file.unlink()
    audio_file.unlink()

    logger.info(f'Combined video and audio, saved as: {output_file}')
    return output_file