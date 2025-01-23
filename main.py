import asyncio
import datetime
import time

from typing import List

from src.config import Config
from src.CrawlVideos import CrawlVideos
from src.CrawlUsers import CrawlUsers
from src.model import Video
from src.search import Search
from src.utils.CountUtils import getPagesAndLimit
from src.logger import getLogger


async def pickVideos(config: Config, videoCrawler: CrawlVideos) -> List[Video]:
    videoIdList = config.getVideoIdList()
    if config.getUsernameList():
        searcher = Search(config)
        users = await searcher.searchUserByUsername(config.getUsernameList()[0])
        videos = await videoCrawler.getVideos(users, videoIdList)
    elif config.getVideoTitleList():
        searcher = Search(config)
        videoIdList = await searcher.searchVideoIdListByVideoTitle(config.getVideoTitleList()[0])
        videos = await videoCrawler.getVideos(None, videoIdList)
    elif config.getUidList():
        userCrawler = CrawlUsers(config)
        pages, limit = getPagesAndLimit(config.getNumber())
        users = await userCrawler.getUsers(config.getUidList(), pages, limit)
        videos = await videoCrawler.getVideos(users, videoIdList)
    else:
        videos = await videoCrawler.getVideos(None, videoIdList)

    return videos


async def main():
    start = time.time()

    config = Config()
    logger = getLogger(__name__, config.getLogLevel())

    logger.info("video numbers to crawl: {}".format(config.getNumber()))
    logger.info("selected resolution: {}".format(config.getVideoResolution()))
    logger.info("try to download videos...")
    
    videoCrawler = CrawlVideos(config)
    videos = await pickVideos(config, videoCrawler)

    tasks = [asyncio.create_task(videoCrawler.getVideoFile(videos), name="VideoCrawler-Task-%d" % i) for i in range(1, config.getTaskNumber() + 1)]
    await asyncio.gather(*tasks)

    logger.info("running time: %s" % datetime.timedelta(seconds=time.time() - start))


if __name__ == "__main__":
    asyncio.run(main())
