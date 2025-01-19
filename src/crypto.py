import hashlib


class Crypto(object):
    def __init__(self):
        self.__secret = "5nFp9kmbNnHdAFhaqMvt"

    def generateXVersion(self, fileId: str, expires: int):
        secret = "%s_%s_%s" % (fileId, expires, self.__secret)
        return hashlib.sha1(secret.encode("utf-8")).hexdigest()
