import pytest

from wp.md_renderer import EscpRenderer


@pytest.fixture
def renderer():
    return EscpRenderer(9)


def test_word(renderer):
    assert renderer.render(md='word') == b'word\r\n'


def test_words(renderer):
    assert (
            renderer.render(md='Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor')
            ==
            b'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor\r\n'
    )


def test_trigger_newline(renderer):
    md = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor ' \
        'incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam'
    expected = b'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor\r\n' \
        b'incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam\r\n'
    assert renderer.render(md=md) == expected
