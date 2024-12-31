from StoppableThread import StoppableThread

""" threadClass class
    This class is used to create a thread that can be stopped.
    Functions:
        __init__(): Constructor
        run(): Start the thread
        stop(): Stop the thread
"""
class threadClass:

    # Global variables
    st = StoppableThread()

    # Constructor
    @classmethod
    def __init__(self):
        pass

    # ** Run function **
    # Start the thread
    @classmethod
    def run(self):
        self.st.start()

    # ** Stop function **
    # Stop the thread
    @classmethod
    def stop(self):
        self.st.stop()
