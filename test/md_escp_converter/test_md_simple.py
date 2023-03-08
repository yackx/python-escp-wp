import pytest

from wp.md_escp_converter import MarkdownEscpRenderer


@pytest.fixture
def renderer():
    return MarkdownEscpRenderer()


def test_sample1(renderer):
    md = """# Station Eleven

**HBO** — _based on the novel by Emily St. John Mandel_

I remember damage. Then escape. Then adrift in a stranger's galaxy for a long time. But I’m safe now. I found it again. My home. My memories are the same as yours, they mean nothing. I feel this again for the first time. I have a job to do. I have found you nine times before, maybe ten. And I’ll find you again until the last time. I always do. I find you because I know you, and I know you because we are the same. You will know your endpoint when you reach it. In the early days before their home was broken, they hardly notice me. It was better to not be noticed. It is better to not be noticed. I do know you from somewhere, if you notice, then you know, then so then you’ll be loved. To be loved is a calamity for someone with your job. You have work to do. Work, love makes work impossible. Love will try to see the words before it’s finished. What is your job, love will ask it, and you will ask, what is my job? And there’s a you not to survive because survival is insufficient. No, the voices are confusing, and soon all I hear is, "I don’t wanna live the wrong life and then die." I remember damage, then escape. I’m at my best when I’m escaping. I have a job to do. I still have a job to do. I have found you nine times before, maybe ten, and I’ll find you again. I always do. There is no rescue mission. We are the same. We are safe."""

    expected_output = """[pragma:escp-wp][soft-wrap:on]
[box:on:thickness:2]Station Eleven[box:off]

[bold:on]HBO[bold:off] — [italic:on]based on the novel by Emily St. John Mandel[italic:off]

I remember damage. Then escape. Then adrift in a stranger's galaxy for a long time. But I’m safe now. I found it again. My home. My memories are the same as yours, they mean nothing. I feel this again for the first time. I have a job to do. I have found you nine times before, maybe ten. And I’ll find you again until the last time. I always do. I find you because I know you, and I know you because we are the same. You will know your endpoint when you reach it. In the early days before their home was broken, they hardly notice me. It was better to not be noticed. It is better to not be noticed. I do know you from somewhere, if you notice, then you know, then so then you’ll be loved. To be loved is a calamity for someone with your job. You have work to do. Work, love makes work impossible. Love will try to see the words before it’s finished. What is your job, love will ask it, and you will ask, what is my job? And there’s a you not to survive because survival is insufficient. No, the voices are confusing, and soon all I hear is, "I don’t wanna live the wrong life and then die." I remember damage, then escape. I’m at my best when I’m escaping. I have a job to do. I still have a job to do. I have found you nine times before, maybe ten, and I’ll find you again. I always do. There is no rescue mission. We are the same. We are safe."""

    assert renderer.render(md) == expected_output


def test_sample2(renderer):
    md = """# Hello there

Very short with _italic text_ and **even bold**."""

    expected_output = """[pragma:escp-wp][soft-wrap:on]
[box:on:thickness:2]Hello there[box:off]

Very short with [italic:on]italic text[italic:off] and [bold:on]even bold[bold:off]."""

    assert renderer.render(md) == expected_output
