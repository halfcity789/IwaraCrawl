import asyncio
import aiofiles

from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectorError
from typing import Tuple, List

from src.model import User, Video
from src.res import header
from src.crypto import Crypto
from src.config import Config
from src.logger import getLogger


class CrawlUsers(object):
    def __init__(self, config: Config):
        self.__config = config
        self.__logger = getLogger(__name__, self.__config.getLogLevel())
        self.__apiUrlBase = "https://api.iwara.tv/"

    def __getPagesAndLimit(self) -> Tuple[List[int], int]:
        # limit max number is 50
        number = self.__config.getNumber()
        if number <= 50:
            pages = [0]
            limit = number
        else:
            pages = range(0, number // 50 + 1)
            limit = 50
        return pages, limit

    async def getUsers(self) -> List[User]:
        url = self.__apiUrlBase + "videos?rating=all&user={uid}&page={page}&limit={limit}"
        pages, limit = self.__getPagesAndLimit()

        self.__logger.info("pages to crawl: {}".format(len(pages)))
        self.__logger.info("limit for one page: {}".format(limit))
        self.__logger.info("try to download videos...")

        users = []
        async with ClientSession() as session:
            for uid in self.__config.getUidList():
                user = User()
                self.__logger.debug("getting user with id: {}".format(uid))
                async with await session.get(url=url.format(uid=uid, page=pages[0], limit=limit), headers=header, proxy=self.__config.getProxy(), timeout=self.__config.getTimeout()) as res:
                    if res.status != 200:
                        self.__logger.warning("request for {uid} get {status} (when requesting page {page}, passed)".format(uid=uid, status=res.status, page=0))
                        continue
                    userAndVideoInfo = await res.json()
                    userInfo = userAndVideoInfo.get("results")[0].get("user")
                    user.basicBuild(userInfo)
                    user.setVideoCount(userAndVideoInfo.get("count"))
                    user.setVideoIdList([item.get("id") for item in userAndVideoInfo.get("results")])
                    videoIdList = [item.get("id") for item in userAndVideoInfo.get("results")]

                    self.__logger.debug("user {} basic built".format(user.getName()))

                for page in pages[1:]:
                    async with await session.get(url=url.format(uid=uid, page=page, limit=limit), headers=header, proxy=self.__config.getProxy(), timeout=self.__config.getTimeout()) as res:
                        if res.status == 200:
                            continue
                        else:
                            self.__logger.warning("request for {uid} get {status} (in request page {page}, passed)".format(uid=uid, status=res.status, page=page))
                        userAndVideoInfo = await res.json()
                        videoIdList.append([item.get("id") for item in userAndVideoInfo.get("results")])
                        await asyncio.sleep(0.5)

                user.setVideoIdList(videoIdList)
                users.append(user)

                self.__logger.debug("got user info: {}".format(user.getName()))

        return users


class CrawlVideos(object):
    def __init__(self, config: Config):
        self.__config = config
        self.__logger = getLogger(__name__, self.__config.getLogLevel())
        self.__apiUrlBase = "https://api.iwara.tv/"

    async def __getVideos(self) -> List[Video]:
        url = self.__apiUrlBase + "video/{videoId}"
        userCrawler = CrawlUsers(self.__config)
        videos = []
        users = await userCrawler.getUsers()

        videoIdList = self.__config.getVideoIdList()
        for user in users:
            videoIdList.extend(user.getVideoIdList())

        async with ClientSession() as session:
            for videoId in videoIdList:
                video = Video()
                self.__logger.debug("try to get video with id: {}".format(videoId))
                async with await session.get(url=url.format(videoId=videoId), headers=header, proxy=self.__config.getProxy(), timeout=self.__config.getTimeout()) as res:
                    if res.status != 200:
                        self.__logger.warning("request for {videoId} get {status} (passed)".format(videoId=videoId, status=res.status))
                        continue
                    videoInfo = await res.json()
                    video.basicBuild(videoInfo)

                    videos.append(video)
                    self.__logger.debug("got video info: {}".format(video.getTitle()))

        return videos

    async def getVideoFile(self) -> None:
        generator = Crypto()
        videos = await self.__getVideos()

        for video in videos:
            if video.getIsPrivate():
                self.__logger.warning("warning video {} is private (passed already)".format(video.getTitle()))
                continue
            key = video.getFileUrl().split("/")[4].split("&")[0].split("?")
            headerForFileReq = header.copy()
            headerForFileReq["X-Version"] = generator.generateXVersion(key[0], key[1].split('=')[1])

            async with ClientSession() as session:
                self.__logger.debug("try to get fileUrl to video: {}".format(video.getTitle()))
                async with await session.get(url=video.getFileUrl(), headers=headerForFileReq, proxy=self.__config.getProxy(), timeout=self.__config.getTimeout()) as res:
                    if res.status != 200:
                        self.__logger.warning("request for {videoTitle} get {status}(passed)".format(videoTitle=video.getTitle(), status=res.status))
                        continue

                    fileDownloadList = await res.json()
                    downloadUrl = "https:%s" % fileDownloadList[3].get("src").get("download")
                    try:
                        async with await session.get(url=downloadUrl, headers=headerForFileReq, proxy=self.__config.getProxy(), timeout=self.__config.getTimeout()) as videoFile:
                            async with aiofiles.open(self.__config.getOutput() + video.getTitle() + ".mp4", "wb") as file:
                                self.__logger.debug("try to download video: {}".format(video.getTitle()))
                                async for chunk in videoFile.content.iter_chunked(102400):
                                    await file.write(chunk)
                                self.__logger.info("video downloaded: {}".format(video.getTitle()))
                                await asyncio.sleep(5)
                    except ClientConnectorError:
                        self.__logger.error("Cannot connect to host clara.iwara.tv:443 ssl:default")
                        self.__logger.warning("this error may caused by too low request interval time (passed already)")
                        continue


class CrawlUserIdByUsername(object):
    def __init__(self, config: Config):
        self.__config = config



