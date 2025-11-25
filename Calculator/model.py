import math
import re

class CalculatorError(Exception):
    pass

class CalculatorModel:
    def __init__(self):
        self.expression = ""
        self.history = ""
        self.has_result = False
        
        # order of operations
        self.precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '%': 2, '^': 3}
        
        # function lookup table
        self.ops = {
            'sin': lambda x: math.sin(math.radians(x)) if self.use_degrees else math.sin(x),
            'cos': lambda x: math.cos(math.radians(x)) if self.use_degrees else math.cos(x),
            'tan': lambda x: math.tan(math.radians(x)) if self.use_degrees else math.tan(x),
            'log': math.log10,
            'ln': math.log,
            'sqrt': math.sqrt
        }
        
        self.history_log = []
        self.MAX_HISTORY = 50 # increased from 10
        self.cycle_index = -1 
        
        self.use_degrees = True 
        self.variables = {'pi': math.pi, 'e': math.e, 'ans': 0.0}

    def _tokenize(self, expr_str):
        # splits the string into numbers, words, and symbols
        pattern = r"(\d*\.?\d+|[a-z]+|[+\-*/%^()=])"
        return [t for t in re.findall(pattern, expr_str) if t.strip()]

    def _to_rpn(self, tokens):
        output = []
        stack = []
        
        for token in tokens:
            if token.replace('.', '', 1).isdigit():
                output.append(token)
            
            # sub in variable values
            elif token in self.variables:
                output.append(str(self.variables[token]))

            elif token in self.ops:
                stack.append(token)
            
            # shunting yard logic
            elif token in self.precedence:
                while (stack and stack[-1] in self.precedence and
                       self.precedence[stack[-1]] >= self.precedence[token]):
                    output.append(stack.pop())
                stack.append(token)
            
            elif token == '(':
                stack.append(token)
            
            elif token == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                if not stack: raise CalculatorError("Mismatched parentheses")
                stack.pop() 
                if stack and stack[-1] in self.ops:
                    output.append(stack.pop())
            
            # catch typos
            else:
                raise CalculatorError(f"Unknown token: {token}")

        while stack:
            if stack[-1] == '(': raise CalculatorError("Mismatched parentheses")
            output.append(stack.pop())
            
        return output

    def _eval_rpn(self, rpn_queue):
        stack = []
        for token in rpn_queue:
            try:
                stack.append(float(token))
                continue
            except ValueError:
                pass

            if token in self.precedence:
                if len(stack) < 2: raise CalculatorError("Missing operand")
                b, a = stack.pop(), stack.pop()
                
                if token == '+': res = a + b
                elif token == '-': res = a - b
                elif token == '*': res = a * b
                elif token == '/': 
                    if b == 0: raise ZeroDivisionError("Division by zero")
                    res = a / b
                elif token == '%': res = a % b
                elif token == '^': res = math.pow(a, b)
                stack.append(res)
            
            # trig and logs
            elif token in self.ops:
                if not stack: raise CalculatorError("Missing argument")
                res = self.ops[token](stack.pop())
                
                # float precision fix (e.g. sin(180))
                if abs(res) < 1e-15: res = 0.0
                stack.append(res)
        
        if len(stack) != 1: raise CalculatorError("Invalid syntax")
        return stack[0]

    def evaluate(self):
        self.cycle_index = -1
        if self.has_result or not self.expression: return (None, None)
        
        self.history = self.expression
        try:
            # handling variable assignment
            if '=' in self.expression:
                var, expr = [x.strip() for x in self.expression.split('=', 1)]
                if not var.isalpha(): raise CalculatorError("Bad variable name")
                
                val = self._eval_rpn(self._to_rpn(self._tokenize(expr)))
                self.variables[var] = val
                
                res_str = f"{val:.4g}" if abs(val) > 1e12 or (abs(val) < 1e-6 and val != 0) else str(val)
                self.expression = res_str
                self.has_result = True
                
                # log assignment to history
                self.history_log.append(f"{var} = {res_str}")
                if len(self.history_log) > self.MAX_HISTORY: self.history_log.pop(0)
                
                return (res_str, None)

            # standard eval
            total = self._eval_rpn(self._to_rpn(self._tokenize(self.expression)))
            self.variables['ans'] = total

            if total == int(total): total_str = str(int(total))
            else: total_str = f"{total:.4g}" if abs(total) > 1e12 or (abs(total) < 1e-6 and total != 0) else str(round(total, 8))
            
            self.history_log.append(f"{self.history} = {total_str}")
            if len(self.history_log) > self.MAX_HISTORY: self.history_log.pop(0)

            self.expression = total_str
            self.has_result = True
            return (total_str, None)
            
        except Exception as e:
            self.expression = ""
            self.has_result = True
            return (None, str(e))

    def get_history(self): return self.history_log
    
    def cycle_up(self):
        if not self.history_log: return None
        self.cycle_index = len(self.history_log) - 1 if self.cycle_index == -1 else max(0, self.cycle_index - 1)
        self.expression = self.history_log[self.cycle_index].split(' = ')[0]
        return self.expression

    def cycle_down(self):
        if self.cycle_index == -1: return None
        self.cycle_index += 1
        if self.cycle_index >= len(self.history_log):
            self.cycle_index = -1; self.expression = ""; return ""
        self.expression = self.history_log[self.cycle_index].split(' = ')[0]
        return self.expression

    def append_char(self, char):
        self.cycle_index = -1
        if self.has_result:
            self.has_result = False
            if char not in '%/+-*^': self.expression = ""
        self.expression += char

    def backspace(self):
        self.cycle_index = -1
        if not self.has_result: self.expression = self.expression[:-1]

    def clear(self):
        self.expression = ""; self.history = ""; self.has_result = False
        self.history_log.clear(); self.cycle_index = -1
    
    def toggle_degrees(self):
        self.use_degrees = not self.use_degrees
        return self.use_degrees