from tkinter import *

class guiClass:
    def __init__(self):
        self.root = Tk()
        self.root.title("GUI")
        self.root.geometry("400x400")
        self.root.resizable(False, False)

        self.label = Label(self.root, text="Hello World!")
        self.label.pack()

        self.button = Button(self.root, text="Click Me!", command=self.clicked)
        self.button.pack()

        self.root.mainloop()

    def clicked(self):
        self.label.config(text="Button Clicked!")