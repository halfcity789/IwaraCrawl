from src.config import Config
from src.crawl import CrawlUsers

import asyncio
import logging


def main():
    logging.basicConfig(level=logging.INFO)
    config = Config()
    userCrawler = CrawlUsers(config)
    loop = asyncio.get_event_loop()

    task1 = asyncio.ensure_future(userCrawler.getUsers())

    tasks = [task1]

    loop.run_until_complete(asyncio.wait(tasks))


if __name__ == "__main__":
    main()
