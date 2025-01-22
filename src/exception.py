class CrawlRunningException(Exception):
    def __init__(self, message):
        self.__message = message

    def getMessage(self):
        return self.__message


class IllegalParameterException(CrawlRunningException):
    def __init__(self, message="parameter provided is illegal"):
        super().__init__(message)
