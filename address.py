""" Address class
    object that holds the address of a package
    Functions:
        - update (entire) address function
        - update address function
        - update city function
        - update state function
        - update zip code function
"""
class address:
    address = ""
    city = ""
    state = ""
    zip = -1

    # ** Constructor **
    def __init__(self, a="", c="", s="", z=-1) -> None:
        self.address = a
        self.city = c
        self.state = s
        self.zip = z

    # ** update (entire) address function **
    # updates the (entire) address of the package to the parts of the entire address passed to the function
    def update(self, a, c, s, z):
        self.address = a
        self.city = c
        self.state = s
        self.zip = z

    # ** update address function **
    # updates the address of the package to the one passed to the function
    def updateAddress(self, a):
        self.address = a

    # ** update city function **
    # updates the city of the package to the one passed to the function
    def updateCity(self, c):
        self.city = c

    # ** update state function **
    # updates the state of the package to the one passed to the function
    def updateState(self, s):
        self.state = s

    # ** update zip code function **
    # updates the zip code of the package to the one passed to the function
    def updateZip(self, z):
        self.zip = z