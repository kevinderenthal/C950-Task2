from datetime import datetime
from package import package # type: ignore
from hashTable import hashTable # type: ignore
from truck import truck # type: ignore
from address import address # type: ignore
from StoppableThread import StoppableThread #type:ignore
import csv, string, re, datetime, threading


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
thread = None

# ** initialize packages function **
# initializes the list of pacakges from the csv file
def initPackages():
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
def checkSpecialNotes():
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
                    fixAddress(temp)
                    listOfTrucks[findBestTruck(pck)].insertPackage(temp)
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
def setTruckAvgZip():
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
# takes into consideration status of the pacakges if delivered, loaded, ready, or not ready 
def initialFillTrucks():
    global packageFilePathName, totalNumOfPackages, table, listOfTrucks
    #iterate through the packages hash table
    for pck in table.packages:
        hasMore = True
        temp = pck
        while(hasMore == True):
            #check to see if the current package is initialized and is ready to be loaded
            if(temp!=None and temp.id!=-1 and temp.status == 0):
                someTruckHasPackage = False
                #iterate through the list of trucks and check whether or not the package is already loaded
                for t in listOfTrucks:
                    if(t.checkPackagesOnTruck(temp.id)):
                        someTruckHasPackage = True
                # if the package isn't laoded already
                if(someTruckHasPackage==False):
                    best = 9999999999
                    truck = -1
                    # determine the best truck to put it on by finding the closest average zip code
                    for t in listOfTrucks: 
                        if(t.isFull()==False and abs(temp.deliveryAddress.zip-t.zipAvg)<best):
                            best = abs(temp.deliveryAddress.zip-t.zipAvg)
                            truck = t.truckNum
                    if(best != 9999999999):
                        #insert the package to the best truck
                        listOfTrucks[truck].insertPackage(temp)
                        setTruckAvgZip()
            if(temp.get_next_node()!=None):
                temp = temp.get_next_node()
            else:
                hasMore = False 

# ** initialize trucks function **
def initTrucks(numOfTrucks, thread):
    global packageFilePathName, totalNumOfPackages, table, listOfTrucks
    # create number of trucks passed to function appending each to the list of trucks 
    for x in range(0,numOfTrucks):
        listOfTrucks.append(truck(x, thread))

def findBestTruck(p):
    global listOfTrucks
    bestTruck = -1
    maxEmptySpace = -1
    # Determine the best fit truck that is not full at the hub based on how empty they are
    for t in listOfTrucks:
        emptySpace = t.maxPackages - len(t.packageList)
        if emptySpace > maxEmptySpace and not t.isFull() and t.stopDeliverFlag == False and t.status != 2 and t.currAddress.zip == t.hubAddress.zip and t.currAddress.address == t.hubAddress.address and t.currAddress.city == t.hubAddress.city and t.currAddress.state == t.hubAddress.state:
            maxEmptySpace = emptySpace
            bestTruck = t.truckNum
    if bestTruck == -1:
        # If there is no truck at the hub, determine the best fit truck that is not full based on how empty they are
        for t in listOfTrucks:
            emptySpace = t.maxPackages - len(t.packageList)
            if t.stopDeliverFlag == False and t.status == 2 and not t.isFull() and emptySpace > maxEmptySpace:
                maxEmptySpace = emptySpace
                bestTruck = t.truckNum
    return bestTruck

def addSpecialPackagesToTrucks(p):
    global listOfTrucks
    bestTruck = findBestTruck(p)
    if bestTruck != -1:
        if listOfTrucks[bestTruck].currAddress == listOfTrucks[bestTruck].hubAddress and listOfTrucks[bestTruck].locked == False:
            print(f"Loading packages at hub onto truck {bestTruck}")
            # Insert the packages to the best truck
            for pck in listOfDelayedPackages:
                listOfTrucks[bestTruck].insertPackage(table.getPackage(pck))
            # Update the average zip code for the trucks
            setTruckAvgZip()
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
            setTruckAvgZip()

# ** calculate truck order function **
# calculates that order of the trucks doing deliveries based on the locations of the packages which are delayed
def calculateTruckOrder():
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

def checkIfDelayedPackagesReady():
    global listOfDelayedPackages, table
    for p_id in listOfDelayedPackages:
        p = table.getPackage(p_id)
        if "Delayed" in p.notes:
            delay_time_str = re.search(r'\d{1,2}:\d{2} [apAP][mM]', p.notes).group()
            delay_time = datetime.datetime.strptime(delay_time_str, "%I:%M %p")
            delay_time = delay_time.replace(year=datetime.datetime.today().year, 
                                            month=datetime.datetime.today().month, 
                                            day=datetime.datetime.today().day).time()
            if delay_time <= thread.dt.time():
                p.status = 0

# ** deliver function **
#
def deliver():
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
            checkIfDelayedPackagesReady()
            pck = None
            for p_id in listOfDelayedPackages:
                pck = table.getPackage(p_id)
                if pck !=None and pck.status == 0:
                    addSpecialPackagesToTrucks(pck)
            #check if trucks still have packages
            for t in listOfTrucks:
                trucksHavePackages = any(not t.isEmpty() for t in listOfTrucks)
            #if trucks have packages make deliveries
            if(trucksHavePackages):
                #set the status of the trucks to drive based on how many drivers are available
                for d in range(0,driverMaxSize):
                    if(len(truckOrder)>=d+1):
                        #if the current truck is empty then pop it from the truck order list
                        if(listOfTrucks[truckOrder[d]].isEmpty()):
                            listOfTrucks[truckOrder[d]].status = 0
                            listOfTrucks[truckOrder[d]].locked = True
                            truckOrder.pop(d)
                        #if the current truck is not delivering then deliver
                        elif(listOfTrucks[truckOrder[d]].status!=2):
                            listOfTrucks[truckOrder[d]].locked = False
                            listOfTrucks[truckOrder[d]].status = 2
                if(loop == 1):
                    h = threading.Thread(target=checkAndSwitchTrucks)
                    h.start()
                    loop = loop + 1  
        for t in listOfDeliveryThreads:
            t.join()


# ** fix address function **
# updates the address of the package passed to the function to the correct address
def fixAddress(pck):
    global listOfNewAddresses
    for address in listOfNewAddresses:
        if address[0] == pck.id:
            pck.deliveryAddress.updateAddress(address[1].address)
            pck.deliveryAddress.updateCity(address[1].city)
            pck.deliveryAddress.updateState(address[1].state)
            pck.status = 0
            
# ** main function **
def checkAndSwitchTrucks():
    global switchFlag, trucksHavePackages
    while(trucksHavePackages):
        global listOfTrucks, truckOrder
        # Check each truck for packages with early deadlines
        for t in listOfTrucks:
            if(switchFlag == False):
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
                            h = threading.Thread(target=waitAndTravel(listOfTrucks[truckOne.truckNum], listOfTrucks[truckTwo.truckNum]))
                            h.start()
                            h.join()
                            switchFlag = True
                        

def waitAndTravel(t1, t2):    
    global switchFlag
    print("Switching trucks", t1.truckNum, "and", t2.truckNum)
    timeFromOnetoTwo = t1.calculateTimeFromTo(t1.currAddress, t2.currAddress)
    startTime = datetime.datetime(thread.dt.year, thread.dt.month, thread.dt.day, thread.dt.hour, thread.dt.minute, 0)
    endTime = None
    hours = int(timeFromOnetoTwo % 24)
    minutes = int((timeFromOnetoTwo % 1) * 60)
    minutes += startTime.minute    
    hr = 0
    if minutes >= 60:
        hr = int(minutes / 60)
    minutes %= 60
    hours = (hours + startTime.hour + hr) % 24
    endTime = datetime.datetime(startTime.year, startTime.month, startTime.day, hours, minutes, 0)
    while(thread.dt.hour<endTime.hour or thread.dt.minute<endTime.minute):
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

def main():
    global trucksHavePackages, thread
    thread = StoppableThread()
    thread.start()    
    #initialize the packages in from the csv file to the hash table
    initPackages()
    #initialized the trucks
    initTrucks(3, thread)
    #check the special notes of the pacakges (inserting them if needed in to the correct trucks)
    checkSpecialNotes()
    #set the average truck zip code based on packages already inserted
    setTruckAvgZip()
    #fill the trucks in the list of trucks with packages from the hash table based on the average zipe code
    initialFillTrucks()
    #calculate the order of the trucks to start delivery
    calculateTruckOrder()
    # Iterate the list of trucks and print packages using printPackageList for each
    for t in listOfTrucks:
        t.printPackageList()
    #starts the timer for the day simualting time passage starting at 8:00am ending at 11:59am (simulating delivery for the entire day)
    deliver()
    while(trucksHavePackages):
        None
    print("finished")
    thread.stop()
main()