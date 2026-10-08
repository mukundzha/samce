# keys.py - bytes in, key name out. no terminal stuff in kname(), so it's testable.
import os
import select
import sys

ESC = 0x1B

# multi-byte escape sequences. terminals disagree, so some keys have 2 forms.
SEQ = {
    b"\x1b[A": "up",    b"\x1bOA": "up",
    b"\x1b[B": "down",  b"\x1bOB": "down",
    b"\x1b[C": "right", b"\x1bOC": "right",
    b"\x1b[D": "left",  b"\x1bOD": "left",
    b"\x1b[H": "home",  b"\x1bOH": "home",  b"\x1b[1~": "home",
    b"\x1b[F": "end",   b"\x1bOF": "end",   b"\x1b[4~": "end",
    b"\x1b[2~": "insert",
    b"\x1b[3~": "delete",
    b"\x1b[5~": "pageup",
    b"\x1b[6~": "pagedown",
}

# single bytes that must win over the ctrl+x range (13 is ^M, 9 is ^I, ...)
ONE = {
    8: "backspace",
    9: "tab",
    10: "enter",
    13: "enter",
    27: "esc",
    127: "backspace",
}


def kname(d):
    if not d:
        return "unknown"
    if d in SEQ:
        return SEQ[d]

    if len(d) == 1:
        c = d[0]
        if c in ONE:
            return ONE[c]
        if 1 <= c <= 26:
            return "ctrl+" + chr(c + 96)
        if 32 <= c < 127:
            return chr(c)
        return "unknown"

    # esc + printable == alt+key
    if d[0] == ESC:
        if len(d) == 2 and 32 <= d[1] < 127:
            return "alt+" + chr(d[1])
        return "unknown"

    try:
        s = d.decode("utf-8")
    except UnicodeDecodeError:
        return "unknown"
    return s if len(s) == 1 else "unknown"


def _rdy(fd, t):
    return bool(select.select([fd], [], [], t)[0])


# first byte of a utf-8 char tells how long the char is
def _u8len(c):
    if c >= 0xF0:
        return 4
    if c >= 0xE0:
        return 3
    if c >= 0xC0:
        return 2
    return 1


def getkey(fd=None):
    if fd is None:
        fd = sys.stdin.fileno()

    # os.read, not sys.stdin.read: stdin has its own buffer and select()
    # can't see into it. learned that the hard way.
    d = os.read(fd, 1)
    if not d:
        raise EOFError("stdin closed")
    c = d[0]

    if c == ESC:
        # nothing after esc within 50ms? then it's a lone esc
        if not _rdy(fd, 0.05):
            return "esc"
        d += os.read(fd, 1)
        if d[1:2] in (b"[", b"O"):
            # read until the final byte (0x40..0x7e)
            while _rdy(fd, 0.05):
                n = os.read(fd, 1)
                d += n
                if 0x40 <= n[0] <= 0x7E:
                    break
        return kname(d)

    if c >= 0xC0:
        for _ in range(_u8len(c) - 1):
            d += os.read(fd, 1)

    return kname(d)


if __name__ == "__main__":
    from samce.term.raw import raw_mode

    with raw_mode():
        sys.stdout.write("press keys, ctrl+c quits\r\n")
        sys.stdout.flush()
        while 1:
            k = getkey()
            sys.stdout.write(k + "\r\n")
            sys.stdout.flush()
            if k == "ctrl+c":
                break
