from __future__ import annotations

from os import system, name


def clear():
    system("cls" if name == "nt" else "clear")


class Board:
    def initial_filler(self, i: int) -> str:
        if i < self.factor * (self.factor - 1):
            return "x"
        elif i >= self.factor * (self.factor + 1):
            return "o"
        return " "

    def __init__(self, factor: int = 4):
        self.factor: int = factor
        self.lines: int = self.factor * 2
        self.size: int = self.factor * self.lines
        self.data: list[str] = [
            self.initial_filler(i)
            for i in range(self.size)
        ]

    def _output(self):
        for i in range(self.lines, 0, -1):
            yield f"{i}|"
            if i % 2 == 0:
                yield " |"
            for j in range(self.factor):
                # index: int = self.data[(i - 1) * self.factor + j]
                index: int = (self.lines - i) * self.factor + j
                yield f"{self.data[index]}|"
                if j != self.factor - 1:
                    yield " |"
            if i % 2 == 1:
                yield " |"
            yield "\n"
        yield " |A|B|C|D|E|F|G|H|"

    def output(self):
        clear()
        return "".join(self._output())


if __name__ == "__main__":
    b = Board()
    print(b.output())
