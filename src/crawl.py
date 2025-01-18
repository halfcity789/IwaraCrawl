from args import args


class CrawlUserVideos(object):
    def __init__(self, user):
        self.__user = user


class CrawlUser(object):
    def __init__(self, uid):
        self.__uid = uid


def saveVideo(stream, fileName):
    with open(args.output + fileName, 'wb') as file:
        file.write(stream.content)
