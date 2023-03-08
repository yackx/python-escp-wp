import escp


class EscpRenderer:

    def __init__(self, pins: int):
        self.escp_commands = escp.lookup_by_pins(pins)

    def render(self, *, md: str, page_width_inches=8.0, cpi=10) -> bytes:
        # with open("your_file.md", "r") as file:
        #     text = file.read()

        self.escp_commands.clear()
        current_line = ""
        current_width = 0
        words = md.split()
        tokens = list(zip(words, [" "] * len(words)))
        for token in tokens:
            token_width = sum(self._char_width(c, cpi) for c in token)
            if current_width + token_width > page_width_inches:
                self.escp_commands.text(current_line)
                self.escp_commands.cr_lf()
                current_line = ""
                current_width = 0
            if current_width != 0 or token != " ":  # skip leading space
                current_line += " " + token
                current_width += token_width
        self.escp_commands.text(current_line)
        self.escp_commands.cr_lf()

        return self.escp_commands.buffer

    def _char_width(self, _char: str, cpi: int) -> float:
        return 1 / cpi
