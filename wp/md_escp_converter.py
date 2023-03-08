import re

from wp.node import GenericNode
from wp.renderer_abc import Renderer


class MarkdownEscpRenderer(Renderer):
    """Converts Markdown to escp-wp"""

    def __init__(self):
        self.output = ''
        self.nodes = []

    def lexer(self, content: str) -> list[str]:
        split = re.split(r'( |\n|\*|_|\#)', content)
        split = [token for token in split if token not in ['']]
        return split

    def parse(self, tokens: list[str]) -> GenericNode:
        root = GenericNode('root')
        nodes = self._parse(tokens)
        root.add(nodes)
        return root

    def _parse(self, tokens: list[str]) -> list[GenericNode]:
        def next_token(idx) -> str | None:
            try:
                return tokens[idx + 1]
            except IndexError:
                return None

        def find_token_index(token, start) -> int:
            for idx in range(start, len(tokens)):
                if tokens[idx] == token:
                    return idx
            raise ValueError(f'Could not find token {token} from index {start}')

        nodes = []
        i = 0
        while i < len(tokens):
            match tokens[i]:
                case '#':
                    level = 1
                    ii = i
                    while next_token(ii) == '#':
                        level += 1
                        ii += 1
                    j = find_token_index('\n', i+level)
                    children = self._parse(tokens[i+level+1:j])
                    h = GenericNode('heading', level)
                    h.add(children)
                    nodes.append(h)
                    i = j
                case '*' | '_':
                    if next_token(i) == tokens[i]:
                        j = find_token_index(tokens[i], i+2)
                        children = self._parse(tokens[i + 2:j])
                        bold = GenericNode('bold')
                        bold.add(children)
                        nodes.append(bold)
                        i = j+2
                    else:
                        j = find_token_index(tokens[i], i+1)
                        children = self._parse(tokens[i + 1:j])
                        italic = GenericNode('italic')
                        italic.add(children)
                        nodes.append(italic)
                        i = j+1
                case '\n':
                    how_many = 0
                    while i < len(tokens) and tokens[i] == '\n':
                        how_many += 1
                        i += 1
                    if how_many > 1:
                        nodes.append(GenericNode('newline', how_many))
                case _:
                    text = ''
                    j = i
                    while j < len(tokens) and tokens[j] not in ['*', '_', '#']:
                        text += tokens[j]
                        j += 1
                    node = GenericNode('text', text)
                    nodes.append(node)
                    i = j
        return nodes

    def render(self, content: str) -> str:
        """Converts Markdown to escp-wp"""

        tokens = self.lexer(content)
        print(tokens)
        root = self.parse(tokens)
        print(root)
        self._render(root)
        return self.output

    def _render(self, node: GenericNode):
        self.nodes.append(node)
        category = node.category.replace('-', '_')
        func = getattr(self, f'render_{category}')
        return func(node)

    def render_children(self, node: GenericNode):
        for child in node.children:
            self._render(child)

    def render_root(self, node: GenericNode):
        self.output += '[pragma:escp-wp][soft-wrap:on]\n'
        self.render_children(node)

    def render_heading(self, node: GenericNode):
        match node.value:
            case 1:
                self.output += f'[box:on:thickness:2]'
                self.render_children(node)
                self.output += '[box:off]'
            case 2:
                self.output += '[underline:on]'
                self.render_children(node)
                self.output += '[underline:off]'
            case _:
                pass

    def render_bold(self, node: GenericNode):
        self.output += '[bold:on]'
        self.render_children(node)
        self.output += '[bold:off]'

    def render_italic(self, node: GenericNode):
        self.output += '[italic:on]'
        self.render_children(node)
        self.output += '[italic:off]'

    def render_newline(self, node: GenericNode):
        self.output += '\n' * node.value

    def render_text(self, node: GenericNode):
        self.output += node.value
