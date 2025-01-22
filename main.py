import asyncio
import datetime
import time

from src.config import Config
from src.CrawlVIdeos import CrawlVideos
from src.logger import getLogger


def main():
    start = time.time()

    config = Config()
    logger = getLogger(__name__, config.getLogLevel())
    videoCrawler = CrawlVideos(config)
    loop = asyncio.get_event_loop()

    task1 = asyncio.ensure_future(videoCrawler.getVideoFile())

    tasks = [task1]

    loop.run_until_complete(asyncio.wait(tasks))
    logger.info("running time: %s" % datetime.timedelta(seconds=time.time() - start))


if __name__ == "__main__":
    main()
