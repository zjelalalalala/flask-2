
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class Stack:
    def __init__(self):
        self.top = None

    def push(self, data):
        new_node = Node(data)

        if self.top:
            new_node.next = self.top

        self.top = new_node

    def pop(self):
        if self.top is None:
            return None

        popped_node = self.top
        self.top = self.top.next
        popped_node.next = None

        return popped_node.data

    def peek(self):
        if self.top:
            return self.top.data

        return None

    def display(self):
        items = []
        current = self.top

        while current:
            items.append(current.data)
            current = current.next

        return items


if __name__ == "__main__":
    stack = Stack()

    stack.push(10)
    stack.push(20)
    stack.push(30)

    print("Stack:", stack.display())
    print("Top element:", stack.peek())
    print("Popped:", stack.pop())
    print("Stack after pop:", stack.display())
