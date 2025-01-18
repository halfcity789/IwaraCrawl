import asyncio
import aiofiles
import logging

from aiohttp import ClientSession

from src.model import User, Video
from src.crypto import Crypto


class CrawlUsers(object):
    def __init__(self, config):
        self.__config = config
        self.__apiUrlBase = "https://api.iwara.tv/"

    def __getPagesAndLimit(self):
        # limit max number is 50
        number = self.__config.getNumber()
        if number <= 50:
            pages = [0]
            limit = number
        else:
            pages = range(0, number // 50 + 1)
            limit = 50
        return pages, limit

    async def getUsers(self):
        header = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://www.iwara.tv",
            "Referer": "https://www.iwara.tv/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
        }
        url = self.__apiUrlBase + "videos?rating=all&user={uid}&page={page}&limit={limit}"
        pages, limit = self.__getPagesAndLimit()

        logging.info("[*] pages to crawl: {}".format(len(pages)))
        logging.info("[*] limit for one page: {}".format(limit))

        users = []
        user = User()
        async with ClientSession() as session:
            for uid in self.__config.getUidList():
                logging.info("[*] getting user with id: {}".format(uid))
                async with await session.get(url=url.format(uid=uid, page=pages[0], limit=limit), headers=header, proxy=self.__config.getProxy(), timeout=self.__config.getTimeout()) as res:
                    if res.status != 200:
                        logging.warning("[-] request for {uid} get {status} (in request page {page})".format(uid=uid, status=res.status, page=0))
                        continue
                    userAndVideoInfo = await res.json()
                    userInfo = userAndVideoInfo.get("results")[0].get("user")
                    user.setId(userInfo.get("id"))
                    user.setName(userInfo.get("name"))
                    user.setUsername(userInfo.get("username"))
                    user.setSeenAt(userInfo.get("seenAt"))
                    user.setCreateAt(userInfo.get("createdAt"))
                    user.setUpdatedAt(userInfo.get("updatedAt"))
                    user.setVideoCount(userAndVideoInfo.get("count"))
                    user.setVideoIdList([item.get("id") for item in userAndVideoInfo.get("results")])
                    videoIdList = [item.get("id") for item in userAndVideoInfo.get("results")]

                for page in pages[1:]:
                    async with await session.get(url=url.format(uid=uid, page=page, limit=limit), headers=header, proxy=self.__config.getProxy(), timeout=self.__config.getTimeout()) as res:
                        if res.status == 200:
                            continue
                        else:
                            logging.warning("[-] request for {uid} get {status} (in request page {page})".format(uid=uid, status=res.status, page=page))
                        userAndVideoInfo = await res.json()
                        videoIdList.append([item.get("id") for item in userAndVideoInfo.get("results")])
                        await asyncio.sleep(0.5)

                user.setVideoIdList(videoIdList)
                users.append(user)

                logging.info("[+] got user: {}".format(user.getName()))

        return users


class CrawlVideos(object):
    def __init__(self, config):
        self.__config = config
        self.__apiUrlBase = "https://api.iwara.tv/"

    async def __getVideos(self):
        header = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": "https://www.iwara.tv",
            "Referer": "https://www.iwara.tv/",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
        }
        url = self.__apiUrlBase + "video/{videoId}"
        userCrawler = CrawlUsers(self.__config)
        video = Video()
        videos = []
        users = await userCrawler.getUsers()

        videoIdList = self.__config.getVideoIdList()
        # for user in users:
        #     videoIdList.extend(user.getVideoIdList())

        async with ClientSession() as session:
            for videoId in videoIdList:
                logging.info("[*] getting video with id: {}".format(videoId))
                async with await session.get(url=url.format(videoId=videoId), headers=header, proxy=self.__config.getProxy(), timeout=self.__config.getTimeout()) as res:
                    if res.status != 200:
                        logging.warning("[-] request for {videoId} get {status}".format(videoId=videoId, status=res.status))
                        continue
                    videoInfo = await res.json()
                    video.setId(videoInfo.get("id"))
                    video.setTitle(videoInfo.get("title"))
                    video.setBody(videoInfo.get("body"))
                    video.setFileUrl(videoInfo.get("fileUrl"))

                    videos.append(video)

        return videos

    async def getVideoFile(self):
        generator = Crypto()
        videos = await self.__getVideos()
        for video in videos:
            key = video.getFileUrl().split("/")[4].split("&")[0].split("?")
            header = {
                "Accept": "application/json",
                "Content-Type": "application/json",
                "Origin": "https://www.iwara.tv",
                "Referer": "https://www.iwara.tv/",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
                "X-Version": generator.generateXVersion(key[0], key[1].split('=')[1])
            }

            async with ClientSession() as session:
                logging.info("[*] getting video with title: {}".format(video.getTitle()))
                async with await session.get(url=video.getFileUrl(), headers=header, proxy=self.__config.getProxy(), timeout=self.__config.getTimeout()) as res:
                    if res.status != 200:
                        logging.warning("[-] request for {videoTitle} get {status}".format(videoTitle=video.getTitle(), status=res.status))
                        continue
                    fileDownloadList = await res.json()
                    downloadUrl = "https:%s" % fileDownloadList[3].get("src").get("download")
                    async with await session.get(url=downloadUrl, headers=header, proxy=self.__config.getProxy(), timeout=self.__config.getTimeout()) as videoFile:
                        async with aiofiles.open(self.__config.getOutput() + video.getTitle() + ".mp4", "wb") as file:
                            async for chunk in videoFile.content.iter_chunked(102400):
                                await file.write(chunk)


class CrawlUserIdByUsername(object):
    def __init__(self, username):
        self.__username = username



