import pytest

from wp.escp_bin_renderer import EscpToBinRenderer


@pytest.fixture
def renderer():
    return EscpToBinRenderer(9)  # number of pin arbitrarily chosen


def test_pragma(renderer):
    assert renderer.render(content='[pragma:escp-wp]word') == b'word\r\n'


def test_double_pragma_illegal(renderer):
    with pytest.raises(ValueError):
        renderer.render(content='[pragma:escp-wp]Lorem[pragma:escp-wp]word')


def test_double_pragma_different_value_illegal(renderer):
    with pytest.raises(ValueError):
        renderer.render(content='[pragma:soft-wrap:on]Lorem[pragma:soft-wrap:off]word')


@pytest.mark.skip(reason='not implemented')
def test_invalid_pragma(renderer):
    with pytest.raises(ValueError):
        renderer.render(content='[pragma:foo]Lorem')


def test_missing_pragma(renderer):
    assert renderer.render(content='word') == b'word\r\n'


def test_words(renderer):
    content = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor'
    expect = b'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor\r\n'
    assert renderer.render(content=content) == expect


def test_long_text_triggers_newline(renderer):
    content = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor ' \
              'incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam'
    expected = b'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor \r\n' \
               b'incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam\r\n'
    assert renderer.render(content=content) == expected


def test_double_newline_in_soft_wrap(renderer):
    content = 'Lorem ipsum\n\ndolor sit amet\n\nconsectetur adipiscing elit'
    expected = b'Lorem ipsum\r\n\r\ndolor sit amet\r\n\r\nconsectetur adipiscing elit\r\n'
    assert renderer.render(content=content) == expected


def test_single_newline_in_soft_wrap(renderer):
    renderer.soft_wrap = True
    content = 'Lorem ipsum\ndolor sit amet\nconsectetur adipiscing elit'
    expected = b'Lorem ipsum\r\ndolor sit amet\r\nconsectetur adipiscing elit\r\n'
    assert renderer.render(content=content) == expected


def test_double_newline_in_hard_wrap(renderer):
    renderer.soft_wrap = False
    content = 'Lorem ipsum\n\ndolor sit amet\n\nconsectetur adipiscing elit'
    expected = b'Lorem ipsum\r\n\r\ndolor sit amet\r\n\r\nconsectetur adipiscing elit\r\n'
    assert renderer.render(content=content) == expected


def test_single_newline_in_hard_wrap(renderer):
    renderer.soft_wrap = False
    content = 'Lorem ipsum\ndolor sit amet\nconsectetur adipiscing elit'
    expected = b'Lorem ipsum\r\ndolor sit amet\r\nconsectetur adipiscing elit\r\n'
    assert renderer.render(content=content) == expected


def test_pragma_soft_wrap_on(renderer):
    renderer.soft_wrap = False
    content = '[pragma:soft-wrap:on]\nLorem ipsum dolor sit amet,\nconsectetur adipiscing elit'
    expected = b'Lorem ipsum dolor sit amet,\r\nconsectetur adipiscing elit\r\n'
    assert renderer.render(content=content) == expected


def test_pragma_soft_wrap_off(renderer):
    renderer.soft_wrap = True
    content = '[pragma:soft-wrap:on]\nLorem ipsum dolor sit amet,\nconsectetur adipiscing elit'
    expected = b'Lorem ipsum dolor sit amet,\r\nconsectetur adipiscing elit\r\n'
    assert renderer.render(content=content) == expected


def test_trailing_space(renderer):
    assert renderer.render(content='word ') == b'word \r\n'


def test_trailing_spaces(renderer):
    assert renderer.render(content='word  ') == b'word  \r\n'


def test_exactly_line_width(renderer):
    content = 80 * 'a'
    expected = b'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\r\n'
    assert len(expected) == 82
    assert renderer.render(content=content) == expected


def test_bold(renderer):
    content = '[bold:on]bold[bold:off]'
    expected = b'\x1bEbold\x1bF\r\n'
    assert renderer.render(content=content) == expected


def test_bold_with_space(renderer):
    content = ' [bold:on]bold[bold:off]'
    expected = b' \x1bEbold\x1bF\r\n'
    assert renderer.render(content=content) == expected


def test_underline(renderer):
    content = '[underline:on]underline[underline:off]'
    expected = b'\x1b-\x01underline\x1b-\x00\r\n'
    assert renderer.render(content=content) == expected


def test_underline_with_space(renderer):
    content = ' [underline:on]underline[underline:off]'
    expected = b' \x1b-\x01underline\x1b-\x00\r\n'
    assert renderer.render(content=content) == expected


def test_bold_and_underline(renderer):
    content = 'It is [bold:on][underline:on]bold and underline[underline:off][bold:off] then'
    expected = b'It is \x1bE\x1b-\x01bold and underline\x1b-\x00\x1bF then\r\n'
    assert renderer.render(content=content) == expected


def test_underline_and_bold(renderer):
    content = 'It is [underline:on][bold:on]bold and underline[bold:off][underline:off] then'
    expected = b'It is \x1b-\x01\x1bEbold and underline\x1bF\x1b-\x00 then\r\n'
    assert renderer.render(content=content) == expected


def test_line_spacing(renderer):
    content = '[line-spacing:45:216]Text'
    expected = b'\x1b3\x2dText\r\n'
    assert renderer.render(content=content) == expected


def test_proportional(renderer):
    content = '[proportional:on]proportional[proportional:off]'
    expected = b'\x1bp\x01proportional\x1bp\x00\r\n'
    assert renderer.render(content=content) == expected


def test_box_thickness_2(renderer):
    content = '[box:on:thickness:2]Hello[box:off]'
    expected = (
            # top left + h bar + top right + crlf
            b'\xc9' + b'\xcd' * 78 + b'\xbb' + b'\r\n' +
            # vert bar + space + text + space + vert bar + crlf
            b'\xba' + b' ' * 36 + b'Hello' + b' ' * 37 + b'\xba' + b'\r\n' +
            # bottom left + h bar + bottom right + crlf
            b'\xc8' + b'\xcd' * 78 + b'\xbc' + b'\r\n'
    )
    assert renderer.render(content=content) == expected


def test_box_colon(renderer):
    content = '[box:on:thickness:2]cp:10[box:off]'
    expected = (
            # top left + h bar + top right + crlf
            b'\xc9' + b'\xcd' * 78 + b'\xbb' + b'\r\n' +
            # vert bar + space + text + space + vert bar + crlf

            b'\xba' + b' ' * 36 + b'cp:10' + b' ' * 37 + b'\xba' + b'\r\n' +
            # bottom left + h bar + bottom right + crlf
            b'\xc8' + b'\xcd' * 78 + b'\xbc' + b'\r\n'
    )
    assert renderer.render(content=content) == expected


def test_margin_left(renderer):
    content = '[margin:left:5]Hello'
    expected = b'\x1bl\x05Hello\r\n'
    assert renderer.render(content=content) == expected


def test_margin_right(renderer):
    content = '[margin:right:75]Hello'
    expected = b'\x1bQ\x4bHello\r\n'
    assert renderer.render(content=content) == expected


@pytest.mark.skip('bug in 0.0.4')
def test_margin_bottom(renderer):
    content = '[margin:bottom:5]'
    expected = b'\x1bN\x05\r\n'
    assert renderer.render(content=content) == expected


def test_symbol_euro(renderer):
    content = '[symbol:euro]'
    expected = b'\xee\r\n'
    assert renderer.render(content=content) == expected


def test_symbol_euro_before_punctuation(renderer):
    content = '10 [symbol:euro].'
    expected = b'10 \xee.\r\n'
    assert renderer.render(content=content) == expected


def test_center_odd_length(renderer):
    content = '1'
    expected = ' ' * 39 + '1' + ' ' * 40
    assert renderer.center_text(content) == expected
    assert len(expected) == 80


def test_center_even_length(renderer):
    content = '12'
    expected = ' ' * 39 + '12' + ' ' * 39
    assert renderer.center_text(content) == expected
    assert len(expected) == 80


def test_init(renderer):
    content = '[init]'
    expected = b'\x1b@\r\n'
    assert renderer.render(content=content) == expected


def test_colon(renderer):
    content = 'cpi:10'
    expected = b'cpi:10\r\n'
    assert renderer.render(content=content) == expected