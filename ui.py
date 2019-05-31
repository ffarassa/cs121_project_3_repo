from tkinter import *
import tkinter.ttk as ttk
from functools import partial
from tkinter.font import Font

import os
from VerticalScrolledFrame import VerticalScrolledFrame
from analytics import *

def changeWhenHovered(widget, color, underlineBool, event):
    widget["fg"] = color
    widget["cursor"] = "hand2"
    f = Font(widget, widget["font"])
    f.configure(underline = underlineBool)
    widget.configure(font=f)

def openFile(filename, event):
    print(filename)
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener ="open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])    
        
class UI():
    def __init__(self): 
        self.root = Tk()
        self.root.wm_title("Search Engine (Miles and Farshad)")
        self.root.geometry("400x400")

        # Search Bar
        if True:
            self.taskbar = Frame(self.root)
                       
            self.SearchText = Label(self.taskbar, text="Search: ")
            self.SearchText.grid(row=0, column = 0, sticky=W, padx = (20, 0),pady = (10, 0))
            
            self.SearchEntry = Entry(self.taskbar, width=40)
            self.SearchEntry.grid(row=0, column = 1, sticky=W+E,  pady = (10, 0))
            self.SearchEntry.bind('<Return>', self.Query)
            
            self.taskbar.pack(fill = X)

            border = Frame(self.root, bg = "gray", height = 1)
            border.pack(fill = X, pady = 10)

        # Results
        if True:
            self.frame = None
            self.newFrame()
            button = Label(self.frame.interior, text="(search results will appear here)")
            button.grid()

    def newFrame(self):
        if (self.frame != None):
            self.frame.pack_forget()
            self.frame.destroy()
        self.frame = VerticalScrolledFrame(self.root, height = 500)
        self.frame.pack(fill = BOTH, expand=True)
            
    def Query(self, event):
        queryText = self.SearchEntry.get().lower()
        if (queryText.strip() == ""):
            pass
        else:
            print("Seaching for " + queryText)
            self.newFrame()
            button = Label(self.frame.interior, text="Searching")
            button.grid()
            
            list = getSortedPostingList(queryText, 30)
            all_links = []
            
            self.newFrame()
            if (list == None):
                button = Label(self.frame.interior, text=("No search results found for query '" + queryText) + "'")
                button.grid(sticky = W)
            else:
                rownumber = 0
                for item in list:
                    all_links.append(item[0])
                    button = Label(self.frame.interior, text=(str(rownumber + 1) + ") http://" + item[0]), anchor="w")
                    button.bind("<Button-1>", partial(openFile, ("http://" + str(item[0])))) #
                    button.bind("<Enter>", partial(changeWhenHovered, button, "blue", True))
                    button.bind("<Leave>", partial(changeWhenHovered, button, "black", False))
                    button2 = Label(self.frame.interior, text=str(item[1]), anchor="w", fg = "gray")
                    button3 = Label(self.frame.interior, text=" ", anchor="w")
                    button.pack(fill = BOTH)
                    button2.pack(fill = BOTH)
                    button3.pack(fill = BOTH)
                    rownumber += 1

if __name__ == "__main__":
    ui = UI()
    mainloop()
