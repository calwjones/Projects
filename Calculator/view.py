import tkinter as tk
from tkinter import ttk
import tkinter.font as font

class CalculatorView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.is_sci = False 
        
        # design system
        self.colors = {
            'bg': "#1e1e1e", 'display_bg': "#2e2e2e", 
            'btn_bg': "#404040", 'accent': "#ff9f0a", 
            'text': "#ffffff", 'dim': "#a0a0a0"
        }
        self.fonts = {
            'main': ('Arial', 18), 'result': ('Arial', 24, "bold"),
            'expr': ('Arial', 16), 'history': ('Arial', 10),
            'small': ('Arial', 10) 
        }
        
        self.root.configure(bg=self.colors['bg'])
        self._setup_ui()

    def _setup_ui(self):
        self._style_widgets()
        self._build_displays()
        self._build_buttons()
        # grid weights
        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.btn_frame.grid_rowconfigure(tuple(range(1, 7)), weight=1)
        
        # default to simple
        self.toggle_sci_mode(False)

    def _style_widgets(self):
        s = ttk.Style()
        s.theme_use('clam')

        base = {'borderwidth': 0, 'relief': 'flat', 'font': self.fonts['main'], 'padding': [0, 15]}
        
        # number keys
        s.configure('Digit.TButton', background=self.colors['btn_bg'], foreground=self.colors['text'], **base)
        s.map('Digit.TButton', background=[('active', self.colors['display_bg'])])

        # function keys
        s.configure('Operator.TButton', background=self.colors['accent'], foreground=self.colors['text'], **base)
        s.map('Operator.TButton', background=[('active', '#ffb340')])

    def _build_displays(self):
        # top bar
        top_bar = tk.Frame(self.root, bg=self.colors['bg'])
        top_bar.grid(row=0, column=0, columnspan=6, sticky="ew", padx=10, pady=(5, 0))

        # mode toggle
        self.mode_btn = tk.Label(top_bar, text="SCI", font=self.fonts['small'], 
                                bg=self.colors['btn_bg'], fg=self.colors['text'], width=4)
        self.mode_btn.pack(side="right", padx=2)
        self.mode_btn.bind("<Button-1>", lambda e: self.controller.switch_mode())

        # deg/rad toggle
        self.deg_switch = tk.Label(top_bar, text="DEG", font=self.fonts['small'],
                                  bg=self.colors['accent'], fg=self.colors['text'], width=4)
        self.deg_switch.pack(side="right", padx=2)
        self.deg_switch.bind("<Button-1>", lambda e: self.controller.toggle_degrees())

        # history stack
        hist_frame = tk.Frame(top_bar, bg=self.colors['bg'])
        hist_frame.pack(side="left", fill="x", expand=True)
        
        self.hist_lbls = []
        for _ in range(3):
            l = tk.Label(hist_frame, text=" ", font=self.fonts['history'], bg=self.colors['bg'], fg=self.colors['dim'], anchor="w")
            l.pack(side="top", fill="x")
            self.hist_lbls.append(l)

        # input line
        self.expr = tk.Entry(self.root, font=self.fonts['expr'], bd=0, justify="right", 
                            bg=self.colors['bg'], fg=self.colors['text'], 
                            readonlybackground=self.colors['bg'], state='readonly', insertbackground=self.colors['text'])
        self.expr.grid(row=1, column=0, columnspan=6, sticky="ew", padx=10, pady=(5,0))

        # result line
        self.res = tk.Entry(self.root, font=self.fonts['result'], bd=0, justify="right", 
                           bg=self.colors['display_bg'], fg=self.colors['text'], 
                           readonlybackground=self.colors['display_bg'], state='readonly')
        self.res.grid(row=2, column=0, columnspan=6, sticky="ew", padx=10, pady=(0,10))

    def _build_buttons(self):
        self.btn_frame = tk.Frame(self.root, bg=self.colors['bg'])
        self.btn_frame.grid(row=3, column=0, columnspan=6, sticky="nsew")

        # button layout
        btns = [
            # sci cols
            ('sin', 1, 0), ('cos', 2, 0), ('tan', 3, 0), ('^', 4, 0), ('pi', 5, 0),
            ('ln', 1, 1), ('log', 2, 1), ('sqrt', 3, 1), ('STO', 4, 1), ('%', 5, 1),
            
            # simple cols
            ('(', 1, 2), (')', 1, 3), ('HIST', 1, 4), ('AC', 1, 5),
            ('7', 2, 2), ('8', 2, 3), ('9', 2, 4), ('/', 2, 5),
            ('4', 3, 2), ('5', 3, 3), ('6', 3, 4), ('*', 3, 5),
            ('1', 4, 2), ('2', 4, 3), ('3', 4, 4), ('-', 4, 5),
            ('0', 5, 2), ('.', 5, 3), ('=', 5, 4), ('+', 5, 5),
        ]

        self.buttons = {}
        self.sci_btns = [] 

        for (txt, r, c) in btns:
            if txt in '0123456789.': style = 'Digit.TButton'
            else: style = 'Operator.TButton'

            cmd = self.controller.get_button_command(txt)
            btn = ttk.Button(self.btn_frame, text=txt, style=style, command=cmd)
            self.buttons[txt] = btn
            btn.grid(row=r, column=c, padx=2, pady=2, sticky="nsew")
            
            if c < 2: self.sci_btns.append(btn)

    def toggle_sci_mode(self, show):
        self.is_sci = show
        f = self.btn_frame
        
        if show:
            self.root.geometry("480x550")
            for btn in self.sci_btns: btn.grid()
            # uniform columns
            for i in range(6): f.grid_columnconfigure(i, weight=1, uniform="btns")
        else:
            self.root.geometry("320x550")
            for btn in self.sci_btns: btn.grid_remove()
            # collapse sci cols
            for i in range(2): f.grid_columnconfigure(i, weight=0, uniform="")
            for i in range(2, 6): f.grid_columnconfigure(i, weight=1, uniform="btns")
            
        self.mode_btn.config(text="SIMP" if show else "SCI", bg=self.colors['accent'] if show else self.colors['btn_bg'])

    def _set_text(self, w, txt):
        ro = w['state'] == 'readonly'
        if ro: w.config(state=tk.NORMAL)
        
        if w == self.res:
            fc = self.fonts['result']
            f = font.Font(family=fc[0], size=fc[1], weight=fc[2])
            while f.measure(txt) > w.winfo_width() - 20 and f['size'] > 10:
                f.config(size=f['size'] - 2)
            w.config(font=f)
            
        w.delete(0, tk.END); w.insert(0, txt)
        if ro: w.config(state='readonly')

    def open_history_window(self, history_list):
        top = tk.Toplevel(self.root)
        top.title("History")
        top.geometry("300x400")
        top.configure(bg=self.colors['bg'])
        
        txt = tk.Text(top, bg=self.colors['bg'], fg=self.colors['text'], font=self.fonts['history'])
        txt.pack(fill="both", expand=True)
        for item in history_list: txt.insert(tk.END, item + "\n")
        txt.config(state='disabled')

    # getters and setters
    def get_expression(self): return self.expr.get()
    def update_expression(self, txt): self._set_text(self.expr, txt)
    def update_result(self, txt): self._set_text(self.res, txt)
    
    def update_history(self, h):
        for l, t in zip(self.hist_lbls, ([" "]*3 + h)[-3:]): l.config(text=t if t else " ")

    def update_deg_btn(self, is_deg):
        self.deg_switch.config(text="DEG" if is_deg else "RAD", bg=self.colors['accent'] if is_deg else "#505050")

    def bind_global_keys(self, k, f): self.root.bind(k, f)
    def unbind_global_keys(self, k): self.root.unbind(k)
    def bind_edit_keys(self, k, f): self.expr.bind(k, f)
    def unbind_edit_keys(self, k): self.expr.unbind(k)
    def get_expression_state(self): return self.expr['state']
    def set_display_state(self, s): self.expr.config(state=s)
    def focus_expression(self): self.expr.focus_set()
    def focus_root(self): self.root.focus_set()