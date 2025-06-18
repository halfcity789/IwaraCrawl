import ctypes

from os.path import abspath

from src.logger import getLogger


class DllManager(object):
    def __init__(self):
        self._logger = getLogger(__name__, "debug")
        try:
            self._CRYPTO = ctypes.CDLL(abspath('./src/cpp/libs/crypto.dll'), winmode=0)

            self._CRYPTO.generateXVersion.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
            self._CRYPTO.generateXVersion.restype = ctypes.POINTER(ctypes.c_char)
            self._CRYPTO.free_result.argtypes = [ctypes.POINTER(ctypes.c_char)]
        except FileNotFoundError as e:
            self._logger.critical(e.args[0])

    def getInstanceOfCrypto(self):
        return self._CRYPTO


def getInstance(targetDll: str):
    dllManager = DllManager()
    match targetDll:
        case "crypto.dll":
            return dllManager.getInstanceOfCrypto()
