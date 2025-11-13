import tkinter as tk
from tkinter import ttk
import tkinter.font as font

class CalculatorView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        
        # styling constants
        self.BG_COLOR = "#1e1e1e"
        self.DISPLAY_BG_COLOR = "#2e2e2e"
        self.BUTTON_BG_COLOR = "#404040"
        self.OPERATOR_BG_COLOR = "#ff9f0a"
        self.TEXT_COLOR = "#ffffff"
        self.HISTORY_TEXT_COLOR = "#a0a0a0"
        self.MAIN_FONT = ('Arial', 18)
        self.RESULT_FONT = ('Arial', 24, "bold")
        self.EXPRESSION_FONT = ('Arial', 16)
        self.HISTORY_FONT = ('Arial', 10)
        
        self.root.configure(bg=self.BG_COLOR)
        self._create_widgets()

    def _create_widgets(self):
        self._configure_styles()
        self._create_displays()
        self._create_buttons()
        self._layout_grid()

    # sets up all the ttk styles
    def _configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        # scrollbar style
        style.configure('Dark.TFrame', background=self.BG_COLOR)
        style.layout('custom.Horizontal.TScrollbar',
                     [('Horizontal.Scrollbar.trough', {'children':
                         [('Horizontal.Scrollbar.thumb', {'expand': '1', 'sticky': 'nswe'})],
                         'sticky': 'we'})])
        style.configure('custom.Horizontal.TScrollbar', troughcolor=self.BG_COLOR, borderwidth=0, relief='flat')
        style.map('custom.Horizontal.TScrollbar', background=[('active', self.OPERATOR_BG_COLOR), ('!active', self.OPERATOR_BG_COLOR)])
        
        # removes default macos button border for a flat look
        style.layout('TButton', [('Button.padding', {'children': [('Button.label', {'sticky': 'nswe'})]})])

        # style for digit buttons
        style.configure('Digit.TButton', background=self.BUTTON_BG_COLOR, foreground=self.TEXT_COLOR,
                        font=self.MAIN_FONT, borderwidth=0, padding=[0, 15])
        style.map('Digit.TButton', background=[('active', self.DISPLAY_BG_COLOR)]) # color when pressed

        # style for operator buttons
        style.configure('Operator.TButton', background=self.OPERATOR_BG_COLOR, foreground=self.TEXT_COLOR,
                        font=self.MAIN_FONT, borderwidth=0, padding=[0, 15])
        style.map('Operator.TButton', background=[('active', '#ffb340')]) # a lighter orange when pressed

    def _create_displays(self):
        # history display
        history_frame = tk.Frame(self.root, bg=self.BG_COLOR)
        history_frame.grid(row=0, column=0, columnspan=4, padx=10, pady=(10,0), sticky="ew")
        self.history_labels = []
        for i in range(5):
            label = tk.Label(history_frame, text="", font=self.HISTORY_FONT,
                             bg=self.BG_COLOR, fg=self.HISTORY_TEXT_COLOR, anchor="e")
            label.pack(side="top", fill="x")
            self.history_labels.append(label)

        # expression display
        self.expression_display = tk.Entry(self.root, font=self.EXPRESSION_FONT, bd=0, justify="right",
                                          bg=self.BG_COLOR, fg=self.TEXT_COLOR,
                                          readonlybackground=self.BG_COLOR, state='readonly',
                                          insertbackground=self.TEXT_COLOR)
        self.expression_display.grid(row=1, column=0, columnspan=4, padx=10, pady=(5, 0), sticky="ew")

        # scrollbar
        scrollbar_frame = ttk.Frame(self.root, style='Dark.TFrame')
        scrollbar_frame.grid(row=2, column=0, columnspan=4, sticky='ew', padx=10)
        self.scrollbar = ttk.Scrollbar(scrollbar_frame, orient='horizontal', command=self.expression_display.xview,
                                       style='custom.Horizontal.TScrollbar')
        self.expression_display.config(xscrollcommand=self.scrollbar.set)

        # result display
        self.result_display = tk.Entry(self.root, font=self.RESULT_FONT, bd=0, width=14, justify="right",
                                     bg=self.DISPLAY_BG_COLOR, fg=self.TEXT_COLOR,
                                     readonlybackground=self.DISPLAY_BG_COLOR, state='readonly')
        self.result_display.grid(row=3, column=0, columnspan=4, padx=10, pady=(0, 10), sticky="ew")

    def _create_buttons(self):
        button_frame = tk.Frame(self.root, bg=self.BG_COLOR)
        button_frame.grid(row=4, column=0, columnspan=4, sticky="nsew")
        buttons = [
            ('(', 1, 0), (')', 1, 1), ('%', 1, 2), ('AC', 1, 3),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2), ('/', 2, 3),
            ('4', 3, 0), ('5', 3, 1), ('6', 3, 2), ('*', 3, 3),
            ('1', 4, 0), ('2', 4, 1), ('3', 4, 2), ('-', 4, 3),
            ('0', 5, 0), ('.', 5, 1), ('=', 5, 2), ('+', 5, 3),
        ]
        for (text, row, col) in buttons:
            # choose the style based on the button text
            button_style = 'Operator.TButton' if text in '()%/AC*/-+= ' else 'Digit.TButton'
            command = self.controller.get_button_command(text)
            
            # create a ttk.Button with the new style
            button = ttk.Button(button_frame, text=text, style=button_style, command=command)
            button.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

    def _layout_grid(self):
        self.root.grid_rowconfigure(0, weight=2)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_rowconfigure(2, weight=0)
        self.root.grid_rowconfigure(3, weight=2)
        self.root.grid_rowconfigure(4, weight=8)
        self.root.grid_columnconfigure(0, weight=1)
        
        # make buttons expand to fill space
        button_frame = None
        for child in self.root.winfo_children():
            if isinstance(child, tk.Frame) and not isinstance(child, ttk.Frame):
                button_frame = child
                break
        if button_frame:
            for i in range(1, 6): button_frame.grid_rowconfigure(i, weight=1)
            # the fix is here: 'uniform' forces columns to be the same size,
            # and 'minsize' gives them a specific minimum width to enforce.
            for i in range(4):
                button_frame.grid_columnconfigure(i, weight=1, uniform="button_grid", minsize=90)

    # shrinks font size if text is too long
    def _fit_font_size(self, widget, text):
        font_name, default_size, style = self.RESULT_FONT
        new_font = font.Font(family=font_name, size=default_size, weight=style)
        
        while new_font.measure(text) > widget.winfo_width() - 20 and new_font['size'] > 10:
            new_font.config(size=new_font['size'] - 2)
            
        widget.config(font=new_font)

    # safely updates the text of a widget
    def _set_display_text(self, widget, text):
        is_readonly = (widget['state'] == 'readonly')
        if is_readonly: widget.config(state=tk.NORMAL)
        
        if widget == self.result_display:
            self._fit_font_size(widget, text)
            
        widget.delete(0, tk.END)
        widget.insert(0, text)
        if is_readonly: widget.config(state='readonly')

    # --- public methods ---
    def get_expression(self):
        return self.expression_display.get()

    def update_expression(self, text):
        self._set_display_text(self.expression_display, text)

    def update_result(self, text):
        self._set_display_text(self.result_display, text)

    def update_history(self, history_list):
        display_list = [""] * 5 + history_list
        display_list = display_list[-5:]
        
        for i, text in enumerate(display_list):
            self.history_labels[i].config(text=text)

    def bind_global_keys(self, key, func):
        self.root.bind(key, func)

    def unbind_global_keys(self, key):
        self.root.unbind(key)

    def bind_edit_keys(self, key, func):
        self.expression_display.bind(key, func)

    def unbind_edit_keys(self, key):
        self.expression_display.unbind(key)

    def set_display_state(self, state):
        self.expression_display.config(state=state)

    def focus_expression(self):
        self.expression_display.focus_set()

    def focus_root(self):
        self.root.focus_set()

