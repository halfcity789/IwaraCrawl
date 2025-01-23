import argparse
import json

from src.logger import getLogger


class Config(object):
    def __init__(self):
        parser = argparse.ArgumentParser(description='a script to crawl videos of iwara')

        targetGroup = parser.add_mutually_exclusive_group()
        targetGroup.add_argument('-ui', '--userid', type=str, help='set modes userid(format: 1,2,3)', default=None)
        targetGroup.add_argument('-u', '--username', type=str, help='set modes username(only one)', default=None)
        targetGroup.add_argument('-il', '--useridlist', type=str, help='provide user list(format: userid1\\nuserid2\\n)', default=None)
        targetGroup.add_argument('-nl', '--usernamelist', type=str, help='provide user list(format: user1\\nuser2\\n)', default=None)
        targetGroup.add_argument('-vi', '--videoid', type=str, help='set modes userid(format no blank: 1,2,3)', default="jKht0GSLbBJlCO,X53mTzYaYKae4t,hOamHEVamaCSEG")
        targetGroup.add_argument('-vt', '--videotitle', type=str, help="search for videos by video title", default=None)

        configGroup = parser.add_argument_group()
        configGroup.add_argument('--useconfig', action='store_true', help='read user list from config file', default=False)
        configGroup.add_argument('--auto', action='store_true', help='auto pick one when asking to select', default=True)
        configGroup.add_argument('--userlimit', type=int, help='numbers of user info to get', default=50)
        configGroup.add_argument('--videolimit', type=int, help='numbers of videos to pick', default=50)
        configGroup.add_argument('--proxy', type=str, help='set proxy', default="http://localhost:7890/")
        configGroup.add_argument('--debug', action="store_true", help='enable debug mode', default=True)
        configGroup.add_argument('--timeout', type=int, help='set timeout', default=150000)
        configGroup.add_argument('-t', '--task', type=int, help='set task number to crawl(default: 1)', default=1)
        configGroup.add_argument('--sleep', type=int, help='set sleep time after crawled a vide', default=5)
        configGroup.add_argument('--output', type=str, help='set output', default=".\\output\\")
        configGroup.add_argument('-r', '--resolution', type=str, help='set video Resolution (360, 540, Source, preview)', default="preview")
        configGroup.add_argument('-n', '--number', type=int, help='set crawl number (default: 1)', default=1)

        self.__args = parser.parse_args()
        with open("config/config.json") as config:
            self.__config = json.load(config)

        videoResolution = ["360", "540", "Source", "preview"]

        # init
        self.__uidList = None
        self.__usernameList = None
        self.__videoTitleList = None
        self.__videoIdList = None
        self.__searchLimit = {
            "user": None,
            "video": None
        }

        if self.__args.useconfig:
            self.__output = self.__config.get("output")
            self.__timeout = self.__config.get("timeout")
            self.__proxy = self.__config.get("proxy")
            self.__number = self.__config.get("number")
            self.__logLevel = self.__config.get("logLevel")
            self.__videoResolution = self.__config.get("videoResolution")
            self.__sleep = self.__config.get("sleep")
            self.__isAutoSelect = self.__config.get("auto")
            self.__taskNumber = self.__config.get("taskNumber")

            if self.__isAutoSelect:
                self.__searchLimit["user"] = self.__config.get("search").get("userLimit")
                self.__searchLimit["video"] = self.__config.get("search").get("videoLimit")

            users = self.__config.get("save").get("users", {})
            self.__uidList = [user['uid'] for user in users.values()]
            self.__usernameList = [user['username'] for user in users.values()]
            self.__videoIdList = [video['id'] for video in self.__config.get("save").get("videos", {}).values()]
            self.__videoTitleList = [video['title'] for video in self.__config.get("save").get("videos", {}).values()]
        else:
            self.__logLevel = "info"
            self.__output = self.__args.output
            self.__timeout = self.__args.timeout
            self.__proxy = self.__args.proxy
            self.__number = self.__args.number
            self.__videoResolution = self.__args.resolution
            self.__sleep = self.__args.sleep
            self.__isAutoSelect = self.__args.auto
            self.__taskNumber = self.__args.task

            if self.__args.debug:
                self.__logLevel = "debug"

            if self.__args.auto:
                self.__searchLimit["user"] = self.__args.userlimit
                self.__searchLimit["video"] = self.__args.videolimit

            if self.__args.userid:
                self.__uidList = self.__args.userid.split(",")

            if self.__args.videoid:
                self.__videoIdList = self.__args.videoid.split(",")
            elif self.__args.videotitle:
                self.__videoTitleList = self.__args.videotitle.split(",")

            if self.__args.useridlist:
                with open(self.__args.useridlist, "r") as userIdList:
                    self.__uidList = userIdList.readlines()

            if self.__args.usernamelist:
                with open(self.__args.usernamelist, "r") as usernameList:
                    self.__usernameList = usernameList.readlines()
            elif self.__args.username:
                self.__usernameList = [self.__args.username]
        self.__logger = getLogger(__name__, self.__logLevel)

        if self.__videoResolution not in videoResolution:
            self.__logger.critical("resolution should be 360 or 540 or Source or preview(try --help)")

        if self.__taskNumber <= 0:
            self.__taskNumber = 1

        if not self.__uidList:
            if not self.__usernameList:
                if not self.__videoIdList:
                    if not self.__videoTitleList:
                        self.__logger.critical("target to crawl must be provided(try --help)")

        if not self.__output:
            self.__logger.critical("output path is null(try --help)")

        self.__logger.debug("loaded config")

    def setLogLevel(self, logLevel: str):
        self.__logLevel = logLevel

    def getUidList(self):
        return self.__uidList

    def getVideoIdList(self):
        return self.__videoIdList

    def getVideoTitleList(self):
        return self.__videoTitleList

    def getUsernameList(self):
        return self.__usernameList

    def getConfig(self):
        return self.__config

    def getTimeout(self):
        return self.__timeout

    def getProxy(self):
        return self.__proxy

    def getNumber(self):
        return self.__number

    def getOutput(self):
        return self.__output

    def getLogLevel(self):
        return self.__logLevel

    def getVideoResolution(self):
        return self.__videoResolution

    def getSleep(self):
        return self.__sleep

    def getIsAutoSelect(self):
        return self.__isAutoSelect

    def getSearchLimit(self):
        return self.__searchLimit

    def getTaskNumber(self):
        return self.__taskNumber
