# escp-wp

**A Python text-based word processor for the ESC/P printer language.**

## At a glance

This basic tool handles a homemade file format called `escp` and the conversion from markdown to `escp`.

`.md -> .escp.txt. -> .bin -> ESC/P printer`

This project leverages [python-escp](https://github.com/yackx/python-escp) to convert this `.escp.txt` file to a binary file that can be sent straight to an Epson ESC/P printer.

## Installation

```bash
$ python -m venv .venv
$ source .venv/bin/activate
(.venv) $ pip install -r requirements.txt
```

## Usage

To convert `.escp.txt -> .bin -> ESC/P printer`

```
$ cat samples/hello.escp.txt

[pragma:escp-wp][soft-wrap:on]
[box:on:thickness:1]Hello there[box:off]

Very short with[italic:on]italic text[italic:off]and[bold:on]even bold[bold:off].
```

```bash
(.venv) $ python -m wp.convert samples/hello.escp.txt -o samples/hello.escp.bin --pins 9
(.venv) $ lpr -o raw samples/hello.escp.bin
```

Or you can start for a markdown file

```
$ cat samples/hello.md

# Hello there

Very short with _italic text_ and **even bold**.
```

```bash
(.venv) $ python -m wp.convert samples/hello.md -o samples/hello.escp.bin --pins 9
(.venv) $ lpr -o raw samples/hello.escp.bin
```

> [!TIP]
> Make sure your Epson ESP/P printer is the default printer before you run the `lpr` command.
