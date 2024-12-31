from package import package # type: ignore

""" hashTable class
    - hashTable class is used to create hash table objects
    Functions:
        - __init__(self, initCapacity=30)
        - insert(self, package)
        - getPackage(self, packageID)
        - printTable(self)
        - getCountOfPackages(self)
"""
class hashTable:

    # ** initialize function for hash table **
    # called when creating a hash table
    def __init__(self, initCapacity=30) -> None:
        self.packages = [None]*initCapacity
        self.capacity = initCapacity

    # ** insert function for hash table **
    # inserts a package into the hash table
    def insert (self, package):
        # iterates the hash table and inserts pacakge
        # based on hash val which is the hash function of the package id modulus the size or capacity of the hash table
        hashval = hash(package.id)%self.capacity
        if(self.packages[hashval]!=None):
            temp = self.packages[hashval]
            while temp.get_next_node()!=None:
                temp = temp.get_next_node()
            temp.set_next_node(package)
        else:
            self.packages[hashval] = package

    # ** get package function **
    # returns a pacakge inside of the hash table based on the package id
    def getPackage (self, packageID):
        # iterates the hash table and finds the pacakge
        # based on hash val which is the hash function of the package id modulus the size or capacity of the hash table
        hashval = hash(packageID)%self.capacity
        p = self.packages[hashval]
        while(p.id!=packageID):
            p = p.get_next_node()
        return p
    
    # ** print table function **
    # prints the entire hash table out
    def printTable(self):
        #iterates the hash table and adds each package id to a string which is then printed
        for p in self.packages:
            if(p!=None):
                temp = p
                pck = ""
                pck = str(p.id)
                while(temp.get_next_node()!=None):
                    temp = temp.get_next_node()
                    pck = pck + " , " + str(temp.id)
                print(pck)

    # ** get count of packages function **
    # returns the count of how many packages are in the table
    def getCountOfPackages(self):
        count = 0
        for p in self.packages:
            while p is not None:
                count += 1
                p = p.get_next_node()
        return count