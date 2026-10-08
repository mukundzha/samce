import sys
import termios
import tty
from contextlib import contextmanager

@contextmanager
def raw_mode():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        yield
    finally:
        termios.tssetattr(fd, termios.TCSADRAIN, old)

