import marko
import escp
from marko.inline import RawText


class MarkoEscpRenderer(marko.Renderer):

    def __init__(self):
        super().__init__()
        self.escp_commands = escp.lookup_by_pins(9)

    def render_paragraph(self, element: marko.block.Paragraph) -> escp.Commands:
        children = self.render_children(element)
        if element._tight:  # type: ignore
            return children
        else:
            return self.escp_commands

    def render_raw_text(self, element: RawText) -> str:
        self.escp_commands.text(element.children)
        return 'fooraw'
