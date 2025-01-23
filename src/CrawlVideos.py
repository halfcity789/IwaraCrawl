import asyncio
import aiofiles

from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectorError, ContentTypeError
from typing import List, Optional
from tqdm.asyncio import tqdm

from src.model import Video, User
from src.res import header
from src.crypto import Crypto
from src.config import Config
from src.logger import getLogger


class CrawlVideos(object):
    def __init__(self, config: Config):
        self.__config = config
        self.__logger = getLogger(__name__, self.__config.getLogLevel())
        self.__apiUrlBase = "https://api.iwara.tv/"

    async def getVideos(self, users: Optional[List[User]] = None, extraVideoIdList: Optional[List[str]] = None) -> List[Video]:
        if not users and not extraVideoIdList:
            self.__logger.critical("users or videoIdList must be provided")

        videos = []
        videoIdList = []
        if extraVideoIdList:
            videoIdList = extraVideoIdList
        if users:
            for user in users:
                videoIdList.extend(user.getVideoIdList())

        url = self.__apiUrlBase + "video/{videoId}"
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

    async def getVideoFile(self, videos: list) -> None:
        while videos:
            video = videos.pop()
            generator = Crypto()
            if video.getIsPrivate():
                self.__logger.error("warning video {} is private (passed already)".format(video.getTitle()))
                continue
            key = video.getFileUrl().split("/")[4].split("&")[0].split("?")
            headerForFileReq = header.copy()
            headerForFileReq["X-Version"] = generator.generateXVersion(key[0], key[1].split('=')[1])

            async with ClientSession() as session:
                self.__logger.debug("try to get fileUrl of video: {}({} views)".format(video.getTitle(), video.getViews()))
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
                                self.__logger.debug("try to download video: {}".format(video.getTitle()))
                                with tqdm(total=fileSize, unit='B', unit_scale=True, desc=video.getTitle(), leave=False) as pbar:
                                    async for chunk in videoFileRes.content.iter_chunked(102400):
                                        await file.write(chunk)
                                        pbar.update(len(chunk))
                                self.__logger.info("video downloaded: {}({} bytes)".format(video.getTitle(), fileSize))
                                if videos:
                                    self.__logger.debug("sleep for {}s".format(self.__config.getSleep()))
                                    await asyncio.sleep(self.__config.getSleep())
                    except ClientConnectorError as e:
                        self.__logger.error(e)
                        self.__logger.warning("this error may caused by too low request interval time (passed already)")
                        continue
                    except ContentTypeError as e:
                        self.__logger.error(e)
                        self.__logger.warning("this error may caused by server error(not local)")
                        continue
                    except TypeError as e:
                        self.__logger.error(e)
                        self.__logger.warning("this error likely caused by target resolution {} doesn't exist to this video".format(self.__config.getVideoResolution()))
                        self.__logger.debug("available: {}".format(file))
                        continue

        self.__logger.debug("task {} exit".format(asyncio.current_task().get_name()))