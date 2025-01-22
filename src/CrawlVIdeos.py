import asyncio
import aiofiles

from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectorError, ContentTypeError
from typing import List, Optional
from tqdm.asyncio import tqdm

from src.CrawlUsers import CrawlUsers
from src.model import Video, User
from src.search import Search
from src.res import header
from src.utils.CountUtils import getPagesAndLimit
from src.crypto import Crypto
from src.config import Config
from src.logger import getLogger


class CrawlVideos(object):
    def __init__(self, config: Config):
        self.__config = config
        self.__logger = getLogger(__name__, self.__config.getLogLevel())
        self.__apiUrlBase = "https://api.iwara.tv/"

    async def getVideos(self, users: List[User], extraVideoIdList: Optional[str] = None) -> List[Video]:
        url = self.__apiUrlBase + "video/{videoId}"

        videos = []
        videoIdList = []
        if extraVideoIdList:
            videoIdList = extraVideoIdList
        for user in users:
            videoIdList.extend(user.getVideoIdList())

        async with ClientSession() as session:
            for videoId in videoIdList:
                video = Video()
                self.__logger.debug("try to get video with id: {}".format(videoId))
                async with await session.get(url=url.format(videoId=videoId), headers=header, proxy=self.__config.getProxy(), timeout=self.__config.getTimeout()) as res:
                    if res.status != 200:
                        self.__logger.error("request for {videoId} get {status} (passed)".format(videoId=videoId, status=res.status))
                        continue
                    videoInfo = await res.json()
                    video.basicBuild(videoInfo)

                    videos.append(video)
                    self.__logger.debug("got video info: {}".format(video.getTitle()))

        return videos

    async def getVideoFile(self) -> None:
        generator = Crypto()
        pages, limit = getPagesAndLimit(self.__config.getNumber())

        self.__logger.info("pages to crawl: {}".format(len(pages)))
        self.__logger.info("limit for one page: {}".format(limit))
        self.__logger.info("selected resolution: {}".format(self.__config.getVideoResolution()))
        self.__logger.info("try to download videos...")
        if self.__config.getUsernameList():
            searcher = Search(self.__config)
            users = await searcher.searchUserByUsername(self.__config.getUsernameList()[0])
        else:
            userCrawler = CrawlUsers(self.__config)
            users = await userCrawler.getUsers(self.__config.getUidList(), pages, limit)
        videoIdList = self.__config.getVideoIdList()
        videos = await self.getVideos(users, videoIdList)

        for video in videos:
            if video.getIsPrivate():
                self.__logger.error("warning video {} is private (passed already)".format(video.getTitle()))
                continue
            key = video.getFileUrl().split("/")[4].split("&")[0].split("?")
            headerForFileReq = header.copy()
            headerForFileReq["X-Version"] = generator.generateXVersion(key[0], key[1].split('=')[1])

            async with ClientSession() as session:
                self.__logger.debug("try to get fileUrl of video: {}".format(video.getTitle()))
                async with await session.get(url=video.getFileUrl(), headers=headerForFileReq, proxy=self.__config.getProxy(), timeout=self.__config.getTimeout()) as res:
                    if res.status != 200:
                        self.__logger.error("request for {videoTitle} get {status}(passed)".format(videoTitle=video.getTitle(), status=res.status))
                        continue

                    fileDownloadList = await res.json()
                    downloadUrl = None
                    for file in fileDownloadList:
                        if file.get("name") == self.__config.getVideoResolution():
                            downloadUrl = "https:%s" % file.get("src").get("download")
                            break
                    try:
                        async with await session.get(url=downloadUrl, headers=headerForFileReq, proxy=self.__config.getProxy(), timeout=self.__config.getTimeout()) as videoFileRes:
                            fileSize = int(videoFileRes.headers.get("content-length"))
                            async with aiofiles.open("%s%s_%s.mp4" % (self.__config.getOutput(), video.getTitle(), self.__config.getVideoResolution()), "wb") as file:
                                self.__logger.debug("try to download video: {}({} bytes)".format(video.getTitle(), fileSize))
                                with tqdm(total=fileSize, unit='B', unit_scale=True, desc=video.getTitle(), leave=False) as pbar:
                                    async for chunk in videoFileRes.content.iter_chunked(102400):
                                        await file.write(chunk)
                                        pbar.update(len(chunk))
                                self.__logger.info("video downloaded: {}({} bytes)".format(video.getTitle(), fileSize))
                                await asyncio.sleep(self.__config.getSleep())
                    except ClientConnectorError as e:
                        self.__logger.error(e)
                        self.__logger.warning("this error may caused by too low request interval time (passed already)")
                        continue
                    except ContentTypeError as e:
                        self.__logger.error(e)
                        self.__logger.warning("this error may caused by server error(not local)")
                        continue
