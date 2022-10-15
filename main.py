from __future__ import annotations

from os import system, name


def clear():
    system("cls" if name == "nt" else "clear")


class Board:
    def output(self):
        clear()
        return "\n".join((
            "8| |x| |x| |x| |x|",
            "7|x| |x| |x| |x| |",
            "6| |x| |x| |x| |x|",
            "5| | | | | | | | |",
            "4| | | | | | | | |",
            "3|o| |o| |o| |o| |",
            "2| |o| |o| |o| |o|",
            "1|o| |o| |o| |o| |",
            " |A|B|C|D|E|F|G|H|",
        ))


if __name__ == "__main__":
    b = Board()
    print(b.output())
