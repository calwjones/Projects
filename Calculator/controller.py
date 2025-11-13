from model import CalculatorModel
from view import CalculatorView

class CalculatorController:
    # connects the model (logic) and the view (ui)
    def __init__(self, root):
        self.model = CalculatorModel()
        self.view = CalculatorView(root, self)
        # set up initial key bindings
        self.view.bind_global_keys("<Key>", self._on_keypress)

    # gets the correct function for a button
    def get_button_command(self, text):
        if text in '0123456789.()%/+-*':
            return lambda: self.append_char(text)
        elif text == 'AC':
            return self.clear
        elif text == '=':
            return self.calculate

    # adds a character to the expression
    def append_char(self, char):
        self.model.append_char(char)
        self.view.update_expression(self.model.expression)

    # calculates the final result
    def calculate(self):
        # sync text from display first, in case of edits
        current_text = self.view.get_expression()
        self.model.expression = current_text
        
        result, error = self.model.evaluate()

        # do nothing if model had nothing to calculate
        if result is None and error is None:
            return

        if error:
            self.view.update_result(f"Error: {error}")
        else:
            self.view.update_result(result)
            # if the calculation was a success, update the history
            history_log = self.model.get_history()
            self.view.update_history(history_log)
        
        # show the expression that was just calculated
        self.view.update_expression(self.model.history + "=")
        self._disable_edit_mode()

    # resets the calculator
    def clear(self):
        self.model.clear()
        self.view.update_expression("")
        self.view.update_result("")
        # also clear the history display
        self.view.update_history([])
        self._disable_edit_mode()

    # handles keys when the main window is focused
    def _on_keypress(self, event):
        if event.keysym == "Up":
            self._enable_edit_mode()
        elif event.keysym == "Return" or event.char == '=':
            self.calculate()
        elif event.keysym == "Escape":
            self.clear()
        elif event.keysym == "BackSpace":
            self.model.backspace()
            self.view.update_expression(self.model.expression)
        elif event.char in '0123456789.()%/+-*':
            self.append_char(event.char)

    # handles keys only when the expression entry is being edited
    def _on_edit_keypress(self, event):
        if event.keysym == "Return" or event.char == '=':
            self.calculate()
            return "break" # stops tkinter from also typing the '='
        elif event.keysym == "Escape":
            self.clear()
            return "break"
        # let the widget handle valid keys itself
        elif event.char in '0123456789.()%/+-*' or \
             event.keysym in ("Up", "Left", "Right", "Down", "BackSpace", "Delete", "Home", "End"):
            pass
        # block all other keys
        else:
            return "break"

    # switches to allow editing the expression
    def _enable_edit_mode(self):
        self.view.set_display_state('normal')
        self.view.focus_expression()
        # swap key bindings to be entry-specific
        self.view.bind_edit_keys("<Key>", self._on_edit_keypress)
        self.view.unbind_global_keys("<Key>")
        
        if self.model.has_result:
            self.view.update_result("")
            self.model.has_result = False
        
        if self.model.history:
            self.view.update_expression(self.model.history)
        
    # returns to the default, non-editable state
    def _disable_edit_mode(self):
        self.view.set_display_state('readonly')
        # swap key bindings back to global
        self.view.unbind_edit_keys("<Key>")
        self.view.bind_global_keys("<Key>", self._on_keypress)
        self.view.focus_root()

