import tkinter as tk
from controller import CalculatorController

if __name__ == '__main__':
    # setup window
    main_window = tk.Tk()
    main_window.title("Python Calculator")
    
    # disable resizing
    main_window.resizable(False, False)
    
    # start the app
    app = CalculatorController(main_window)
    main_window.mainloop()