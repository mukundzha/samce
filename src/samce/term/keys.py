import os
import select
import sys

ESC = 0x1B

SEQUENCES ={
    b"\x1b[A": "up",
    b"\x1b[B": "down",
    b"\x1b[C": "right",
    b"\x1b[D": "left",
    b"\x1bOA": "up",
    b"\x1bOB": "down",
    b"\x1bOC": "right",
    b"\x1bOD": "left",
    b"\x1b[H": "home",
    b"\x1b[F": "end",
    b"\x1bOH": "home",
    b"\x1bOF": "end",
    b"\x1b[1~": "home",
    b"\x1b[4~": "end",
    b"\x1b[2~": "insert",
    b"\x1b[3~": "delete",
    b"\x1b[5~": "pageup",
    b"\x1b[6~": "pagedown",
}

SINGLE = {
    9: "tab",
    10: "enter",
    13: "enter",
    27: "esc",
    8: "backspace",
    127: "backspace",
}

def parse(data:bytes) -> str:
    if not data:
        return "unknown"

    if data in SEQUENCES:
        return SEQUENCE[data]

    if len(data) == 1:
        b = data[0]
        if b in SINGLE:
            return SINGLE[b]
        if 1 <= b <= 26:
            return "ctrl+" + chr(b+96)
        if 32<= b < 127:
            return chr(b)
        return "unknown"

    if data[0] == ESC:
        if len(data) == 2 and 32 <= data[1] < 127:
            return "alt+" + chr(data[1])
        return "unknown"

    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return "unknown"
    return text if len(text) == 1 else "unknown"

def _ready(fd: int, timeout: float) -> bool:
    return bool(select.select([fd], [], [], timeout)[0])


def _utf8_length(first: int) -> int:
    if first >= 0xF0:
        return 4
    if first >= 0xE0:
        return 3
    if first >= 0xC0:
        return 2
    return 1


def read_key(fd: int | None = None) -> str:
    if fd is None:
        fd = sys.stdin.fileno()

    first = os.read(fd, 1)
    if not first:
        raise EOFError("stdin closed")
    b = first[0]

    if b == ESC:
        if not _ready(fd, 0.05):
            return "esc"
        data = first + os.read(fd, 1)
        if data[1:2] in (b"[", b"O"):
            while _ready(fd, 0.05):
                nxt = os.read(fd, 1)
                data += nxt
                if 0x40 <= nxt[0] <= 0x7E:
                    break
        return parse(data)

    if b >= 0xC0:
        data = first
        for _ in range(_utf8_length(b) - 1):
            data += os.read(fd, 1)
        return parse(data)

    return parse(first)


if __name__ == "__main__":
    from samce.term.raw import raw_mode

    with raw_mode():
        sys.stdout.write("press keys, ctrl+c to quit\r\n")
        sys.stdout.flush()
        while True:
            key = read_key()
            sys.stdout.write(f"{key}\r\n")
            sys.stdout.flush()
            if key == "ctrl+c":
                break
