# custom error
class CalculatorError(Exception):
    pass

class CalculatorModel:
    def __init__(self):
        # main state variables
        self.expression = ""
        self.history = ""
        self.has_result = False
        # operator precedence for the shunting-yard algorithm
        self.precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '%': 2}
        
        # stores the calculation history
        self.history_log = []
        self.MAX_HISTORY = 10 # sets how many entries to remember

    # turns the input string into a list of tokens
    def _tokenize(self, expression_str):
        tokens = []
        i = 0
        while i < len(expression_str):
            char = expression_str[i]

            if char.isspace():
                i += 1
                continue

            # scan for a full number, including decimals
            elif char.isdigit() or char == '.':
                start = i
                decimal_found = False
                while i < len(expression_str) and (expression_str[i].isdigit() or expression_str[i] == '.'):
                    if expression_str[i] == '.':
                        if decimal_found:
                            raise CalculatorError("Invalid number") # catch things like 3.1.4
                        decimal_found = True
                    i += 1
                num_str = expression_str[start:i]
                
                # handle implied multiplication like (5)3
                if tokens and tokens[-1] == ')':
                    tokens.append('*')
                tokens.append(num_str)
                continue

            # handle implied multiplication like 3(5) or (3)(5)
            elif char == '(':
                if tokens and (tokens[-1][-1].isdigit() or tokens[-1] == ')'):
                    tokens.append('*')
                tokens.append(char)

            elif char in self.precedence:
                tokens.append(char)
            
            elif char == ')':
                tokens.append(char)
            
            else:
                raise CalculatorError(f"Invalid character: {char}")

            i += 1
        return tokens

    # converts infix tokens to Reverse Polish Notation (RPN)
    def _to_rpn(self, tokens):
        output = []
        operators = []
        for token in tokens:
            if token.replace('.', '', 1).isdigit():
                output.append(token)
            elif token in self.precedence:
                while (operators and operators[-1] in self.precedence and
                       self.precedence[operators[-1]] >= self.precedence[token]):
                    output.append(operators.pop())
                operators.append(token)
            elif token == '(':
                operators.append(token)
            elif token == ')':
                while operators and operators[-1] != '(':
                    output.append(operators.pop())
                if not operators or operators[-1] != '(':
                    raise CalculatorError("Mismatched parentheses")
                operators.pop()

        while operators:
            if operators[-1] == '(':
                raise CalculatorError("Mismatched parentheses")
            output.append(operators.pop())
        return output

    # calculates the final result from an RPN queue
    def _eval_rpn(self, rpn_queue):
        stack = []
        for token in rpn_queue:
            if token.replace('.', '', 1).isdigit():
                stack.append(float(token))
            elif token in self.precedence:
                if len(stack) < 2:
                    raise CalculatorError("Missing operand")
                b = stack.pop()
                a = stack.pop()
                if token == '+': result = a + b
                elif token == '-': result = a - b
                elif token == '*': result = a * b
                elif token == '/':
                    if b == 0: raise ZeroDivisionError("Division by zero")
                    result = a / b
                elif token == '%': result = a % b
                stack.append(result)
        
        if len(stack) == 1:
            return stack[0]
        else:
            raise CalculatorError("Invalid syntax")

    # allows the controller to get the history
    def get_history(self):
        return self.history_log

    # adds a character to the expression
    def append_char(self, char):
        if self.has_result:
            if char in '%/+-*':
                self.has_result = False
            else:
                self.expression = ""
                self.has_result = False
        self.expression += char

    # handles backspace
    def backspace(self):
        if not self.has_result:
            self.expression = self.expression[:-1]

    # resets the calculator state
    def clear(self):
        self.expression = ""
        self.history = ""
        self.has_result = False
        # also clear the history log
        self.history_log.clear()

    # the main evaluation function
    def evaluate(self):
        if self.has_result or not self.expression:
            return (None, None) # nothing to do
        
        self.history = self.expression
        try:
            tokens = self._tokenize(self.expression)
            
            # handle case of a single number being entered
            if len(tokens) == 1 and tokens[0].replace('.', '', 1).isdigit():
                self.has_result = True
                self.expression = tokens[0]
                return (tokens[0], None)

            rpn_queue = self._to_rpn(tokens)
            total = self._eval_rpn(rpn_queue)

            # format the result cleanly
            if total == int(total): total_str = str(int(total))
            else: total_str = str(round(total, 8))
            if abs(total) > 1e12 or (abs(total) < 1e-6 and total != 0):
                total_str = f"{total:.4g}"
            
            # add the calculation to our history log
            history_entry = f"{self.history} = {total_str}"
            self.history_log.append(history_entry)
            if len(self.history_log) > self.MAX_HISTORY:
                self.history_log.pop(0) # remove the oldest entry

            self.expression = total_str
            self.has_result = True
            return (total_str, None)
            
        except CalculatorError as e:
            self.expression = ""
            self.has_result = True
            return (None, str(e))
        except ZeroDivisionError:
            self.expression = ""
            self.has_result = True
            return (None, "Division by zero")

