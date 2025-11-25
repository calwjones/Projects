from model import CalculatorModel
from view import CalculatorView

class CalculatorController:
    # link logic to ui
    def __init__(self, root):
        self.model = CalculatorModel()
        self.view = CalculatorView(root, self)
        self.view.bind_global_keys("<Key>", self._handle_keypress)
        # mouse click to edit
        self.view.expr.bind("<Button-1>", lambda e: self._set_edit_mode(True))

    def get_button_command(self, text):
        if text == 'AC': return self.clear
        elif text == '=': return self.calculate
        elif text == 'STO': return lambda: self.append_char('=')
        elif text == 'HIST': return self.show_full_history
        elif text == 'DEG': return self.toggle_degrees
        # auto add bracket
        elif text in ('sin', 'cos', 'tan', 'log', 'ln', 'sqrt'): return lambda: self.append_char(text + '(')
        else: return lambda: self.append_char(text)

    def append_char(self, char):
        # sync model with view
        if self.view.get_expression_state() == 'normal':
            self.model.expression = self.view.get_expression()

        self.model.append_char(char)
        self.view.update_expression(self.model.expression)

    def toggle_degrees(self):
        is_deg = self.model.toggle_degrees()
        self.view.update_deg_btn(is_deg)
        
    def switch_mode(self):
        # toggle simple/sci
        new_state = not self.view.is_sci
        self.view.toggle_sci_mode(new_state)

    def show_full_history(self):
        log = self.model.get_history()
        self.view.open_history_window(log)

    def calculate(self):
        # sync before solving
        current_text = self.view.get_expression()
        
        # fix: strip trailing = to prevent double equals error
        if current_text.endswith('='): current_text = current_text.rstrip('=')
            
        self.model.expression = current_text
        
        result, error = self.model.evaluate()

        if result is None and error is None: return

        if error:
            self.view.update_result(f"Error: {error}")
        else:
            self.view.update_result(result)
            self.view.update_history(self.model.history_log) 
        
        self.view.update_expression(self.model.history + "=")
        self._set_edit_mode(False)

    def clear(self):
        self.model.clear()
        self.view.update_expression("")
        self.view.update_result("")
        self._set_edit_mode(False)

    def cycle_history(self, direction):
        text = self.model.cycle_up() if direction == 'up' else self.model.cycle_down()
        if text is not None: self.view.update_expression(text)

    def _handle_keypress(self, event):
        is_editing = self.view.get_expression_state() == 'normal'
        k = event.keysym

        if k in ('Return', 'equal'):
            self.calculate()
            return "break"
        elif k == 'Escape':
            self.clear()
            return "break"
        
        # nav and edit keys
        elif k in ('Up', 'Down', 'Left', 'Right'):
            if not is_editing: self._set_edit_mode(True)
            
            if k == 'Up': 
                self.cycle_history('up')
                return "break"
            elif k == 'Down': 
                self.cycle_history('down')
                return "break"
            else:
                # let entry handle cursor
                return 

        if is_editing:
            # standard typing
            if k in ('BackSpace', 'Delete', 'Home', 'End'): return
            if event.char and event.char in "0123456789.()+-*/%^abcdefghijklmnopqrstuvwxyz=": return
            return "break"
        
        elif k == 'BackSpace':
            self.model.backspace()
            self.view.update_expression(self.model.expression)
        elif event.char and event.char in "0123456789.()+-*/%^abcdefghijklmnopqrstuvwxyz=":
            self.append_char(event.char)

    def _set_edit_mode(self, active):
        if active:
            self.view.set_display_state('normal')
            self.view.focus_expression()
            if self.model.has_result:
                self.view.update_result("")
                self.model.has_result = False
        else:
            self.view.set_display_state('readonly')
            self.view.focus_root()