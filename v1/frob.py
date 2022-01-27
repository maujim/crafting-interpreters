from typing import Protocol
from abc import abstractmethod


class Frobbable(Protocol):
    @abstractmethod
    def frob(self) -> None:
        raise NotImplementedError
    @abstractmethod
    def bob(self) -> None:
        raise NotImplementedError


def main(knob: Frobbable) -> None:
    knob.frob()


class BrokenKnob:
    def frob(self) -> None:
        raise NotImplementedError


main(BrokenKnob())
