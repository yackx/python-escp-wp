import abc


class Renderer(abc.ABC):
    @abc.abstractmethod
    def render(self, content: str) -> bytes | str:
        pass
