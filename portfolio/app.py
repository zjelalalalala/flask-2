import math

from flask import Flask, render_template, request, send_from_directory
from stack import Stack

app = Flask(__name__)

@app.route('/check-video')
def check_video():
    return "CHECK VIDEO ROUTE WORKS!"

SITE_NAME = "Zje's Web World"


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None

    def add(self, data):
        new_node = Node(data)

        if self.head is None:
            self.head = new_node
        else:
            current = self.head

            while current.next is not None:
                current = current.next

            current.next = new_node

    def delete(self, data):
        current = self.head
        previous = None

        while current is not None:
            if current.data == data:

                if previous is None:
                    self.head = current.next
                else:
                    previous.next = current.next

                return True

            previous = current
            current = current.next

        return False

    def display(self):
        items = []
        current = self.head

        while current is not None:
            items.append(current.data)
            current = current.next

        return items


linked_list = LinkedList()
stack = Stack()
undo_stack = Stack()
current_text = ""
visit_count = 0


# ---------------------------------------------------------------
# Helpers shared by every page
# ---------------------------------------------------------------

@app.before_request
def count_visits():
    """Count page views (ignores CSS/images) for the visitor counter."""
    global visit_count

    if request.endpoint and request.endpoint != 'static':
        visit_count += 1


@app.context_processor
def inject_globals():
    """Values every template can use: the site name and the visitor counter."""
    return {
        'site_name': SITE_NAME,
        'visits': f"{visit_count:06d}"
    }


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


def parse_non_negative(value):
    """Turn form text into a float. Returns None if it is not a valid,
    non-negative, finite number (so the page shows a message, not a crash)."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None

    if math.isnan(number) or math.isinf(number) or number < 0:
        return None

    return number


# ---------------------------------------------------------------
# Main pages
# ---------------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/profile')
def profile():
    return render_template('profile.html')


@app.route('/works')
def works():
    return render_template('works.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


# ---------------------------------------------------------------
# Programming works
# ---------------------------------------------------------------

@app.route('/works/uppercase', methods=['GET', 'POST'])
def uppercase():
    result = None
    original = ''

    if request.method == 'POST':
        original = request.form.get('inputString', '')
        result = original.upper()

    return render_template(
        'touppercase.html',
        result=result,
        original=original
    )


@app.route('/works/area/circle', methods=['GET', 'POST'])
def acircle():
    result = None
    message = None
    radius = ''

    if request.method == 'POST':
        radius = request.form.get('radius', '').strip()
        value = parse_non_negative(radius)

        if value is None:
            message = "Please enter a valid radius (a number, 0 or more)."
        else:
            result = math.pi * value * value

    return render_template(
        'circle.html',
        result=result,
        message=message,
        radius=radius
    )


@app.route('/works/area/triangle', methods=['GET', 'POST'])
def atriangle():
    result = None
    message = None
    base = ''
    height = ''

    if request.method == 'POST':
        base = request.form.get('base', '').strip()
        height = request.form.get('height', '').strip()

        base_value = parse_non_negative(base)
        height_value = parse_non_negative(height)

        if base_value is None or height_value is None:
            message = "Please enter a valid base and height (numbers, 0 or more)."
        else:
            result = 0.5 * base_value * height_value

    return render_template(
        'triangle.html',
        result=result,
        message=message,
        base=base,
        height=height
    )


@app.route('/works/linkedlist', methods=['GET', 'POST'])
def linkedlist():
    message = None

    if request.method == 'POST':
        action = request.form.get('action')
        data = request.form.get('data', '').strip()

        if not data:
            message = "Please enter an item."

        elif action == 'add':
            linked_list.add(data)
            message = "Item added successfully."

        elif action == 'delete':
            if linked_list.delete(data):
                message = "Item deleted successfully."
            else:
                message = "Item not found."

    items = linked_list.display()

    return render_template(
        'linkedlist.html',
        items=items,
        message=message
    )


# ---------------------------------------------------------------
# Stack applications
# ---------------------------------------------------------------

@app.route('/works/stack')
def stack_menu():
    return render_template('stack.html')


@app.route('/works/stack/basic', methods=['GET', 'POST'])
def stack_page():
    message = None

    if request.method == 'POST':
        action = request.form.get('action')
        data = request.form.get('data', '').strip()

        if action == 'push':
            if data:
                stack.push(data)
                message = f"Successfully pushed {data}."
            else:
                message = "Please enter an item."

        elif action == 'pop':
            result = stack.pop()
            message = (
                f"Popped item: {result}"
                if result is not None
                else "The stack is empty."
            )

        elif action == 'peek':
            result = stack.peek()
            message = (
                f"Top element: {result}"
                if result is not None
                else "The stack is empty."
            )

    items = stack.display()

    return render_template(
        'stack_basic.html',
        items=items,
        message=message
    )


@app.route('/works/stack/reverse', methods=['GET', 'POST'])
def reverse_string():
    original = ''
    result = None

    if request.method == 'POST':
        original = request.form.get('text', '')

        # Create a new stack for reversing the string
        reverse_stack = Stack()

        # Push each character onto the stack
        for character in original:
            reverse_stack.push(character)

        # Pop characters to get the reversed string
        reversed_characters = []

        while reverse_stack.peek() is not None:
            reversed_characters.append(reverse_stack.pop())

        result = ''.join(reversed_characters)

    return render_template(
        'stack_reverse.html',
        original=original,
        result=result
    )


@app.route('/works/stack/undo', methods=['GET', 'POST'])
def undo_typing():
    global current_text

    message = None

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'save':
            new_text = request.form.get('text', '').strip()

            if new_text:
                undo_stack.push(current_text)
                current_text = new_text
                message = "Text saved successfully."
            else:
                message = "Please enter some text."

        elif action == 'undo':
            previous_text = undo_stack.pop()

            if previous_text is not None:
                current_text = previous_text
                message = "Undo successful."
            else:
                message = "Nothing to undo."

    return render_template(
        'stack_undo.html',
        current_text=current_text,
        message=message
    )


@app.route('/works/stack/number-bases', methods=['GET', 'POST'])
def number_bases():
    number = None
    base = 2
    result = None
    message = None

    if request.method == 'POST':
        try:
            number = int(request.form.get('number', ''))
            base = int(request.form.get('base', '2'))

            if number < 0:
                message = "Please enter a non-negative integer."

            elif base not in (2, 8, 16):
                message = "Please select base 2, 8, or 16."

            else:
                digits = "0123456789ABCDEF"
                conversion_stack = Stack()

                if number == 0:
                    result = "0"
                else:
                    # Work on a copy so the original number can be shown.
                    remaining = number

                    while remaining > 0:
                        remainder = remaining % base
                        conversion_stack.push(digits[remainder])
                        remaining //= base

                    converted = []

                    while conversion_stack.peek() is not None:
                        converted.append(conversion_stack.pop())

                    result = ''.join(converted)

        except ValueError:
            message = "Please enter a valid whole number."
            number = None
            result = None

    return render_template(
        'stack_number_bases.html',
        number=number,
        base=base,
        result=result,
        message=message
    )


@app.route('/works/stack/infix-postfix', methods=['GET', 'POST'])
def infix_postfix():
    result = None
    message = None
    expression = ''

    if request.method == 'POST':
        expression = request.form.get('expression', '').strip()

        if not expression:
            message = "Please enter an expression."
        else:
            try:
                result = convert_infix_to_postfix(expression)
            except ValueError as error:
                message = str(error)

    return render_template(
        'stack_infix_postfix.html',
        result=result,
        message=message,
        expression=expression
    )


def convert_infix_to_postfix(expression):
    operators = []
    output = []

    precedence = {
        '+': 1,
        '-': 1,
        '*': 2,
        '/': 2,
        '^': 3
    }

    # Convert the expression into tokens.
    tokens = []
    i = 0

    while i < len(expression):
        char = expression[i]

        if char.isspace():
            i += 1

        elif char.isalnum():
            token = char

            while (
                i + 1 < len(expression)
                and expression[i + 1].isalnum()
            ):
                i += 1
                token += expression[i]

            tokens.append(token)
            i += 1

        elif char in '+-*/^()':
            tokens.append(char)
            i += 1

        else:
            raise ValueError(
                "Use letters, numbers, operators, and parentheses."
            )

    if not tokens:
        raise ValueError("Please enter an expression.")

    expect_operand = True

    for token in tokens:

        if token.isalnum():
            if not expect_operand:
                raise ValueError(
                    "Check the expression's operators."
                )

            output.append(token)
            expect_operand = False

        elif token == '(':
            if not expect_operand:
                raise ValueError(
                    "Add an operator before the parenthesis."
                )

            operators.append(token)
            expect_operand = True

        elif token == ')':
            if expect_operand:
                raise ValueError(
                    "Check the expression near the parenthesis."
                )

            while operators and operators[-1] != '(':
                output.append(operators.pop())

            if not operators:
                raise ValueError(
                    "Unmatched closing parenthesis."
                )

            operators.pop()
            expect_operand = False

        elif token in precedence:
            if expect_operand:
                raise ValueError(
                    "An operator needs an operand before it."
                )

            while (
                operators
                and operators[-1] != '('
                and (
                    precedence[operators[-1]] > precedence[token]
                    or (
                        precedence[operators[-1]] == precedence[token]
                        and token != '^'
                    )
                )
            ):
                output.append(operators.pop())

            operators.append(token)
            expect_operand = True

    if expect_operand:
        raise ValueError(
            "The expression cannot end with an operator."
        )

    while operators:
        operator = operators.pop()

        if operator == '(':
            raise ValueError(
                "Unmatched opening parenthesis."
            )

        output.append(operator)

    return ' '.join(output)


if __name__ == "__main__":
    app.run(debug=True)
