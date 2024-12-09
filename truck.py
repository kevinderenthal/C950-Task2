from package import package # type: ignore
import heapq
from dataclasses import dataclass, field
from typing import Any
from address import address
from datetime import datetime
from timeKeeper import timeKeeper # type: ignore
import csv, string

# **** truck class ****
class truck:
    # priority queue of packages in truck
    packageList = None
    # zip code of the hub
    hubAddress = address("4001 South 700 East", "Salt Lake City", "Utah", 84107)
    # truck number
    truckNum = -1
    # maximum number of packages on the truck
    maxPackages = 16
    # average package zip code of all packages on the truck
    zipAvg = -1
    # status of whether it is ready to drive(1), driving(2), parked(0)
    status = 0
    # current address of the truck
    currAddress = hubAddress
    # whether the truck is occupied by a driver
    occupied = False
    # total mileage driven of the truck
    mileage = 0
    # locked variable to lock out delivering during time interval while driving
    locked = True
    # time that the truck is locked out for while driving
    timeLocked = None
    # distance file path
    distanceFilePathName = ""
    # package to be delivered next
    packageToBeDelivered = None
    # maximum speed for truck
    maxSpeed = 18
    # start time while delivering
    startTime = None
    # end time while delivering
    endTime = None
    # flag to stop delivering
    stopDeliverFlag = False
    # ** initialize function for truck **
    # called when creating a truck
    def __init__(self, num) -> None:
        # sets the truck number to the number passed in the parameters
        self.truckNum = num
        # creates a new empty priority queue for the truck
        self.packageList = []

    # ** get priority function **
    # returns the priority of the package passed in parameters
    def getPriority(self, pck):
        # Check if the package has a deadline that is not end of day
        if pck.deadline != datetime(datetime.now().year, datetime.now().month, datetime.now().day, 17, 0, 0):
            # Assign highest priority if the deadline is not end of day
            priority = 0
        else:
            # Calculate priority based on the distance from the hub address
            priority = abs(self.hubAddress.zip - pck.deliveryAddress.zip) + 1
        print("Priority of package ", pck.id, " is ", (int(priority)))
        return (int(priority))

    # ** insert package function **
    # inserts package passed in parameters into the priority queue
    def insertPackage(self, p):
        # checks to make sure the truck isn't filled before inserting package into the priority queue
        if len(self.packageList) < self.maxPackages:
            # inserts the package into the queue, sets the truck number to the current truck and status as loaded (1)
            p.truckNum = self.truckNum
            p.status = 1
            heapq.heappush(self.packageList,(self.getPriority(p), p))
        else:
            # prints error message if the truck is full while insert a package
            print("Truck" + str(self.truckNum) + " cannot fit item with id " + str(p.id))
            return -1

    # ** check package on truck function **
    # returns whether or not the package passed in parameters is inside of the trucks priority queue
    def checkPackagesOnTruck(self, package):
        # iterates the priority queue and checks whether any packages match the id of the package passed to the function
        for p in self.packageList: # type: ignore
            if p[1].id == package.id:
                return True
        return False

    # ** is full function **
    # returns whether or not the truck is full
    def isFull(self):
        # compares the total number of packages in the priority queue to the maximum allowed packages checking if the queue is full
        if len(self.packageList) < self.maxPackages:
            return False
        return True

    # ** is empty function **
    # returns whether or not the truck is empty
    def isEmpty(self):
        for pck in self.packageList:
            return False
        return True

    # ** remove package function **
    # removes the package passed in parameters from the priority queue
    def removePackage(self, package):
        None

    # ** hasPackages function **
    # returns true if packages are on the truck and false otherwise
    def hasPackages(self):
        if len(self.packageList) > 0:
            return True
        else:
            return False

    # calculates the time needed for path from current address to new address
    def calculateTimeFromTo(self, old, new):
        # distance object containing distance between new/old addresses
        dist = -1
        # the final row and column numbers of the distance
        colFinalNum = -1
        rowFinalNum = -1
        # opens the csv file containing distances between delivery addresses
        distanceFile = csv.reader(open(self.distanceFilePathName + 'WGUPS Distance Table.csv', mode='r'))
        rowNum = -7
        # search the distance file for the old and new addresses
        # iterate through the file by each row
        for row in distanceFile:
            if rowNum == 0:
                colNum = -1
                # iterate through the columns of the current row only if it is at the first row checking the addresses at the top of the table
                for data in row:
                    # clean the data from the cell at current row/column putting it in someData
                    data.translate({ord(c): None for c in string.whitespace})
                    # check if the old address is in someData
                    if old.address in data:
                        colFinalNum = colNum
                    colNum = colNum + 1
            # if past the first row, start to check the addresses on the left side of the table and compare them to the new address
            elif rowNum > 1:
                if new.address in row[0]:
                    rowFinalNum = rowNum
            rowNum = rowNum + 1
        # reopen the distance file from the beginning of the file
        distanceFile = csv.reader(open(self.distanceFilePathName + 'WGUPS Distance Table.csv', mode='r'))
        rowNum = -7
        # iterate the rows in the file until we get to the already founded row number
        for r in distanceFile:
            # if we are at the row already founded grab the data in the cell at the column already found
            if rowNum == rowFinalNum:
                try:
                    dist = float(r[colFinalNum + 1])
                except Exception as error:
                    None
            # if the distance data found is not empty get out of the loop and stop searching for the distance
            if dist != -1:
                break
            rowNum = rowNum + 1
        if dist == -1:
            rowNum = -7
            colFinalNum = -1
            rowFinalNum = -1
            # reopen the distance file from the beginning of the file
            distanceFile = csv.reader(open(self.distanceFilePathName + 'WGUPS Distance Table.csv', mode='r'))
            # iterate through the file by each row
            for row in distanceFile:
                if rowNum == 0:
                    colNum = -1
                    # iterate through the columns of the current row only if it is at the first row checking the addresses at the top of the table
                    for data in row:
                        # clean the data from the cell at current row/column putting it in someData
                        data.translate({ord(c): None for c in string.whitespace})
                        # check if the new address is in someData
                        if new.address in data:
                            colFinalNum = colNum
                        colNum = colNum + 1
                # if past the first row, start to check the addresses on the left side of the table and compare them to the old address
                elif rowNum > 1:
                    if old.address in row[0]:
                        rowFinalNum = rowNum
                rowNum = rowNum + 1
            # reopen the distance file from the beginning of the file
            distanceFile = csv.reader(open(self.distanceFilePathName + 'WGUPS Distance Table.csv', mode='r'))
            rowNum = -7
            # iterate the rows in the file until we get to the already founded row number
            for r in distanceFile:
                # if we are at the row already founded grab the data in the cell at the column already found
                if rowNum == rowFinalNum:
                    try:
                        dist = float(r[colFinalNum + 1])
                    except Exception as error:
                        None
                # if the distance data found is not empty get out of the loop and stop searching for the distance
                if dist != -1:
                    break
                rowNum = rowNum + 1
        hrs = dist / self.maxSpeed
        return hrs

    def stopDelivering(self):
        if self.status != 2:
            # Only stop if not currently delivering
            self.status = 0  # Set status to parked
            self.startTime = None 
            self.endTime = None
            self.locked = True
        elif self.status == 2:
            # Wait for current delivery to complete
            while timeKeeper.dt.hour <= self.endTime.hour and timeKeeper.dt.minute <= self.endTime.minute:
                pass
            self.status = 0
            self.startTime = None
            self.endTime = None
            self.locked = True
            self.stopDeliverFlag = False

    def deliverPackage(self):
        while True:
            # if the truck isn't locked because it was stopped delivery or currently delivering
            if self.locked == False and self.status == 2:
                self.locked = True
                # record the start time of the delivery
                self.startTime = timeKeeper.dt
                # get the package to be delivered from the truck priority queue
                self.packageToBeDelivered = heapq.heappop(self.packageList)[1]
                print("truck ", self.truckNum, "is delivering package", self.packageToBeDelivered.id)
                # calculate time needed for path to new address
                timeToDeliver = self.calculateTimeFromTo(self.currAddress, self.packageToBeDelivered.deliveryAddress)
                # set initial hours and minutes to 0
                hours = 0
                minutes = 0
                # get the hours and minutes from the time previously calculated
                hours = int(timeToDeliver % 24)
                minutes = int((timeToDeliver % 1 * 60))
                # add them to the current time
                minutes = minutes + self.startTime.minute
                hr = 0
                if minutes > 60:
                    hr = int(minutes / 60)
                minutes = minutes % 60
                hours = (hours + self.startTime.hour + hr) % 24
                # set the ending time of delivery to the newly calculated total
                self.endTime = datetime(self.startTime.year, self.startTime.month, self.startTime.day, hours, minutes, 0)
                print("start time is ", self.startTime)
                print("end time is ", self.endTime, "\n")
                # keep looping until the current address is equal to the new address
                while self.status == 2 and self.currAddress != self.packageToBeDelivered.deliveryAddress:
                    # if the current time has reached the ending time of delivery then set the current address to the delivery address as the delivery is completed
                    if self.status == 2 and timeKeeper.dt.hour >= self.endTime.hour and timeKeeper.dt.minute >= self.endTime.minute:
                        self.currAddress = self.packageToBeDelivered.deliveryAddress
                        self.packageToBeDelivered.currentAddress = self.packageToBeDelivered.deliveryAddress
                        print("done")
                        self.locked = False
                        if(self.isEmpty()):
                            print("Truck ", self.truckNum, "is empty")
                            self.status = 0

    def pickupPackage(self, package):
        if not self.locked:
            self.locked = True
            self.startTime = timeKeeper.dt
            timeToPickup = self.calculateTimeFromTo(self.currAddress, package.deliveryAddress)
            hours = int(timeToPickup % 24)
            minutes = int((timeToPickup % 1) * 60)
            minutes += self.startTime.minute
            hr = 0
            if minutes >= 60:
                hr = int(minutes / 60)
            minutes %= 60
            hours = (hours + self.startTime.hour + hr) % 24
            self.endTime = datetime(self.startTime.year, self.startTime.month, self.startTime.day, hours, minutes, 0)
            while timeKeeper.dt < self.endTime:
                pass
            self.currAddress = self.hubAddress
            self.insertPackage(package)
            # Check for more packages at the hub with status 0 and insert them if the truck is not full
            for pck in package.delayedPackages:
                if pck.status == 0 and not self.isFull():
                    self.insertPackage(pck)
            self.locked = False

    # ** print package list **
    # ** prints the ids of all packages in the priority queue for the truck
    def printPackageList(self):
        printTotal = ""
        countPack = 0
        # iterates the priority queue adding the package id's to the output string and counting the number of packages
        for pck in self.packageList:
            if pck[1].status == 1:
                printTotal = printTotal + str(pck[1].id) + " "
                countPack = countPack + 1
        # prints the number of packages then prints the output string
        print("Total packages on truck " + str(self.truckNum) + ": ", countPack)
        print(printTotal)
