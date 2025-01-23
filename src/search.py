import asyncio

from aiohttp import ClientSession, ClientConnectorError
from typing import List

from src.config import Config
from src.CrawlUsers import CrawlUsers
from src.model import User, Video
from src.logger import getLogger
from src.res import header
from src.utils.CountUtils import getPagesAndLimit


class Search(object):
    def __init__(self, config: Config):
        self.__apiBaseUrl = "https://api.iwara.tv/search?type={type}&page={page}&query={query}&limit={limit}"
        self.__config = config
        self.__logger = getLogger(__name__, self.__config.getLogLevel())
        self.__searchType = {
            "video": "video",
            "user": "user"
        }

    async def searchUserByUsername(self, username: str) -> List[User]:
        return await self.__searchUsers(username)

    async def searchUserByUsernameList(self, usernameList: list) -> List[List[User]]:
        # TODO: deving
        pass

    async def searchVideoIdListByVideoTitle(self, title: str) -> List[str]:
        return await self.__searchVideosIdList(title)

    async def __searchInfo(self, searchType: str, query: str) -> list:
        async with ClientSession() as session:
            try:
                pages, limit = getPagesAndLimit(self.__config.getSearchLimit().get(searchType))
                self.__logger.debug("try to search {} with name: {}(this may take time due to api speed, limit {})".format(searchType, query, len(pages) * limit))
                async with await session.get(
                        url=self.__apiBaseUrl.format(type=searchType, query=query, page=pages, limit=limit),
                        headers=header, proxy=self.__config.getProxy(),
                        timeout=self.__config.getTimeout()) as res:
                    if res.status != 200:
                        self.__logger.error("when searching {} get {}".format(searchType, res.status))
                    infoList = dict(await res.json()).get("results")

                for page in pages[1:]:
                    async with await session.get(
                            url=self.__apiBaseUrl.format(type=searchType, query=query, page=page, limit=limit),
                            headers=header, proxy=self.__config.getProxy(),
                            timeout=self.__config.getTimeout()) as res:
                        if res.status != 200:
                            self.__logger.error("when searching {} get {} (page={})".format(searchType, res.status, page))
                            continue
                        infoList.extend(dict(await res.json()).get("results"))
                        await asyncio.sleep(0.5)
                self.__logger.info("search result: {} {}".format(len(infoList), searchType))

                return infoList
            except ClientConnectorError as e:
                self.__logger.critical(e)

    async def __searchUsers(self, username) -> List[User]:
        userInfoList = await self.__searchInfo("user", username)
        userCrawler = CrawlUsers(self.__config)
        userIdList = []
        for userInfo in userInfoList:
            userIdList.append(userInfo.get("id"))
        self.__logger.info("try to get user's follower numbers")
        pages, limit = getPagesAndLimit(self.__config.getNumber())
        users = await userCrawler.getUsers(userIdList, pages, limit)
        users.sort(key=lambda user: user.getFollowers(), reverse=True)

        return users[:self.__config.getSearchLimit().get("user")]

    async def __searchVideosIdList(self, videoTitle) -> List[str]:
        videoInfoList = await self.__searchInfo("video", videoTitle)
        videoInfoList.sort(key=lambda x: x.get("numViews"), reverse=True)
        videoIdList = []
        for videoInfo in videoInfoList[:self.__config.getSearchLimit().get("video")]:
            if videoInfo.get("private"):
                self.__logger.warning("video with id: {} is private (passed)".format(videoInfo.get("id")))
                continue
            videoIdList.append(videoInfo.get("id"))

        return videoIdList[:self.__config.getNumber()]
