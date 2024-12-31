# imports
from datetime import datetime
from time import sleep
import threading

""" StoppableThread class
    This class is used to create a thread that can be stopped.
    Functions:
        __init__(): Constructor
        run(): Start the thread
        stop(): Stop the thread
"""
class StoppableThread(threading.Thread):
    dt = datetime(datetime.today().year, datetime.today().month, datetime.today().day, 8, 0 ,0)
    et = datetime(datetime.today().year, datetime.today().month, datetime.today().day, 18, 0 ,0)

    # ** Constructor **
    def __init__(self):
        super().__init__()
        self._stop_event = threading.Event()

    # ** stop function **
    # stops the thread
    def stop(self):
        self._stop_event.set()

    # ** run function **
    # starts the thread
    def run(self):
        global et, dt
        while not self._stop_event.is_set():
            if(StoppableThread.dt<StoppableThread.et):
                print(self.dt, "\n")
                if(self.dt.minute == 59):
                    self.dt = self.dt.replace(hour = (self.dt.hour + 1)%24)
                self.dt = self.dt.replace(minute = (self.dt.minute + 1)%60)
                sleep(2)
    