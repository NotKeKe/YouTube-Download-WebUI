import logging
import logging.handlers
from pathlib import Path
import sys

log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

def setup_logging():
    log_format = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    # 避免 httpx 發送請求就有日誌
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
  
    # 寫入檔案
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_dir / "app.log",  # 主要日誌檔的名稱
        when='D',                     # 'D' 代表按天 (Day) 輪替
        interval=1,                   # 間隔為 1 天
        backupCount=10,               # 保留 10 個舊的日誌檔案 (等於保留10天的紀錄)
        encoding="utf-8",
    )
    # --------------------------

    file_handler.setFormatter(log_format)

    # 避免重複加入 Handler
    if root_logger.handlers: # 如果已經有 handler 了
        for handler in root_logger.handlers[:]: # 遍歷一個副本，以便安全移除
            root_logger.removeHandler(handler)
            
    if not root_logger.handlers:
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)

    sys.stdout = StreamToLogger(logging.getLogger(), logging.INFO)
    sys.stderr = StreamToLogger(logging.getLogger(), logging.ERROR)

class StreamToLogger:
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        # 避免記錄空行
        if message.rstrip() != "":
            self.logger.log(self.level, message.rstrip())

    def flush(self):
        # logging 的 handlers 會自動處理 flush，所以這裡可以 pass
        pass

    def isatty(self):
        return False