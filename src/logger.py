import logging
import os
from logging.handlers import RotatingFileHandler

from colorama import Fore, Style, Back


class LogFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG: Fore.LIGHTBLACK_EX + Style.BRIGHT,
        logging.INFO: Fore.CYAN + Style.BRIGHT,
        logging.WARNING: Fore.LIGHTYELLOW_EX + Style.BRIGHT,
        logging.ERROR: Fore.RED + Style.BRIGHT,
        logging.CRITICAL: Fore.RED + Back.LIGHTYELLOW_EX + Style.BRIGHT
    }

    # Override
    def format(self, record) -> str:
        logFormat = self.COLORS.get(record.levelno) + "[%(levelname)s]: %(message)s" + Style.RESET_ALL
        formatter = logging.Formatter(logFormat)
        return formatter.format(record)


class LogErrorHandler(logging.Handler):
    # Override
    def emit(self, record):
        if record.levelno == logging.CRITICAL:
            exit(1)


class ExitOnCriticalHandler(logging.Handler):
    def emit(self, record):
        exit(1)


class RotatingFileHandlerModified(RotatingFileHandler):
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=False, errors=None):
        super().__init__(filename, mode, maxBytes, backupCount, encoding, delay, errors)

    # Override
    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None
        if self.backupCount > 0:
            baseFileName = self.baseFilename.split(".")
            for i in range(self.backupCount - 1, 0, -1):
                # sfn = self.rotation_filename("%s.%d" % (self.baseFilename, i))
                # dfn = self.rotation_filename("%s.%d" % (self.baseFilename, i + 1))
                sfn = self.rotation_filename("%s_%d.%s" % (baseFileName[0], i, baseFileName[1]))
                dfn = self.rotation_filename("%s_%d.%s" % (baseFileName[0], i + 1, baseFileName[1]))
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            # dfn = self.rotation_filename(self.baseFilename + ".1")
            dfn = self.rotation_filename("%s_1.%s" % (baseFileName[0], baseFileName[1]))
            if os.path.exists(dfn):
                os.remove(dfn)
            self.rotate(self.baseFilename, dfn)
        if not self.delay:
            self.stream = self._open()


def getLogger(name: str, level: str) -> logging.Logger:
    LEVELS = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }

    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(LEVELS.get(level))

        # output to console
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(LEVELS.get(level))
        consoleHandler.setFormatter(LogFormatter())

        # output to log file
        MAXSIZE = 1024 * 200  # 200KB
        fileHandler = RotatingFileHandlerModified('.\\logs\\log.log', maxBytes=MAXSIZE, backupCount=5)
        fileHandler.setLevel(LEVELS.get(level))
        fileHandler.setFormatter(
            logging.Formatter("[%(asctime)s] [%(threadName)s] [%(name)s:%(funcName)s] [%(levelname)s]: %(message)s"))

        logger.addHandler(consoleHandler)
        logger.addHandler(fileHandler)
        logger.addHandler(LogErrorHandler())

    return logger
