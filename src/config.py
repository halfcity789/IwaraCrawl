import argparse
import json
import logging


class Config(object):
    def __init__(self):
        logging.debug("[*] loading config")
        parser = argparse.ArgumentParser(description='a script to crawl images of pixiv')

        userInfoGroup = parser.add_mutually_exclusive_group()
        userInfoGroup.add_argument('-i', '--userid', type=str, help='set modes userid(format: 1,2,3)', default=None)
        userInfoGroup.add_argument('-u', '--username', type=str, help='set modes username(only one)', default=None)
        userInfoGroup.add_argument('-il', '--useridlist', type=str, help='provide user list(format: userid1\\nuserid2\\n)', default=None)
        userInfoGroup.add_argument('-nl', '--usernamelist', type=str, help='provide user list(format: user1\\nuser2\\n)', default=None)

        configGroup = parser.add_argument_group()
        configGroup.add_argument('--useconfig', action='store_true', help='read user list from config file', default=True)
        configGroup.add_argument('--proxy', type=str, help='set proxy', default=None)
        configGroup.add_argument('--timeout', type=int, help='set timeout', default=None)
        configGroup.add_argument('--output', type=str, help='set output', default=".\\output\\")
        configGroup.add_argument('-n', '--number', type=int, help='set crawl number (default: 1)', default=1)

        self.__args = parser.parse_args()
        with open("config/config.json") as config:
            self.__config = json.load(config)

        if self.__args.useconfig:
            self.__output = self.__config.get("output")
            self.__timeout = self.__config.get("timeout")
            self.__proxy = self.__config.get("proxy")
            self.__number = self.__config.get("number")

            users = self.__config.get("save").get("users", {})
            self.__uidList = [user['uid'] for user in users.values()]
            self.__usernameList = [user['username'] for user in users.values()]
        else:
            self.__output = self.__args.output
            self.__timeout = self.__args.timeout
            self.__proxy = self.__args.proxy
            self.__number = self.__args.number
            self.__uidList = None
            self.__usernameList = None

            if self.__args.userid:
                self.__uidList = self.__args.userid.split(",")

            if self.__args.useridlist:
                with open(self.__args.useridlist, "r") as userIdList:
                    self.__uidList = userIdList.readlines()

            if self.__args.usernamelist:
                with open(self.__args.usernamelist, "r") as usernameList:
                    self.__usernameList = usernameList.readlines()

        if not self.__uidList or not self.__usernameList:
            logging.error("[-] uidList or usernameList is null")
            print("[-] please set a id or username or a list of them")
            exit(1)

        if not self.__output:
            logging.error("[-] output path is null")
            exit(1)

    def getUidList(self):
        return self.__uidList

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

    def setConfig(self, config):
        with open("test.json", 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False)
            self.__config = config
            logging.info("config set")
