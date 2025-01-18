class User(object):
    def __init__(self):
        self.__id = None
        self.__name = None
        self.__username = None
        self.__status = None
        self.__seenAt = None
        self.__createAt = None
        self.__updatedAt = None
        self.__videoList = None

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

    def setVideoList(self, videoList):
        self.__videoList = videoList

    def getVideoList(self):
        return self.__videoList


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

    def setIsPrivate(self, isPrivate):
        self.__isPrivate = isPrivate

    def getIsPrivate(self):
        return self.__isPrivate
