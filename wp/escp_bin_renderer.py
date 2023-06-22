import math
import re
import sys
from decimal import Decimal

import escp

from .node import GenericNode
from .renderer_abc import Renderer
from .magic_encoding import plain_char_substitutions, char_set_substitutions


def render_escp(content: str, *, pins: int, soft_wrap=True) -> bytes:
    renderer = EscpToBinRenderer(pins=pins, soft_wrap=soft_wrap)
    return renderer.render(content)


class EscpToBinRenderer(Renderer):

    def __init__(
            self,
            pins: int,
            *,
            soft_wrap=True, init_on_render=False, form_feed_after_render=False):
        self.escp_commands = escp.lookup_by_pins(pins)
        self.pins = pins
        self.soft_wrap = soft_wrap
        self.init_on_render = init_on_render
        self.form_feed_after_render = form_feed_after_render
        self.directives_processed_once = []
        self.tokens = []
        self.box_width = None
        self.current_line_position_inch = 0
        self.page_width_inches = 8.0
        self.cpi = 10
        self.margin_left = 0
        self.margin_right = 80
        self.previous_node = None
        self.text_buffer = ''

    def cr_lf(self, how_many=1):
        for _ in range(how_many):
            self.escp_commands.cr_lf()
        self.current_line_position_inch = 0

    def text(self, text: str):
        self.escp_commands.text(text)
        self.current_line_position_inch += self.text_width_inches(text)

    def magic_text(self, text: str):
        self.escp_commands.magic_text(
            text,
            character_set_substitution=char_set_substitutions,
            plain_text_substitution=plain_char_substitutions
        )
        self.current_line_position_inch += self.text_width_inches(text)

    def lexer(self, content: str) -> list[str]:
        split = re.split(r'( |\n|\[|]|:)', content)
        split = [token for token in split if token not in ['']]
        return split

    def parse(self, tokens: list[str]) -> GenericNode:
        root = GenericNode('root')
        nodes = self._parse(tokens)
        root.add(nodes)
        return root

    def _parse(self, tokens: list[str]) -> list[GenericNode]:
        def extract_directive_with_params(start_at, end_at) -> list[str]:
            directive_tokens = tokens[start_at+1:end_at]
            return [t for t in directive_tokens if t != ':']

        def find_next_closing_bracket(start_at) -> int:
            return tokens[start_at:].index(']') + start_at

        def find_directive_index(start_at, directive, first_arg) -> int:
            for i in range(start_at, len(tokens)):
                if tokens[i] == '[' and tokens[i+1] == directive and tokens[i+3] == first_arg:
                    return i

        nodes = []
        i = 0
        while i < len(tokens):
            match tokens[i]:
                case '[':
                    closing_bracket_index = find_next_closing_bracket(i)
                    directive_with_params = extract_directive_with_params(i, closing_bracket_index)
                    directive = directive_with_params[0]
                    args = directive_with_params[1:]
                    match directive:
                        case 'init':
                            # no arg
                            nodes.append(GenericNode(directive, []))
                            i = closing_bracket_index + 1
                        case 'pragma':
                            nodes.append(GenericNode(directive, args[0]))
                            i = closing_bracket_index + 1
                        case 'soft-wrap':
                            # directive on/off
                            nodes.append(GenericNode(directive, self._on_off_as_bool(args[0])))
                            i = closing_bracket_index + 1
                        case 'bold' | 'italic' | 'underline' | 'condensed' | 'box' | 'proportional' | \
                             'double-width' | 'double-height':
                            # directive w/ closing tag - 1 on/off argument + other optional arguments
                            next_directive_index = find_directive_index(i, directive, 'off')
                            args[0] = self._on_off_as_bool(args[0])
                            node = GenericNode(directive, args)
                            # TODO Not part of the lexer
                            children = self._parse(tokens[closing_bracket_index+1:next_directive_index])
                            node.add(children)
                            nodes.append(node)
                            i = find_next_closing_bracket(next_directive_index) + 1
                        case 'justification' | 'symbol' | 'font':
                            # 1+ string argument(s)
                            nodes.append(GenericNode(directive, args))
                            i = closing_bracket_index + 1
                        case 'cpi':
                            # 1 int argument
                            nodes.append(GenericNode(directive, [int(args[0])]))
                            i = closing_bracket_index + 1
                        case 'line-spacing':
                            # 2 int arguments
                            nodes.append(GenericNode(directive, [int(args[0]), int(args[1])]))
                            i = closing_bracket_index + 1
                        case 'margin' | 'page-length':
                            # 1 string argument + 1 int argument
                            nodes.append(GenericNode(directive, [args[0], int(args[1])]))
                            i = closing_bracket_index + 1
                        case _:
                            raise ValueError(f'Unknown directive: {directive}')
                case '\n':
                    how_many = 0
                    while i < len(tokens) and tokens[i] == '\n':
                        how_many += 1
                        i += 1
                    nodes.append(GenericNode('newline', how_many))
                case ' ':
                    how_many = 0
                    while i < len(tokens) and tokens[i] == ' ':
                        how_many += 1
                        i += 1
                    nodes.append(GenericNode('space', how_many))
                case _:
                    text = ''
                    j = i
                    while j < len(tokens) and tokens[j] not in ['[', '\n', ' ']:
                        text += tokens[j]
                        j += 1
                    node = GenericNode('text', text.strip())
                    nodes.append(node)
                    i = j
        return nodes

    def _render(self, node: GenericNode):
        category = node.category.replace('-', '_')
        func = getattr(self, f'render_{category}')
        func(node)
        self.previous_node = node

    def render_root(self, node: GenericNode):
        if self.init_on_render:
            self.escp_commands.init()
        self.render_children(node)
        if self.form_feed_after_render:
            self.escp_commands.form_feed()
        else:
            self.cr_lf()

    def render_pragma(self, node: GenericNode):
        # TODO Check this is the first directive
        if node.category in self.directives_processed_once:
            raise ValueError('Pragma directive can only be used once')
        match node.value:
            case 'escp-wp':
                pass
            case 'soft-wrap':
                self.soft_wrap = node.value
            case _:
                raise ValueError(f'Unknown pragma: {node.value}')
        self.directives_processed_once.append('pragma')

    def render_init(self, node: GenericNode):
        assert node.value == []
        self.escp_commands.init()

    def render_margin(self, node: GenericNode):
        side = next(m for m in escp.Margin if m.name.lower() == node.value[0])
        value = node.value[1]
        match side:
            case escp.Margin.LEFT: self.margin_left = value
            case escp.Margin.RIGHT: self.margin_right = value
        self.escp_commands.margin(side, value)

    def render_line_spacing(self, node: GenericNode):
        self.escp_commands.line_spacing(node.value[0], node.value[1])

    def render_cpi(self, node: GenericNode):
        value = node.value[0]
        self.cpi = value
        self.escp_commands.character_width(value)

    def render_page_length(self, node: GenericNode):
        print("Skipping page length directive")
        # TODO Implement this

    def render_justification(self, node: GenericNode):
        justification = next(j for j in escp.Justification if j.name.lower() == node.value[0])
        self.escp_commands.justify(justification)

    def render_symbol(self, node: GenericNode):
        symbol = node.value[0]
        match symbol:
            case 'euro':
                symbol = b'\xee'
                self.text(symbol)
            case '_':
                raise ValueError(f'Symbol {symbol} not supported')

    def render_typeface(self, node: GenericNode):
        typeface = node.value[0].to_lower()
        match typeface:
            case 'roman':
                self.escp_commands.typeface(escp.TypeFace.ROMAN)
            case 'sans-serif':
                self.escp_commands.typeface(escp.TypeFace.SANS_SERIF)
            case _:
                raise ValueError(f'Unknown typeface: {typeface}')
        self.escp_commands.typeface(typeface)

    def render_proportional(self, node: GenericNode):
        self.escp_commands.proportional(True)
        self.render_children(node)
        self.escp_commands.proportional(False)

    def render_double_width(self, node: GenericNode):
        self.escp_commands.double_character_width(True)
        self.render_children(node)
        self.escp_commands.double_character_width(False)

    def render_double_height(self, node: GenericNode):
        self.escp_commands.double_character_height(True)
        self.render_children(node)
        self.escp_commands.double_character_height(False)

    def render_newline(self, node: GenericNode):
        how_many = node.value
        if not self.soft_wrap and self.current_line_position_inch > 0:
            # how_many = 0 if how_many == 1 else how_many
            pass
        elif self.current_line_position_inch == 0 and self.soft_wrap:
            how_many -= 1

        if how_many > 0:
            self.cr_lf(how_many)

    def render_bold(self, node: GenericNode):
        self.escp_commands.bold(True)
        self.render_children(node)
        self.escp_commands.bold(False)

    def render_italic(self, node: GenericNode):
        self.escp_commands.italic(True)
        self.render_children(node)
        self.escp_commands.italic(False)

    def render_underline(self, node: GenericNode):
        self.escp_commands.underline(True)
        self.render_children(node)
        self.escp_commands.underline(False)

    def output_text_in_box(self, thickness):
        if self.text_buffer:
            self.box_vert_line(thickness)
            text = self.center_text(self.text_buffer.rstrip('\n'), b'\xb3\xb3')
            self.magic_text(text)
            self.box_vert_line(thickness)
            self.cr_lf()
            self.text_buffer = ''

    def render_box(self, node: GenericNode):
        self.text_buffer = ''  # wrap not handled in box

        if self.current_line_position_inch > 0:
            self.cr_lf()

        thickness = int(node.value[2])
        self.box_horizontal_line('top', thickness)
        self.cr_lf()

        for child in node.children:
            match child.category:
                case 'text':
                    self.text_buffer += child.value
                case 'space':
                    self.text_buffer += child.value * ' '
                case 'newline':
                    self.output_text_in_box(thickness)
                    self.cr_lf()
                case _:
                    raise ValueError(f'node category not allowed in box: {child.category}')

        self.output_text_in_box(thickness)
        self.box_horizontal_line('bottom', thickness)

    def render_soft_wrap(self, node: GenericNode):
        self.soft_wrap = node.value

    def render_space(self, node: GenericNode):
        spaces = node.value * ' '
        inches = self.text_width_inches(spaces)
        if node.value == 1:
            # Regular space
            if self.current_line_position_inch + inches > self.printable_width_inches():
                # Omitted if at the end of a line and won't fit
                self.cr_lf()
            else:
                self.text(' ')
        else:
            # Several spaces. Always print but break line if needed
            i = node.value
            while i > 0:
                if self.current_line_position_inch + inches > self.printable_width_inches():
                    self.cr_lf()
                self.text(' ')
                i -= 1

    def render_text(self, node: GenericNode):
        words = node.value.split(' ')
        for idx, word in enumerate(words):
            try:
                word = self.transcode(word)
                inches = self.text_width_inches(word)
                if self.current_line_position_inch + inches > self.printable_width_inches():
                    self.cr_lf()
                self.magic_text(word)
            except UnicodeEncodeError as e:
                if word:
                    print(f'UnicodeEncodeError for word: [{word}]', file=sys.stderr)
                raise e

    def transcode(self, text: str) -> str:
        text = text.replace('\u2019', "'")  # french apostrophe
        return text

    def render_children(self, node: GenericNode):
        for child in node.children:
            self._render(child)

    def render(self, content: str) -> bytes:
        tokens = self.lexer(content)
        root = self.parse(tokens)
        self._render(root)
        return self.escp_commands.buffer

    def char_width_inches(self, _char: str | bytes) -> Decimal:
        return Decimal(1) / Decimal(self.cpi)

    def text_width_inches(self, text: str) -> Decimal:
        return sum([self.char_width_inches(c) for c in text])

    def printable_width_inches(self) -> Decimal:
        chars_per_line = self.page_width_inches * self.cpi
        return (
            Decimal(self.page_width_inches) -
            Decimal(chars_per_line - (self.margin_right - self.margin_left)) * Decimal('0.1')
        )

    def check_and_store_pragma(self, pragma) -> bool:
        if self.escp_commands.buffer != b'':
            raise ValueError('[pragma] must be the first line in the file')
        name = pragma[1:-1].split(':')[1]
        if name in self.directives_processed_once:
            raise ValueError(f'{pragma} already processed')
        self.directives_processed_once.append(name)
        return True

    def _on_off_as_bool(self, value) -> bool:
        return {'on': True, 'off': False}[value]

    def center_text(self, text: str, leave_space_for=None):
        # in inches
        text_width = self.text_width_inches(text)
        space_width = self.char_width_inches(' ')
        extra_space = 0 if leave_space_for is None else self.text_width_inches(leave_space_for)
        number_of_spaces = (self.printable_width_inches() - text_width - extra_space) / space_width
        left_spaces = int(number_of_spaces / 2)
        right_spaces = math.ceil(number_of_spaces - left_spaces)
        return ' ' * left_spaces + text + ' ' * right_spaces

    def box_horizontal_line(self, part: str, thickness=1) -> None:
        if part == 'top':
            self.escp_commands.text(b'\xda' if thickness == 1 else b'\xc9')
            self._box_horizontal_line(thickness)
            self.escp_commands.text(b'\xbf' if thickness == 1 else b'\xbb')
        elif part == 'bottom':
            self.escp_commands.text(b'\xc0' if thickness == 1 else b'\xc8')
            self._box_horizontal_line(thickness)
            self.escp_commands.text(b'\xd9' if thickness == 1 else b'\xbc')
        else:
            raise ValueError(f'Invalid box part: {part}')

    def _box_horizontal_line(self, thickness=1):
        c = b'\xc4' if thickness == 1 else b'\xcd'
        extra_inch = self.char_width_inches(str(b'\xda')) * 2  # arbitrary corner char
        remaining_inches = self.printable_width_inches() - extra_inch
        w = Decimal(0)
        while w < remaining_inches:
            self.escp_commands.text(c)
            w += self.char_width_inches(str(c))

    def box_vert_line(self, thickness=1) -> None:
        self.escp_commands.text(b'\xb3' if thickness == 1 else b'\xba')
