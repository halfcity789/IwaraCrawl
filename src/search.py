from aiohttp import ClientSession

from src.config import Config
from src.model import User


class Search(object):
    def __init__(self, config: Config):
        self.__apiBaseUrl = "https://api.iwara.tv/search?type={type}&page={page}&query={query}&limit={limit}"
        self.__config = config
        self.__searchType = {
            "video": "video",
            "user": "user"
        }

    def searchUserByUsername(self, username: str) -> User:
        async with ClientSession() as session:
            logging.info("[*] getting user with id: {}".format(uid))
            async with await session.get(url=url.format(uid=uid, page=pages[0], limit=limit), headers=header, proxy=self.__config.getProxy(), timeout=self.__config.getTimeout()) as res:
                if res.status != 200:
                    logging.warning("[-] request for {uid} get {status} (in request page {page})".format(uid=uid, status=res.status, page=0))
                    continue
