from __future__ import annotations

from collections.abc import Iterator
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
    promotes: bool
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
class Piece:
    filler: Filler
    king: bool = False

    def going_up(self):
        return self.filler == Filler.WHITE

    def promote(self):
        self.king = True

    def __str__(self) -> str:
        result = self.filler.value
        if self.king:
            return result.upper()
        return result


class Direction(Enum):
    value: int
    NORTH = 0
    EAST = 1
    SOUTH = 3
    WEST = 2

    def is_up(self):
        return self.value & 2 == 0


@dataclass()
class Space:
    piece: Piece | None = None
    directions: dict[Direction, int] = None

    def __post_init__(self):
        if self.directions is None:
            self.directions = {}

    def __eq__(self, other) -> bool:
        if isinstance(other, Filler):
            return self.piece.filler == other
        return super().__eq__(other)

    def __ne__(self, other) -> bool:
        if isinstance(other, Filler):
            return self.piece.filler != other
        return super().__ne__(other)

    def __str__(self) -> str:
        if self.is_empty():
            return " "
        return str(self.piece)

    def __getitem__(self, item: Direction) -> int | None:
        return self.directions.get(item)

    def __iter__(self) -> Iterator[tuple[Direction, int]]:
        for direction, index in self.directions.items():
            if index is not None:
                yield direction, index

    def is_empty(self) -> bool:
        return self.piece is None


class Board:
    def initial_filler(self, i: int) -> Piece | None:
        if i < self.factor * (self.factor - 1):
            return Piece(Filler.BLACK)
        elif i >= self.factor * (self.factor + 1):
            return Piece(Filler.WHITE)
        return None

    def start_space(self, i: int) -> Space:
        filler: Piece = self.initial_filler(i)

        current_line: int = i // self.factor
        line_bonus: int = current_line % 2
        current_column: int = i % self.factor + (1 - line_bonus)
        i -= line_bonus

        directions: dict[Direction, int] = {}
        if current_line != 0:
            top: int = i - self.factor
            if current_column != 0:
                directions[Direction.NORTH] = top
            if current_column != self.factor:
                directions[Direction.EAST] = top + 1
        if current_line != self.lines - 1:
            bottom: int = i + self.factor
            if current_column != 0:
                directions[Direction.WEST] = bottom
            if current_column != self.factor:
                directions[Direction.SOUTH] = bottom + 1

        return Space(filler, directions)

    def __init__(self, factor: int = 4):
        self.factor: int = factor
        self.lines: int = self.factor * 2
        self.size: int = self.factor * self.lines
        self.data: list[Space] = [
            self.start_space(i)
            for i in range(self.size)
        ]

    def __setitem__(self, key: int, value: Piece | None):
        self.data[key].piece = value

    def __getitem__(self, item: int) -> Space:
        return self.data[item]

    def _output(self, specials: dict[int, str]):
        for i in range(self.lines, 0, -1):
            yield f"{i}|"
            if i % 2 == 0:
                yield " |"
            for j in range(self.factor):
                # index: int = self.data[(i - 1) * self.factor + j]
                index: int = (self.lines - i) * self.factor + j
                space = specials.get(index) or self[index]
                yield f"{space}|"
                if j != self.factor - 1:
                    yield " |"
            if i % 2 == 1:
                yield " |"
            yield "\n"
        yield " |A|B|C|D|E|F|G|H|"

    def output(self, specials: dict[int, str] = None):
        clear()
        return "".join(self._output(specials or {}))

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

    def need_promotion(self, position: int, piece: Piece = None):
        if piece is None:
            piece = self[position]
        return position // self.factor == (0 if piece.going_up() else self.factor - 1)

    def _move(self, move: Move):
        if self[move.field_from].is_empty() is None:
            raise ValueError("Can't move an empty space")
        if not self[move.field_to].is_empty():
            raise ValueError("Can't go to a non-empty space")
        self[move.field_to] = self[move.field_from].piece
        self[move.field_from] = None

        for capture in move.captured:
            if self[capture] is None:
                raise ValueError("Can't capture an empty space")
            self[capture] = None

        if move.promotes:
            self[move.field_from].piece.promote()

    def move(self, simple_move: str):
        if not isinstance(simple_move, str):
            raise ValueError("Simple move is not a string")
        if len(simple_move) != 4:
            raise ValueError("Simple move's length is not 4")

        field_from: int = self.coord_convert(simple_move[:2])
        field_to: int = self.coord_convert(simple_move[2:])

        self._move(Move(field_from, field_to, self.need_promotion(field_from)))

    def generate_captures(
        self,
        field_from: int,
        piece: Piece,
        current: int,
        promotes: bool = False,
        *captures: int,
    ) -> Iterator[Move]:
        if not piece.king and self.need_promotion(current, piece):
            promotes = True
            piece.promote()

        stopped: bool = True
        for direction, index in self[current]:
            if (
                index not in captures
                and (next_index := self[index][direction]) is not None
                and not self[index].is_empty()
                and self[index] != piece
                and self[next_index].is_empty()
            ):
                stopped = False
                yield from self.generate_captures(
                    field_from, piece, next_index, promotes, *captures, index
                )

        if stopped and field_from != current:
            yield Move(field_from, current, promotes, list(captures))

    def generate_moves(self, field_from: int) -> list[Move]:
        piece: Piece = self[field_from].piece
        if piece is None:
            return []

        result: list[Move] = list(self.generate_captures(field_from, piece, field_from))
        if len(result) == 0:
            return [
                Move(field_from, index, self.need_promotion(field_from, piece))
                for direction, index in self[field_from]
                if self[index].is_empty() and direction.is_up() == piece.going_up()
            ]

        # remove short moves
        # max_captured = max(result, key=len)
        # return [move for move in result if len(move) == max_captured]

        return result


class TaskBoard(Board):
    def __init__(
        self,
        factor: int = 4,
        *,
        white_pieces: set[int] = None,
        black_pieces: set[int] = None,
        white_kings: set[int] = None,
        black_kings: set[int] = None,
    ):
        self.white_pieces: set[int] = white_pieces or set()
        self.black_pieces: set[int] = black_pieces or set()
        self.white_kings: set[int] = white_kings or set()
        self.black_kings: set[int] = black_kings or set()

        all_sets = (
            self.white_pieces,
            self.black_pieces,
            self.white_kings,
            self.black_kings,
        )
        if len(set.union(*all_sets)) != sum(map(len, all_sets)):
            raise ValueError("Collision: only one piece is allowed per cell")

        super().__init__(factor)

    def initial_filler(self, i: int) -> Piece | None:
        if i in self.black_pieces:
            return Piece(Filler.BLACK)
        if i in self.white_pieces:
            return Piece(Filler.WHITE)
        if i in self.black_kings:
            return Piece(Filler.BLACK, king=True)
        if i in self.white_kings:
            return Piece(Filler.WHITE, king=True)
        return None


if __name__ == "__main__":
    b = TaskBoard(white_pieces={0, 1, 2}, black_kings={23, 24})
    print(b.output())
    while True:
        while True:
            try:
                field_from = b.coord_convert(input())
                break
            except ValueError as e:
                print(e)

        print(field_from)
        moves = b.generate_moves(field_from)
        print(moves)
        tos = {move.field_to: move for move in moves}
        print(b.output(specials=dict.fromkeys(tos.keys(), ".")))

        while True:
            try:
                field_to = b.coord_convert(input())
                break
            except ValueError as e:
                print(e)
        if field_to not in tos:
            raise ValueError()

        print(field_from, field_to)
        b._move(tos[field_to])
        print(b.output())
