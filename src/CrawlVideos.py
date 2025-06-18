import asyncio
import aiofiles
import ctypes

from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectorError, ContentTypeError, ClientPayloadError
from typing import List, Optional
from tqdm.asyncio import tqdm

from src.model import Video, User, BaseCrawler
from src.res import header
from src.utils.FileUtils import reformVideoFileName
from src.DllManager import getInstance
from src.config import Config


class CrawlVideos(BaseCrawler):
    def __init__(self, config: Config):
        super().__init__(config, __name__)
        self._CRYPTO = getInstance("crypto.dll")
        # self.__ERRORNUMBER = 0
        self.__apiUrlBase = "https://api.iwara.tv/"

    async def getVideos(self, users: Optional[List[User]] = None, extraVideoIdList: Optional[List[str]] = None) -> List[Video]:
        if not users and not extraVideoIdList:
            self._logger.critical("users or videoIdList must be provided")

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
                self._logger.debug("try to get video with id: {}".format(videoId))
                async with await session.get(url=url.format(videoId=videoId), headers=header, proxy=self._config.getProxy(), timeout=self._config.getTimeout()) as res:
                    if res.status != 200:
                        self._logger.error("request for {videoId} get {status} (passed)".format(videoId=videoId, status=res.status))
                        continue
                    videoInfo = await res.json()
                    video.basicBuild(videoInfo)

                    videos.append(video)
                    self._logger.debug("got video info: {}".format(video.getTitle()))

        return videos

    async def getVideoFile(self, videos: List[Video]) -> None:
        self._logger.debug("task {} started".format(asyncio.current_task().get_name()))
        while videos:
            video = videos.pop()
            if video.getIsPrivate():
                self._logger.error("warning video {} is private (passed already)".format(video.getTitle()))
                continue
            key = video.getFileUrl().split("/")[4].split("&")[0].split("?")
            headerForFileReq = header.copy()
            resultPtr = self._CRYPTO.generateXVersion(key[0].encode("utf-8"), key[1].split('=')[1].encode("utf-8"))
            if not resultPtr:
                self._logger.error("failed to generate XVersion filed ({})" % asyncio.current_task)
                continue
            self._logger.debug("XVersion: %s" % ctypes.string_at(resultPtr).decode('utf-8'))
            headerForFileReq["X-Version"] = ctypes.string_at(resultPtr).decode('utf-8')
            self._CRYPTO.free_result(resultPtr)

            async with ClientSession() as session:
                self._logger.debug("try to get fileUrl of video: {}({} views)".format(video.getTitle(), video.getViews()))
                async with await session.get(url=video.getFileUrl(), headers=headerForFileReq, proxy=self._config.getProxy(), timeout=self._config.getTimeout()) as res:
                    if res.status != 200:
                        self._logger.error("request for {videoTitle} get {status}(passed)".format(videoTitle=video.getTitle(), status=res.status))
                        continue

                    fileDownloadList = await res.json()
                    downloadUrl = None
                    for file in fileDownloadList:
                        if file.get("name") == self._config.getVideoResolution():
                            downloadUrl = "https:%s" % file.get("src").get("download")
                            break
                    try:
                        async with await session.get(url=downloadUrl, headers=headerForFileReq, proxy=self._config.getProxy(), timeout=self._config.getTimeout()) as videoFileRes:
                            fileSize = int(videoFileRes.headers.get("content-length"))
                            fileName = reformVideoFileName("%s%s_%s.mp4" % (self._config.getOutput(), video.getTitle(), self._config.getVideoResolution()))
                            async with aiofiles.open(fileName, "wb") as file:
                                self._logger.debug("try to download video: {}".format(video.getTitle()))
                                video.setTitle(reformVideoFileName(video.getTitle()))
                                if self._config.getProgress():
                                    with tqdm(total=fileSize, unit='B', unit_scale=True, desc=video.getTitle(), leave=False) as pbar:
                                        async for chunk in videoFileRes.content.iter_chunked(102400):
                                            await file.write(chunk)
                                            pbar.update(len(chunk))
                                else:
                                    self._logger.info("downing video {} (this may take a while)".format(video.getTitle()))
                                    async for chunk in videoFileRes.content.iter_chunked(102400):
                                        await file.write(chunk)
                                self._logger.info("video downloaded: {}({} bytes)".format(video.getTitle(), fileSize))
                                if videos:
                                    self._logger.debug("sleep for {}s ({})".format(self._config.getSleep(), asyncio.current_task()))
                                    await asyncio.sleep(self._config.getSleep())
                    except ClientConnectorError as e:
                        self._logger.error(e)
                        self._logger.warning("this error may caused by too low request interval time (passed already)")
                        continue
                    except ContentTypeError as e:
                        self._logger.error(e)
                        self._logger.warning("this error may caused by server error(not local)")
                        continue
                    except ClientPayloadError as e:
                        self._logger.error("{} ({})".format(e, video.getTitle()))
                        self._logger.warning("这个bug出现时间不定无法复现，我懒得管了，出现了就重试一下或者调整一下请求的时间之类的")
                        continue
                    except TypeError as e:
                        self._logger.error(e)
                        self._logger.warning("this error likely caused by target resolution {} doesn't exist to this video".format(self._config.getVideoResolution()))
                        self._logger.info("available (pick the resolution): {}".format(file))
                        continue
                    except Exception as e:
                        self._logger.error(e)
                        # if self.__ERRORNUMBER >= 3:
                        #     self._logger.critical("unknown error happened for times, exiting...")
                        # self.__ERRORNUMBER += 1
                        continue

        self._logger.debug("task {} exit".format(asyncio.current_task().get_name()))