from src.config import Config
from src.crawl import CrawlVideos

import asyncio
import logging


def main():
    logging.basicConfig(level=logging.INFO)
    config = Config()
    videoCrawler = CrawlVideos(config)
    loop = asyncio.get_event_loop()

    task1 = asyncio.ensure_future(videoCrawler.getVideoFile())

    tasks = [task1]

    loop.run_until_complete(asyncio.wait(tasks))


if __name__ == "__main__":
    main()
