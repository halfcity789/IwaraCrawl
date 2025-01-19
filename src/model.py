class User(object):
    def __init__(self):
        self.__id = None
        self.__name = None
        self.__username = None
        self.__status = None
        self.__seenAt = None
        self.__createAt = None
        self.__updatedAt = None
        self.__videoCount = None
        self.__videoIdList = None

    def basicBuild(self, userInfo: dict):
        self.setId(userInfo.get("id"))
        self.setName(userInfo.get("name"))
        self.setUsername(userInfo.get("username"))
        self.setStatus(userInfo.get("status"))
        self.setSeenAt(userInfo.get("seenAt"))
        self.setCreateAt(userInfo.get("createdAt"))
        self.setUpdatedAt(userInfo.get("updatedAt"))

    def setId(self, uid):
        self.__id = uid

    def getId(self):
        return self.__id

    def setName(self, name):
        self.__name = name

    def getName(self):
        return self.__name

    def setUsername(self, username):
        self.__username = username

    def getUsername(self):
        return self.__username

    def setStatus(self, status):
        self.__status = status

    def getStatus(self):
        return self.__status

    def setSeenAt(self, seenAt):
        self.__seenAt = seenAt

    def getSeenAt(self):
        return self.__seenAt

    def setCreateAt(self, createAt):
        self.__createAt = createAt

    def getCreateAt(self):
        return self.__createAt

    def setUpdatedAt(self, updatedAt):
        self.__updatedAt = updatedAt

    def getUpdatedAt(self):
        return self.__updatedAt

    def setVideoCount(self, videoCount):
        self.__videoCount = videoCount

    def getVideoCount(self):
        return self.__videoCount

    def setVideoIdList(self, videoIdList):
        self.__videoIdList = videoIdList

    def getVideoIdList(self):
        return self.__videoIdList


class Video(object):
    def __init__(self):
        self.__id = None
        self.__title = None
        self.__body = None
        self.__likes = None
        self.__views = None
        self.__comments = None
        self.__fileUrl = None
        self.__isPrivate = None

    def basicBuild(self, videoInfo: dict):
        self.setId(videoInfo.get("id"))
        self.setTitle(videoInfo.get("title"))
        self.setBody(videoInfo.get("body"))
        self.setIsPrivate(videoInfo.get("private"))
        self.setLikes(videoInfo.get("numLikes"))
        self.setViews(videoInfo.get("numViews"))
        self.setComments(videoInfo.get("numComments"))
        self.setFileUrl(videoInfo.get("fileUrl"))

    def setId(self, videoId):
        self.__id = videoId

    def getId(self):
        return self.__id

    def setTitle(self, title):
        self.__title = title

    def getTitle(self):
        return self.__title

    def setBody(self, body):
        self.__body = body

    def getBody(self):
        return self.__body

    def setLikes(self, likes):
        self.__likes = likes

    def getLikes(self):
        return self.__likes

    def setViews(self, views):
        self.__views = views

    def getViews(self):
        return self.__views

    def setComments(self, comments):
        self.__comments = comments

    def getComments(self):
        return self.__comments

    def setFileUrl(self, fileUrl):
        self.__fileUrl = fileUrl

    def getFileUrl(self):
        return self.__fileUrl

    def setIsPrivate(self, isPrivate: bool):
        self.__isPrivate = isPrivate

    def getIsPrivate(self):
        return self.__isPrivate
