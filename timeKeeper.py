# ** keep time function **
# handles the running of the thread time keeping which runs every second incrementing the minute of the simulation
import datetime
from time import sleep
from programStatus import programStatus # type: ignore

class timeKeeper():
    dt = datetime.datetime(datetime.datetime.today().year, datetime.datetime.today().month, datetime.datetime.today().day, 8, 0 ,0)
    et = datetime.datetime(datetime.datetime.today().year, datetime.datetime.today().month, datetime.datetime.today().day, 18, 0 ,0)
    @classmethod
    def keepTime(self):
        global et, dt
        while programStatus.trucksHavePackages:
            if(timeKeeper.dt<timeKeeper.et):
                print(self.dt, "\n")
                if(self.dt.minute == 59):
                    self.dt = self.dt.replace(hour = (self.dt.hour + 1)%24)
                self.dt = self.dt.replace(minute = (self.dt.minute + 1)%60)
                sleep(2)
