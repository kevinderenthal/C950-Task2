from datetime import datetime
from address import address # type: ignore
# ***** package class *****
#
# contains all functions as well as variables for each package
# all information for each package is derived from the csv or other spreadsheet file imported/used
#
# (package status information)
# - package status of -1 is not loaded and not ready
# - package status of 0 is not loaded and ready
# - packaage status of 1 is loaded
# - package status of 2 is delivered

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