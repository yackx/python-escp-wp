class Node:
    def __init__(self, value=None):
        self.value = value
        self.children = []

    def __iter__(self):
        return iter(self.children)

    def __getitem__(self, item):
        return self.children[item]

    def __len__(self):
        return len(self.children)

    def add(self, value):
        if isinstance(value, list):
            self.children.extend(value)
        else:
            self.children.append(value)

    def __repr__(self):
        return f'Node({self.value}, {self.children})'


class GenericNode:
    def __init__(self, category: str, value=None):
        self.category = category
        self.value = value
        self.children = []

    def __iter__(self):
        return iter(self.children)

    def __getitem__(self, item):
        return self.children[item]

    def __len__(self):
        return len(self.children)

    def add(self, value):
        if isinstance(value, list):
            self.children.extend(value)
        else:
            self.children.append(value)

    def __repr__(self):
        value = f'({self.value})' if self.value else ''
        return f'Node #{self.category}{value} -> {self.children}'
