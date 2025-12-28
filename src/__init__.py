from ._setup_log import setup_logging as _setup_logging

_setup_logging()

async def close_event():
    import logging
    logger = logging.getLogger(__name__)

    try:
        from .utils import HttpxAsyncClient
        await HttpxAsyncClient.aclose()
        logger.info("Close src.utils.HttpxAsyncClient.")
    except:
        logger.info("Can't close src.utils.HttpxAsyncClient.")

    try:
        from .utils import HttpxSyncClient
        HttpxSyncClient.close()
        logger.info("Close src.utils.HttpxSyncClient.")
    except:
        logger.info("Can't close src.utils.HttpxSyncClient.")

    try:
        from .scrapetube import clients
        for client in clients:
            try: await client.aclose()
            except: ...
        logger.info("Close src.scrapetube.clients.")
    except:
        logger.info("Can't close src.scrapetube.clients.")

    try:
        from .utils import MultiExecutor
        MultiExecutor.shutdown(wait=True)
        logger.info("Close src.utils.MultiExecutor.")
    except:
        logger.info("Can't close src.utils.MultiExecutor.")