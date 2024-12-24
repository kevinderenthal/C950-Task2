# ** keep time function **
# handles the running of the thread time keeping which runs every second incrementing the minute of the simulation
import datetime
from time import sleep
import threading

class StoppableThread(threading.Thread):
    dt = datetime.datetime(datetime.datetime.today().year, datetime.datetime.today().month, datetime.datetime.today().day, 8, 0 ,0)
    et = datetime.datetime(datetime.datetime.today().year, datetime.datetime.today().month, datetime.datetime.today().day, 18, 0 ,0)

    def __init__(self):
        super().__init__()
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        global et, dt
        while not self._stop_event.is_set():
            if(StoppableThread.dt<StoppableThread.et):
                print(self.dt, "\n")
                if(self.dt.minute == 59):
                    self.dt = self.dt.replace(hour = (self.dt.hour + 1)%24)
                self.dt = self.dt.replace(minute = (self.dt.minute + 1)%60)
                sleep(2)
    