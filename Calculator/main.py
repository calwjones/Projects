import tkinter as tk
from controller import CalculatorController

if __name__ == '__main__':
    # setup the main window
    main_window = tk.Tk()
    main_window.title("Python Calculator")
    
    # let tkinter size the window automatically
    main_window.resizable(False, False)
    
    # create and run the app
    app = CalculatorController(main_window)
    main_window.mainloop()

