
#######################################
# LOGGER
#######################################

import time

# 수가 더 클 수록 더 많이 표시되는 것
LOGLEVEL = {
    "DEBUG": 256,
    "INFO": 128,
    "WARNING": 64,
    "ERROR": 32,
    "CRITICAL": 16,
    "FATAL": 8,
    "LOG": 4,
}

verboseLevel = LOGLEVEL["DEBUG"]

class L:
    def prCyan(self, skk): return "\033[96m{}\033[00m".format(skk)
    def prYello(self, skk): return "\033[93m{}\033[00m".format(skk)
    def prRed(self, skk): return "\033[91m{}\033[00m".format(skk)
    def prGreen(self, skk): return "\033[92m{}\033[00m".format(skk)
    def prPurple(self, skk): return "\033[95m{}\033[00m".format(skk)
    def prGray(self, skk): return "\033[90m{}\033[00m".format(skk)

    def getTimeSTR(self):
        return time.strftime("%H:%M:%S", time.localtime())

    def print(self, scope: str, message, level: int = LOGLEVEL["DEBUG"]):
        if level > verboseLevel:
            return
        inf = self.prCyan("[INFO    ]")
        if level == LOGLEVEL["ERROR"]:
            inf = self.prRed("[ERROR   ]")
        if level == LOGLEVEL["WARNING"]:
            inf = self.prYello("[WARNING ]")
        if level == LOGLEVEL["LOG"]:
            inf = self.prGreen("[LOG     ]")
        if level == LOGLEVEL["CRITICAL"]:
            inf = self.prPurple("[CRITICAL]")
        if level == LOGLEVEL["DEBUG"]:
            inf = self.prGray("[DEBUG   ]")
        
        yl = self.prYello(f"[{str.ljust(scope, 20)}]")
        if(message == ""):
            print(f"[{self.getTimeSTR()}] {inf} {self.prYello("[global              ]")} {scope}")
        else:
            print(f"[{self.getTimeSTR()}] {inf} {yl} {message}")

    def debug(self, scope: str, message = ""):
        self.print(scope, message, level=LOGLEVEL["DEBUG"])
    def info(self, scope: str, message = ""):
        self.print(scope, message, level=LOGLEVEL["INFO"])
    def warning(self, scope: str, message = ""):
        self.print(scope, message, level=LOGLEVEL["WARNING"])
    def error(self, scope: str, message = ""):
        self.print(scope, message, level=LOGLEVEL["ERROR"])
    def critical(self, scope: str, message = ""):
        self.print(scope, message, level=LOGLEVEL["CRITICAL"])
    def log(self, scope: str, message = ""):
        self.print(scope, message, level=LOGLEVEL["LOG"])

    def fit(self, stri: str, length: int):
        stri = str(stri)
        if(len(stri) <= length):
            return str.ljust(stri, length)
        else:
            strlen = len(stri)
            return "..." + stri[strlen - length + 3:]