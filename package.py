from datetime import datetime
from address import address # type: ignore
""" package class
    - package class is used to create package objects
    Functions:
        - __init__(self, next_node=None)
        - __lt__(self, otherPackage)
        - __le__(self, otherPackage)
        - __gt__(self, otherPackage)
        - __ge__(self, otherPackage)
        - __eq__(self, otherPackage)
        - __ne__(self, otherPackage)
        - set_next_node(self, next_node)
        - get_next_node(self)
        - get_id(self)
        - get_delivery_address(self)
        - get_current_address(self)
        - get_deadline(self)
        - get_weight(self)
        - get_notes(self)
        - get_status(self)
        - get_truck_num(self)
        - getAllPackageAttributes(self)
"""

class package:
    id = -1
    deliveryAddress = None
    currentAddress = None
    deadline = datetime(1,1,1)
    weight = -1
    notes = ""
    status = -1
    truckNum = -1

    # ** initialize function for package **
    # called when creating a package
    # by default next node is None
    def __init__(self, next_node=None):
        self.deliveryAddress = address()
        # sets next node to node passed
        self.next_node = next_node
    
    # ** less than function **
    def __lt__(self, otherPackage):
        # compares two packages based on id value
        # returns true if package is less than the package in the paramters
        return self.id<otherPackage.id
    
    # ** less than or equal function **
    def __le__(self, otherPackage):
    # compares two packages based on id value
    # returns true if package is less than or equal to the package in the paramters
        return self.id<=otherPackage.id

    # ** greater than function **
    def __gt__(self, otherPackage):
        # compares two packages based on id value
        # returns true if package is greater than the package in the paramters
        return self.id>otherPackage.id
    
    # ** greater than or equal to function **
    def __ge__(self, otherPackage):
        # compares two packages based on id value
        # returns true if package is greater than or equal to the package in the paramters
        return self.id>=otherPackage.id
    
    # ** equal to function **
    def __eq__(self, otherPackage):
        # compares two packages based on id value
        # returns true if package is less than the package in the paramters
        if(self.__class__=="package" and otherPackage.__class__=="package"):
            return self.id==otherPackage.id
        else:
            return False
    
    # ** not equal to function **
    def __ne__(self, otherPackage):
        # compares two packages based on id value
        # returns true if package is not equal to the package in the paramters
        if(self.__class__=="package" and otherPackage.__class__=="package"):
            return self.id!=otherPackage.id
        else:
            return True

    # ** set next node function **
    def set_next_node(self, next_node):
        # sets package next node to the package passed in parameters
        self.next_node = next_node
    
    # ** get next node function **
    def get_next_node(self):
        # returns next node (package or None)
        return self.next_node
    
    # ** get id function **
    def get_id(self):
        return self.id

    # ** get delivery address function **
    def get_delivery_address(self):
        return self.deliveryAddress

    # ** get current address function **
    def get_current_address(self):
        return self.currentAddress

    # ** get deadline function **
    def get_deadline(self):
        return self.deadline

    # ** get weight function **
    def get_weight(self):
        return self.weight

    # ** get notes function **
    def get_notes(self):
        return self.notes

    # ** get status function **
    def get_status(self):
        return self.status

    # ** get truck number function **
    def get_truck_num(self):
        return self.truckNum
    
    # ** get package attributes function **
    def getAllPackageAttributes(self):
        return [self.id, self.deliveryAddress, self.currentAddress, self.deadline, self.weight, self.notes, self.status, self.truckNum]