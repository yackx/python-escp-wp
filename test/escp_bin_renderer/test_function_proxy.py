import wp


def test_proxy():
    assert wp.render_escp('Lorem ipsum', pins=9) == b'Lorem ipsum\r\n'
