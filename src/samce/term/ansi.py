ESC = "\x1b"
CSI = ESC + "["

# styles
RESET = CSI + "0m"
BOLD = CSI + "1m"
DIM = CSI + "2m"
ITALIC = CSI + "3m"
UNDER = CSI + "4m"      
REV = CSI + "7m"

# screen
CLEAR = CSI + "2J"
CLREOL = CSI + "K"
HIDE = CSI + "?25l"
SHOW = CSI + "?25h"
ALT_ON = CSI + "?1049h"    # private screen, user's terminal comes back on exit
ALT_OFF = CSI + "?1049l"

# cursor shape
BLOCK = CSI + "2 q"
BAR = CSI + "6 q"

def goto(y, x):
    return f"{CSI}{y + 1};{x + 1}H"


# "#c4a7e7" -> (196, 167, 231)
def rgb(h):
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def fg(h):
    r, g, b = rgb(h)
    return f"{CSI}38;2;{r};{g};{b}m"


def bg(h):
    r, g, b = rgb(h)
    return f"{CSI}48;2;{r};{g};{b}m"
