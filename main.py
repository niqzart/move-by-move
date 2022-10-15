from __future__ import annotations

from os import system, name

UPPER = ord("A")
LOWER = ord("a")


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

    def coord_convert(self, coord: str) -> int:
        if not isinstance(coord, str):
            raise ValueError("Coord is not a string")
        if len(coord) != 2:
            raise ValueError("Coord's length is not 2")

        # numerics are ok
        if coord.isdigit():
            result: int = int(coord) - 1
            if result < 0 or result > self.factor * self.lines:
                raise ValueError("Coord out of range")
            return result

        # converting strings
        place: int = ord(coord[0])
        if UPPER <= place < UPPER + self.lines:
            place -= UPPER
        elif LOWER <= place < LOWER + self.lines:
            place -= LOWER
        else:
            raise ValueError("Coord's first symbol out of range")

        if not coord[1].isdigit():
            raise ValueError("Coord's second symbol is not a number")
        # line: int = int(coord[1]) - 1
        line: int = self.lines - int(coord[1])  # counting from the top (black's side)
        if line % 2 == place % 2:
            raise ValueError("Coord can't be a white space")

        return line * self.factor + place // 2


if __name__ == "__main__":
    b = Board()
    print(b.output())
    while True:
        while True:
            try:
                print("Detected coord:", b.coord_convert(input()))
                break
            except ValueError as e:
                print(e)
