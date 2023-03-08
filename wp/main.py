import marko

from wp.marko_md_renderer_9_pins import MarkoEscpRenderer


def main():
    # md_to_escp = EscpRenderer()
    markdown = marko.Markdown(renderer=MarkoEscpRenderer)
    rendered = markdown('Hello, world!')
    # cmds = md_to_escp.render('Hello, world!')
    print(rendered)


if __name__ == '__main__':
    main()
