import escp

import argparse
import sys


def main(file, *, vendor_id: int, product_id: int, init: bool, pins: int):
    printer = escp.UsbPrinter(id_vendor=vendor_id, id_product=product_id)

    if init:
        commands = escp.lookup_by_pins(pins)
        commands.init()
        printer.send(commands.buffer)

    printer.send(file.read())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Print an ESCP binary file')
    parser.add_argument('file', type=argparse.FileType('rb'), help='Binary file to print')
    parser.add_argument(
        '--init', action='store_true', required=False, default=False, help='Send init sequence before printing'
    )
    parser.add_argument('--connector', type=str, required=True, choices=['usb'], help='Connector type')
    parser.add_argument('--vendor-id', type=str, required=True, help='USB Vendor ID (eg 0x04b8)')
    parser.add_argument('--product-id', type=str, required=True, help='USB Product ID (eg 0x0005)')
    parser.add_argument(
        '--pins', type=int, default=9, choices=[9, 24, 48], required=False,
        help='Number of printer pins. Required if extra commands are to be sent to the printer.'
    )

    args = parser.parse_args()

    if not args.pins:
        if args.init:
            parser.error('Number of pins is required if init sequence is to be sent')
            exit(1)
    try:
        main(
            args.file,
            vendor_id=int(args.vendor_id, 16), product_id=int(args.product_id, 16),
            pins=args.pins, init=args.init
        )
    except escp.PrinterNotFound as e:
        print(f'Printer not found: {e}', file=sys.stderr)
        exit(1)
    except ValueError as e:
        print('Invalid vendor/product ID', file=sys.stderr)
        exit(1)
