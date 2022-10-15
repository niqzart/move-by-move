from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from os import system, name

UPPER = ord("A")
LOWER = ord("a")


def clear():
    system("cls" if name == "nt" else "clear")


@dataclass()
class Move:
    field_from: int
    field_to: int
    captured: list[int] = None

    def __post_init__(self):
        if self.captured is None:
            self.captured = []

    def __len__(self):
        return len(self.captured)


class Filler(str, Enum):
    value: str
    WHITE = "o"
    BLACK = "x"

    def __invert__(self):
        if self == self.WHITE:
            return self.BLACK
        elif self == self.BLACK:
            return self.WHITE
        raise NotImplementedError()


@dataclass()
class Space:
    filler: Filler | None = None

    def __str__(self) -> str:
        if self.is_empty():
            return " "
        return self.filler.value

    def is_empty(self) -> bool:
        return self.filler is None


class Board:
    def initial_filler(self, i: int) -> Filler | None:
        if i < self.factor * (self.factor - 1):
            return Filler.BLACK
        elif i >= self.factor * (self.factor + 1):
            return Filler.WHITE
        return None

    def __init__(self, factor: int = 4):
        self.factor: int = factor
        self.lines: int = self.factor * 2
        self.size: int = self.factor * self.lines
        self.data: list[Space] = [
            Space(self.initial_filler(i))
            for i in range(self.size)
        ]

    def __setitem__(self, key: int, value: Filler | None):
        self.data[key].filler = value

    def __getitem__(self, item: int) -> Space:
        return self.data[item]

    def _output(self):
        for i in range(self.lines, 0, -1):
            yield f"{i}|"
            if i % 2 == 0:
                yield " |"
            for j in range(self.factor):
                # index: int = self.data[(i - 1) * self.factor + j]
                index: int = (self.lines - i) * self.factor + j
                yield f"{self[index]}|"
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

    def _move(self, move: Move):
        if self[move.field_from].is_empty() is None:
            raise ValueError("Can't move an empty space")
        if not self[move.field_to].is_empty():
            raise ValueError("Can't go to a non-empty space")
        self[move.field_to] = self[move.field_from].filler
        self[move.field_from] = None

        for capture in move.captured:
            if self[capture] is None:
                raise ValueError("Can't capture an empty space")
            self[capture] = None

    def move(self, simple_move: str):
        if not isinstance(simple_move, str):
            raise ValueError("Simple move is not a string")
        if len(simple_move) != 4:
            raise ValueError("Simple move's length is not 4")

        field_from: int = self.coord_convert(simple_move[:2])
        field_to: int = self.coord_convert(simple_move[2:])

        self._move(Move(field_from, field_to))


if __name__ == "__main__":
    b = Board()
    while True:
        print(b.output())
        while True:
            try:
                b.move(input())
                break
            except ValueError as e:
                print(e)
