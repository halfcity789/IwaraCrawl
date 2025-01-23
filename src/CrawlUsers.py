import asyncio

from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientProxyConnectionError
from typing import List

from src.model import User
from src.res import header
from src.config import Config
from src.logger import getLogger


class CrawlUsers(object):
    def __init__(self, config: Config):
        self.__config = config
        self.__logger = getLogger(__name__, self.__config.getLogLevel())
        self.__apiUrlBase = "https://api.iwara.tv/"

    async def getUsers(self, uidList, pages: List[int] = None, limit=50) -> List[User]:
        if not pages:
            pages = [0]

        videoApiUrl = "%svideos?rating=all&user={uid}&page={page}&limit={limit}" % self.__apiUrlBase
        followerApiUrl = "%suser/{uid}/followers?limit={limit}" % self.__apiUrlBase
        users = []
        async with ClientSession() as session:
            for uid in uidList:
                user = User()
                self.__logger.debug("getting user with id: {}".format(uid))
                try:
                    async with await session.get(url=videoApiUrl.format(uid=uid, page=pages[0], limit=limit), headers=header, proxy=self.__config.getProxy(), timeout=self.__config.getTimeout()) as res:
                        if res.status != 200:
                            self.__logger.error("request for {uid} get {status} (when requesting page {page}, passed)".format(uid=uid, status=res.status, page=0))
                            continue
                        userAndVideoInfo = await res.json()
                        userInfo = userAndVideoInfo.get("results")[0].get("user")
                        user.basicBuild(userInfo)
                        user.setVideoCount(userAndVideoInfo.get("count"))
                        user.setVideoIdList([item.get("id") for item in userAndVideoInfo.get("results")])
                        videoIdList = [item.get("id") for item in userAndVideoInfo.get("results")]

                        self.__logger.debug("user {} basic built".format(user.getName()))

                    for page in pages[1:]:
                        async with await session.get(url=videoApiUrl.format(uid=uid, page=page, limit=limit), headers=header, proxy=self.__config.getProxy(), timeout=self.__config.getTimeout()) as res:
                            if res.status == 200:
                                continue
                            else:
                                self.__logger.error("request for {uid} get {status} (in request page {page}, passed)".format(uid=uid, status=res.status, page=page))
                            userAndVideoInfo = await res.json()
                            videoIdList.append([item.get("id") for item in userAndVideoInfo.get("results")])
                            await asyncio.sleep(0.5)
                    user.setVideoIdList(videoIdList)

                    async with await session.get(url=followerApiUrl.format(uid=uid, page=0, limit=1), headers=header,
                                                 proxy=self.__config.getProxy(),
                                                 timeout=self.__config.getTimeout()) as res:
                        if res.status != 200:
                            self.__logger.error("request followers for {uid} get {status} (passed)".format(uid=uid, status=res.status))
                            continue
                        user.setFollowers(dict(await res.json()).get("count"))

                    users.append(user)
                    self.__logger.info("got user info: {}({} followers)".format(user.getName(), user.getFollowers()))
                except ClientProxyConnectionError as e:
                    self.__logger.critical(e)
                except IndexError:
                    self.__logger.warning("user with uid {} doesn't have any videos or exist".format(uid))

        return users



