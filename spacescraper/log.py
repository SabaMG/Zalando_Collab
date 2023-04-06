from datetime import timedelta
import datetime
from colorama import Fore,init
import threading
screen_lock = threading.Semaphore(value=1)
import platform
import time,requests
try: 
    from src.functions.settings import *
except Exception: 
    try:
        from ..functions.settings import *
    except Exception:
        pass
try: 
    from src.functions.api import *
except Exception: 
    try:
        from ..functions.api import *
    except Exception:
        pass

log_file = str(time.time()).split(".")[0]
#-------------------------------------------#
if platform.system() == 'Windows':
    init(convert=True)
#-------------------------------------------#

class Logger:
    def __init__(self, title="", taskcount=None ,timedelta=timedelta(hours= 2)):
        self._logColor = ''
        self._errorColor = Fore.RED
        self._successColor = Fore.GREEN
        self._warnColor = Fore.YELLOW
        self._magentaColor = Fore.MAGENTA
        self._timedelta = timedelta
        self.title = title
        self.taskcount = taskcount
        

    def print(self, title, message, color):
        screen_lock.acquire()
        if title is None:
            title = self.title
        if self.taskcount == None:
            print('{}[{}] [{}] {}{}{}'.format(Fore.RESET,datetime.datetime.utcnow() +self._timedelta, title ,color, message, Fore.RESET))
        else:
            if len(str(self.taskcount)) == 1:
                print('{}[{}] [{}] [Task   {}] {}{}{}'.format(Fore.RESET,datetime.datetime.utcnow() +self._timedelta, title,self.taskcount ,color, message, Fore.RESET))
            elif len(str(self.taskcount)) == 2:
                print('{}[{}] [{}] [Task  {}] {}{}{}'.format(Fore.RESET,datetime.datetime.utcnow() +self._timedelta, title,self.taskcount ,color, message, Fore.RESET))
            else:
                print('{}[{}] [{}] [Task {}] {}{}{}'.format(Fore.RESET,datetime.datetime.utcnow() +self._timedelta, title,self.taskcount ,color, message, Fore.RESET))
        screen_lock.release()

    def log(self, message, title = None):
        self.print(title, message, self._logColor,)

    def error(self, message, title = None,log_message = None):
        if log_message != None:
            try:
                with open(getPath() +f"/config/error/{log_file}.txt", 'a') as f: f.write(log_message)
            except Exception as e:
                pass
        self.print(title, message, self._errorColor)

    def success(self, message, title = None):
        self.print(title, message, self._successColor)

    def warn(self, message, title = None):
        self.print(title, message, self._warnColor)
    
    def magenta(self, message, title = None):
        self.print(title,message, self._magentaColor)

    def setTimedelta(self, newTimedelta):
        self._timedelta = newTimedelta

    def setTaskcount(self, taskcount):
        self.taskcount = taskcount
    
    def setTitle(self, title):
        self.title = title

    def setColor(self, messageType, newColor):
        if messageType == 'log':
            self._logColor = newColor
        elif messageType == 'error':
            self._errorColor = newColor
        elif messageType == 'warn':
            self._warnColor = newColor
        elif messageType == 'success':
            self._successColor = newColor