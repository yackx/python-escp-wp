import argparse
import os
import sys

from .escp_bin_renderer import EscpToBinRenderer
from .md_escp_converter import MarkdownEscpRenderer


def get_renderer(extension_from: str, extension_to: str, pins: int):
    match extension_from, extension_to:
        case '.md', '.txt':
            return MarkdownEscpRenderer()
        case '.txt', '.bin':
            return EscpToBinRenderer(pins)
        case _:
            raise ValueError(f'Invalid conversion: {extension_from} to {extension_to}')


def output(destination: str | None, payload: bytes | str):
    if destination is None:
        if isinstance(payload, bytes):
            print('Output is in binary format. Use -o to specify an output file.', file=sys.stderr)
            exit(1)
        else:
            print(payload)
    else:
        mode = 'wb' if isinstance(payload, bytes) else 'w'
        with open(destination, mode) as f:
            f.write(payload)


def main():
    pass


# $ python3 -m wp.convert
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Converts a document to escp-wp format or to a binary file')
    parser.add_argument('file', type=argparse.FileType('r', encoding='utf-8'), help='Source file')
    parser.add_argument(
        '--pins', type=int, default=9, choices=[9, 24, 48], required=True, help='Number of printer pins'
    )
    # TODO implement me
    parser.add_argument('--init', type=bool, required=False, default=False, help='Add init sequence at the beginning')
    # TODO implement me
    parser.add_argument('--ff', type=bool, required=False, default=False, help='Add form feed sequence at the end')
    parser.add_argument('-o', '--output', type=str, required=False, help='Output file (default: stdout)')
    args = parser.parse_args()

    _, input_file_extension = os.path.splitext(args.file.name)
    if input_file_extension not in ['.txt', '.md']:
        raise ValueError(f'Invalid file extension: {input_file_extension}')

    _, output_file_extension = os.path.splitext(args.output)
    if output_file_extension not in ['.txt', '.bin']:
        raise ValueError(f'Invalid file extension: {output_file_extension}')

    if input_file_extension == output_file_extension:
        raise ValueError(f'Input and output file extensions must be different: {input_file_extension}')

    renderer = get_renderer(input_file_extension, output_file_extension, args.pins)
    content = args.file.read()
    print(f'Converting {args.file.name} to {args.output} ({output_file_extension})')
    renderered = renderer.render(content)
    output(args.output, renderered)
