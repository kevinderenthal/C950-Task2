"""
WGUPS Package Delivery System
# WGUPS Package Delivery System
# Kevin Derenthal
# C950
# Student ID: 010964869
"""

# import statements 
from datetime import datetime
from package import package # type: ignore
from hashTable import hashTable # type: ignore
from truck import truck # type: ignore
from address import address # type: ignore
from StoppableThread import StoppableThread #type:ignore
import csv, string, re, datetime, threading
from threadClass import threadClass
from guiClass import guiClass

# global variables 
PYTHONHASHSEED = 1
packageFilePathName = ""
totalNumOfPackages = 0
table = hashTable()
listOfTrucks = []
truckMaxSize = 16
driverMaxSize = 2
listOfNewAddresses = {(9, address("410 S. State St.", "Salt Lake City", 84111))}
listOfDelayedPackages = []
listOfWrongAddressPackages = []
truckOrder = []
switchFlag = False
listOfDeliveryThreads = []
trucksHavePackages = True

"""
This module simulates a package delivery system for WGUPS. It includes classes and methods to initialize packages, 
trucks, and handle the delivery process.
Classes:
    main: The main class that orchestrates the package delivery system.
Functions:
    __init__(self):
    initPackages(self):
    checkSpecialNotes(self):
    setTruckAvgZip(self):
    initialFillTrucks(self):
    initTrucks(self, numOfTrucks):
    findBestTruck(self, p):
    addSpecialPackagesToTrucks(self, p):
    calculateTruckOrder(self):
    checkIfDelayedPackagesReady(self):
    deliver(self):
    fixAddress(self, pck):
    checkAndSwitchTrucks(self):
    waitAndTravel(self, t1, t2):
    main(self):
"""

class main:
    def __init__(self):
        pass

    # ** initPackages function **
    #Initializes the list of packages from the CSV file and inserts them into the hash table. """
    
    def initPackages(self):
        global packageFilePathName, totalNumOfPackages, table, listOfTrucks
        #sets initial row number to 0 to iterate through file
        rowNum = 0
        #opens csv file
        packageFile = csv.reader(open(packageFilePathName + 'WGUPS Package File.csv', mode ='r'))
        #iterates through file by row
        for row in packageFile:
            #variable to keep track of current package id
            currPackID = ""
            #temporary package to add into hash table
            currPackage = package()
            #sets initial column number to 0 for each row
            columnNum = 0
            #iterates through rows
            rowNum = rowNum + 1
            #iterates through columns in each row
            for data in row:
                #gets rid of any white space
                data.translate({ord(c): None for c in string.whitespace})
                #checks if the current cell data is numeric and is in the first column setting the package id for the current package
                if(columnNum==0):
                    try:
                        int(data)
                        currPackID = data
                    except:
                        None
                #sets the correct variable in the package to the data in the current cell
                if(currPackID!=""):
                    totalNumOfPackages = totalNumOfPackages + 1
                    if(columnNum==0):
                        currPackage.id=int(data)
                    if(columnNum==1):
                        currPackage.deliveryAddress.updateAddress(data)
                    if(columnNum==2):
                        currPackage.deliveryAddress.updateCity(data)
                    if(columnNum==3):
                        currPackage.deliveryAddress.updateState(data)
                    if(columnNum==4):
                        currPackage.deliveryAddress.updateZip(int(data))
                    if(columnNum==5):
                        if(data=="EOD"):
                            data = "5:00 PM"
                        currPackage.deadline= datetime.datetime.strptime(data, "%I:%M %p")
                        currPackage.deadline = currPackage.deadline.replace(year=datetime.datetime.today().year)
                        currPackage.deadline = currPackage.deadline.replace(month=datetime.datetime.today().month)
                        currPackage.deadline = currPackage.deadline.replace(day=datetime.datetime.today().day)
                    if(columnNum==6):
                        currPackage.weight=int(data)
                    if(columnNum==7):
                        currPackage.notes = data
                #iterate the column number
                columnNum = (columnNum + 1)%8
            #insert the package into the hash table
            if(currPackage.id!=-1):
                table.insert(currPackage)
    
    # ** check special notes function **
    # checks the special notes inside of the csv file and deals with them accordingly
    
    def checkSpecialNotes(self):
        global packageFilePathName, totalNumOfPackages, table, listOfTrucks
        for pck in table.packages:
            #check for any packages that need to be on a certain truck 
            if(pck!=None):
                isDone = False
                temp = pck 
                while(isDone==False):
                    if ("Can only be on truck" in temp.notes):
                            truckNum = ''.join(re.findall(r'\d+', temp.notes))
                            listOfTrucks[(int(truckNum))].insertPackage(temp)
                    elif "Delayed" in temp.notes:
                        listOfDelayedPackages.append(temp.id)
                    elif "Wrong address" in temp.notes:
                        self.fixAddress(temp)
                        listOfTrucks[self.findBestTruck(pck)].insertPackage(temp)
                    elif "delivered with" in temp.notes:
                            specialPackageIDs = (re.findall(r'\d+', temp.notes))
                            specialPackageIDs = [eval(i) for i in specialPackageIDs]
                            specialPackageIDs.append(temp.id)
                            truckNum = -1
                            #iterate through all of the packages to see if any are loaded
                            for p in specialPackageIDs:
                                #if any of the packages were already loaded onto a truck, get the truck number
                                if(table.getPackage(p).status==1):
                                    truckNum = table.getPackage(p).truckNum
                            #if a truck number was found for a package then load all packages in the grouping onto that truck
                            if(truckNum!=-1):
                                for p in specialPackageIDs:
                                    if listOfTrucks[truckNum].checkPackagesOnTruck(p):
                                        None
                                    else:
                                        listOfTrucks[truckNum].insertPackage(table.getPackage(p))   
                            #if there was no truck number determiend, get the truck number based on distance, then load it
                            else:
                                truckNum = 0
                                for p in specialPackageIDs:
                                    if listOfTrucks[truckNum].checkPackagesOnTruck(p):
                                        None
                                    else:
                                        listOfTrucks[truckNum].insertPackage(table.getPackage(p))    
                    elif temp.status==-1:
                        temp.status = 0
                    if(temp.get_next_node()!=None):
                        temp = temp.get_next_node()
                    else:
                        isDone = True

    # ** set truck average zip code function **
    # iterates through all of the packages inside of every truck and sets each truck average zip code 
    def setTruckAvgZip(self):
        # iterates through the list of trucks
        for t in listOfTrucks:
            avg = 0
            count = 0
            # iterates through the packages
            for pck in t.packageList:
                #adds the new zip code to the average for the current truck
                temp = pck[1]
                avg = avg + temp.deliveryAddress.zip
                count = count + 1
            if(count>0):
                avg = avg / count
                t.zipAvg = avg
                
    # ** (initial) fill trucks function **
    # fills all trucks in list of trucks with packages in the hash table 
    # takes into consideration status of the packages if delivered, loaded, ready, or not ready 
    def initialFillTrucks(self):
        """
        Fills all trucks in the list of trucks with packages from the hash table.
        Takes into consideration the status of the packages (delivered, loaded, ready, or not ready).
        """
        global packageFilePathName, totalNumOfPackages, table, listOfTrucks, listOfDelayedPackages
        # Counters to keep track of the number of packages with deadlines before end of day in the first two trucks
        truck0_deadline_count = sum(1 for p in listOfTrucks[0].packageList if p[1].deadline < datetime.datetime(datetime.datetime.today().year, datetime.datetime.today().month, datetime.datetime.today().day, 17, 0, 0))
        truck1_deadline_count = sum(1 for p in listOfTrucks[1].packageList if p[1].deadline < datetime.datetime(datetime.datetime.today().year, datetime.datetime.today().month, datetime.datetime.today().day, 17, 0, 0))
        
        # Count packages that must be on a specific truck
        truck_specific_packages = [0] * len(listOfTrucks)
        for p_id in range(1, table.getCountOfPackages() + 1):
            p = table.getPackage(p_id)
            if "Can only be on truck" in p.notes:
                truck_num = int(re.findall(r'\d+', p.notes)[0])
                truck_specific_packages[truck_num] += 1

        # iterate through the packages hash table
        for pck in table.packages:
            hasMore = True
            temp = pck
            while(hasMore == True):
                # check to see if the current package is initialized and is ready to be loaded
                if(temp != None and temp.id != -1 and temp.status == 0):
                    someTruckHasPackage = False
                    # iterate through the list of trucks and check whether or not the package is already loaded
                    for t in listOfTrucks:
                        if(t.checkPackagesOnTruck(temp.id)):
                            someTruckHasPackage = True
                    # if the package isn't loaded already
                    if(someTruckHasPackage == False):
                        # Check if the deadline is not end of day
                        if temp.deadline < datetime.datetime(datetime.datetime.today().year, datetime.datetime.today().month, datetime.datetime.today().day, 17, 0, 0):
                            # Load it to the truck with fewer packages with deadlines before end of day
                            if truck0_deadline_count <= truck1_deadline_count:
                                if not listOfTrucks[0].isFull(truck_specific_packages[0]):
                                    listOfTrucks[0].insertPackage(temp)
                                    truck0_deadline_count += 1
                                elif not listOfTrucks[1].isFull(truck_specific_packages[1]):
                                    listOfTrucks[1].insertPackage(temp)
                                    truck1_deadline_count += 1
                            else:
                                if not listOfTrucks[1].isFull(truck_specific_packages[1]):
                                    listOfTrucks[1].insertPackage(temp)
                                    truck1_deadline_count += 1
                                elif not listOfTrucks[0].isFull(truck_specific_packages[0]):
                                    listOfTrucks[0].insertPackage(temp)
                                    truck0_deadline_count += 1
                            self.setTruckAvgZip()
                        else:
                            best = 9999999999
                            truck = -1
                            # determine the best truck to put it on by finding the closest average zip code
                            for t in listOfTrucks[2:]: 
                                if(t.isFull(truck_specific_packages[t.truckNum]) == False and abs(temp.deliveryAddress.zip - t.zipAvg) < best):
                                    best = abs(temp.deliveryAddress.zip - t.zipAvg)
                                    truck = t.truckNum
                            if(best != 9999999999):
                                # insert the package to the best truck
                                listOfTrucks[truck].insertPackage(temp)
                                self.setTruckAvgZip()
                            else:
                                # if all other trucks are full, use the first two trucks
                                if not listOfTrucks[0].isFull(truck_specific_packages[0]):
                                    listOfTrucks[0].insertPackage(temp)
                                elif not listOfTrucks[1].isFull(truck_specific_packages[1]):
                                    listOfTrucks[1].insertPackage(temp)
                if(temp.get_next_node() != None):
                    temp = temp.get_next_node()
                else:
                    hasMore = False
        print(truck_specific_packages)

    # ** initialize trucks function **
    def initTrucks(self, numOfTrucks):
        global packageFilePathName, totalNumOfPackages, table, listOfTrucks
        # create number of trucks passed to function appending each to the list of trucks 
        for x in range(0,numOfTrucks):
            listOfTrucks.append(truck(x))

    # ** find best truck function **
    # determines the best truck to load a package onto based on various criteria

    def findBestTruck(self, p):
        global listOfTrucks
        bestTruck = -1
        maxEmptySpace = -1
        minDeadlineCount = float('inf')
        deadline_count = [-1] * len(listOfTrucks)
        # Determine the best fit truck that is currently delivering and has fewer packages with deadlines before end of day
        if bestTruck == -1:
            count = 0
            for t in listOfTrucks:
                if t.status == 2 and not t.isFull() and t.stopDeliverFlag == False:
                    deadline_count[count] = sum(1 for pck in t.packageList if pck[1].deadline < datetime.datetime(datetime.datetime.today().year, datetime.datetime.today().month, datetime.datetime.today().day, 17, 0, 0))
                count = count + 1           
            for c in range(len(deadline_count)):
                if(deadline_count[c]!=-1):
                    if deadline_count[c] < minDeadlineCount:
                        minDeadlineCount = deadline_count[c]
                        bestTruck = c

        # If no such truck is found, continue with the rest of the function
        if bestTruck == -1:
            for t in listOfTrucks:
                emptySpace = t.maxPackages - len(t.packageList)
                if emptySpace > maxEmptySpace and not t.isFull() and t.stopDeliverFlag == False and t.status != 2 and t.currAddress.zip == t.hubAddress.zip and t.currAddress.address == t.hubAddress.address and t.currAddress.city == t.hubAddress.city and t.currAddress.state == t.hubAddress.state:
                    maxEmptySpace = emptySpace
                    bestTruck = t.truckNum
            if bestTruck == -1:
                for t in listOfTrucks:
                    emptySpace = t.maxPackages - len(t.packageList)
                    if t.stopDeliverFlag == False and t.status == 2 and not t.isFull() and emptySpace > maxEmptySpace:
                        maxEmptySpace = emptySpace
                        bestTruck = t.truckNum
        return bestTruck

    # ** add special packages to trucks function **
    # adds special packages to the best truck available

    def addSpecialPackagesToTrucks(self, p):
        global listOfTrucks
        bestTruck = self.findBestTruck(p)
        if bestTruck != -1:
            if listOfTrucks[bestTruck].currAddress == listOfTrucks[bestTruck].hubAddress and listOfTrucks[bestTruck].locked == False:
                print(f"Loading packages at hub onto truck {bestTruck}")
                # Count how many packages have deadlines before the end of day for each truck
                deadline_counts = [sum(1 for pck in t.packageList if pck[1].deadline < datetime.datetime(datetime.datetime.today().year, datetime.datetime.today().month, datetime.datetime.today().day, 17, 0, 0)) for t in listOfTrucks]
                max_deadline_count = max(deadline_counts)
                
                # Insert the packages to the best truck up to the maximum count of any truck + 1
                count = 0
                for pck in listOfDelayedPackages:
                    if count < max_deadline_count + 1:
                        listOfTrucks[bestTruck].insertPackage(table.getPackage(pck))
                        count += 1
                    else:
                        break
                
            # Update the average zip code for the trucks
            self.setTruckAvgZip()
            
            # Remove the packages from the list of delayed packages
            for pck in list(listOfDelayedPackages):  # Create a copy of the list to iterate over
                if listOfTrucks[bestTruck].checkPackagesOnTruck(pck):
                    print(f"Package {pck} loaded onto truck {bestTruck}")
                    listOfDelayedPackages.remove(pck)
            else:
                print(f"Truck {bestTruck} is not at the hub. Picking up the package ", p.id)
                if(listOfTrucks[bestTruck].locked == True):
                    listOfTrucks[bestTruck].stopDelivering()
                listOfTrucks[bestTruck].pickupPackage(p, listOfDelayedPackages, table)
                self.setTruckAvgZip()

    # ** calculate truck order function **
    # calculates that order of the trucks doing deliveries based on the locations of the packages which are delayed
    def calculateTruckOrder(self):
        global truckOrder
        truckOrder = []
        delayedTrucks = {}
        for num in range(len(listOfTrucks)):
            delayedTrucks[num] = 0
        #iterate through package ids that are already deemed to be delayed
        for p in listOfDelayedPackages:
            #get package object from package id
            temp = table.getPackage(p)
            #check if package is loaded or delviered
            if(temp.status != 1 and temp.status != 2):
                truck = -1
                best = 99999999
                # determine the best truck to put it on by finding the closest average zip code
                for t in listOfTrucks: 
                    if(abs(temp.deliveryAddress.zip-t.zipAvg)<best):
                        truck = t.truckNum
                        best = abs(temp.deliveryAddress.zip-t.zipAvg)
                        if(truck != -1):
                            #increment delayed trucks array at the corresponding index
                            delayedTrucks[truck] = delayedTrucks[truck] + 1       
        #create copy of original length of delayedTrucks
        originalLen = len(delayedTrucks)
        #set the delivery order of the trucks
        for p in range(originalLen):
            bestIndex = 0
            best = -1
            for element in delayedTrucks:
                if(delayedTrucks[element]>best):
                    best = delayedTrucks[element]
                    bestIndex = element
            truckOrder.append(bestIndex)
            delayedTrucks.pop(bestIndex)

    # ** check if delayed packages ready function **
    # checks if delayed packages are ready to be loaded onto trucks

    def checkIfDelayedPackagesReady(self):
        global listOfDelayedPackages, table
        for p_id in listOfDelayedPackages:
            p = table.getPackage(p_id)
            if "Delayed" in p.notes:
                delay_time_str = re.search(r'\d{1,2}:\d{2} [apAP][mM]', p.notes).group()
                delay_time = datetime.datetime.strptime(delay_time_str, "%I:%M %p")
                delay_time = delay_time.replace(year=datetime.datetime.today().year, 
                                                month=datetime.datetime.today().month, 
                                                day=datetime.datetime.today().day).time()
                if delay_time <= threadClass.st.dt.time():
                    p.status = 0

    # ** deliver function **
    # manages the delivery process, including starting delivery threads and checking for delayed packages

    def deliver(self):
            global listOfTrucks, listOfDeliveryThreads, trucksHavePackages
            loop = 1
            #initialize the list of delivery threads
            for n in range(0,len(listOfTrucks)):
                listOfDeliveryThreads.append(None)
            for n in range(0,len(listOfTrucks)):
                h = threading.Thread(target=listOfTrucks[truckOrder[n]].deliverPackage)
                h.start()
                listOfDeliveryThreads[truckOrder[n]] = h
            #while there are still packages to be delivered keep delivering
            while(trucksHavePackages):
                self.checkIfDelayedPackagesReady()
                pck = None
                for p_id in listOfDelayedPackages:
                    pck = table.getPackage(p_id)
                    if pck !=None and pck.status == 0:
                        self.addSpecialPackagesToTrucks(pck)
                #check if trucks still have packages
                for t in listOfTrucks:
                    trucksHavePackages = any(not t.isEmpty() for t in listOfTrucks)
                #if trucks have packages make deliveries
                if(trucksHavePackages):
                    #set the status of the trucks to drive based on how many drivers are available
                    for d in range(0,driverMaxSize):
                        if(len(truckOrder)>=d+1):
                            #if the current truck is empty then pop it from the truck order list
                            if(listOfTrucks[truckOrder[d]].isEmpty() and listOfTrucks[truckOrder[d]].status!=2):
                                truckOrder.pop(d)
                            #if the current truck is not delivering then deliver
                            elif(listOfTrucks[truckOrder[d]].status!=2):
                                listOfTrucks[truckOrder[d]].locked = False
                                listOfTrucks[truckOrder[d]].status = 2
                    if(loop == 1):
                        h = threading.Thread(target=self.checkAndSwitchTrucks)
                        h.start()
                        loop = loop + 1  
            for t in listOfDeliveryThreads:
                t.join()


    # ** fix address function **
    # updates the address of the package passed to the function to the correct address
    def fixAddress(self, pck):
        global listOfNewAddresses
        for address in listOfNewAddresses:
            if address[0] == pck.id:
                pck.deliveryAddress.updateAddress(address[1].address)
                pck.deliveryAddress.updateCity(address[1].city)
                pck.deliveryAddress.updateState(address[1].state)
                pck.status = 0
                
    # ** check and switch trucks function **
    # checks and switches trucks if necessary based on package deadlines and truck statuses

    def checkAndSwitchTrucks(self):
        global switchFlag, trucksHavePackages
        while(trucksHavePackages):
            global listOfTrucks, truckOrder
            if len(truckOrder) > 2:
                # Check each truck for packages with early deadlines
                for t in listOfTrucks:
                    if(switchFlag == False and t.stopDeliverFlag == False):
                        truckOne = None
                        truckTwo = None
                        if(t.status == 0 or t.status == 1):
                            for p in t.packageList:
                                if p[1].deadline.hour < 17 and truckTwo == None:
                                    truckOne = t
                                    #Find a truck that has no early deadlines
                                    for other_truck in listOfTrucks:
                                        if(other_truck.status == 2 and other_truck.endTime!=None and truckTwo == None):
                                            for op in other_truck.packageList:
                                                if not op[1].deadline.hour < 17:
                                                    truckTwo = other_truck
                                                    break
                        #If there is both a truck that is not driving with deadlines and a truck that is driving without deadlines then switch
                        if(truckOne != None and truckTwo != None):
                            # Update truck order                                                                                                                                                                                                                                                                                                                                                                              `
                            if truckOne.truckNum in truckOrder:
                                idxOne = truckOrder.index(truckOne.truckNum)
                                if truckTwo.truckNum in truckOrder:
                                    idxTwo = truckOrder.index(truckTwo.truckNum)
                                    listTh = []
                                    h = threading.Thread(target=truckOne.stopDelivering())
                                    listTh.append(h)
                                    h.start()
                                    h = threading.Thread(target=truckTwo.stopDelivering())
                                    listTh.append(h)
                                    h.start()
                                    for th in listTh:
                                        th.join()
                                    truckOrder[idxOne] = truckTwo.truckNum
                                    truckOrder[idxTwo] = truckOne.truckNum
                                    h = threading.Thread(target=self.waitAndTravel(listOfTrucks[truckOne.truckNum], listOfTrucks[truckTwo.truckNum]))
                                    h.start()
                                    h.join()
                                    switchFlag = True

    # ** wait and travel function **
    # manages the process of switching trucks and updating their statuses and locations
    
    def waitAndTravel(self, t1, t2):    
        global switchFlag
        print("Switching trucks", t1.truckNum, "and", t2.truckNum)
        timeFromOnetoTwo = t1.calculateTimeFromTo(t1.currAddress, t2.currAddress)
        startTime = datetime.datetime(threadClass.st.dt.year, threadClass.st.dt.month, threadClass.st.dt.day, threadClass.st.dt.hour, threadClass.st.dt.minute, 0)
        endTime = None
        hours = int(timeFromOnetoTwo % 24)
        minutes = int((timeFromOnetoTwo % 1) * 60)
        minutes = minutes + startTime.minute    
        hr = 0
        if minutes >= 60:
            hr = int(minutes / 60)
        minutes %= 60
        hours = (hours + startTime.hour + hr) % 24
        endTime = datetime(startTime.year, startTime.month, startTime.day, hours, minutes, 0)
        while(threadClass.st.dt.hour<endTime.hour or threadClass.st.dt.minute<endTime.minute):
            None
        t2.currAddress = t1.currAddress
        t1.status = 2
        t2.status = 1
        t1.locked = False
        t1.stopDeliverFlag = False
        t2.stopDeliverFlag = False
        switchFlag = False
        print("Switch Complete")
        print("\nTruck ", t1.truckNum  , " is now at ", t1.currAddress.address, t1.currAddress.city, t1.currAddress.state, t1.currAddress.zip)
        print("\nTruck ", t2.truckNum , " is now at ", t2.currAddress.address, t2.currAddress.city, t2.currAddress.state, t2.currAddress.zip)
        print("\n)")

    # ** main function **
    # runs the entire package delivery system

    def main(self):
        gui = guiClass()
        threadClass.run()
        #initialize the packages in from the csv file to the hash table
        self.initPackages()
        #initialized the trucks
        self.initTrucks(3)
        #check the special notes of the pacakges (inserting them if needed in to the correct trucks)
        self.checkSpecialNotes()
        #set the average truck zip code based on packages already inserted
        self.setTruckAvgZip()
        #fill the trucks in the list of trucks with packages from the hash table based on the average zipe code
        self.initialFillTrucks()
        #calculate the order of the trucks to start delivery
        self.calculateTruckOrder()
        # Iterate the list of trucks and print packages using printPackageList for each
        for t in listOfTrucks:
            t.printPackageList()
        #starts the timer for the day simualting time passage starting at 8:00am ending at 11:59am (simulating delivery for the entire day)
        self.deliver()
        while(trucksHavePackages):
            None
        print("finished")
        threadClass.stop()


# main function call to run the package delivery system
m = main()
m.main()