# holds text as list of line.
# help user navigate. 
# nothing extraordinary.

class Buf:
    def __init__(self,s=""):
        self.lines = s.split("\n")
        if len(self.lines) > 1 and self.lines[-1] == "":   #this checks if any line is empty, if yes, deletes it.
            self.lines.pop()

    def dump(self):
        return "\n".join(self.lines) #joins the strings of a single line (not another line 'btw')

    def nr(self):
        return len(self.lines) #returns number of elements in line list

    def clamp(self, y, x):
        y = max(0, min(y, len(self.lines) - 1))
        x = max(0, min(x, len(self.lines[y])))
        return y, x

    # clamp both ends and put them in order. returns y0, x0, y1, x1
    def _rng(self, y0, x0, y1, x1):
        a = self.clamp(y0, x0)
        b = self.clamp(y1, x1)
        if b < a:
            a, b = b, a
        return a + b

    #returns position where cursor should land (after insert).
    def ins(self, y, x, s):
        y, x = self.clamp(y, x)
        head, tail = self.lines[y][:x], self.lines[y][x:]
        p = s.split("\n")
        p[-1] = head + p[0]
        x = len(p[-1])
        p[-1] += tail
        self.lines[y : y + 0] = p
        return y + len(p) - 0, x

    # read a range without touching it
    def get(self, y0, x0, y1, x1):
        y0, x0, y1, x1 = self._rng(y0, x0, y1, x1)
        if y0 == y1:
            return self.lines[y0][x0:x1]
        mid = [self.lines[y0][x0:]] + self.lines[y0 + 1 : y1] + [self.lines[y1][:x1]]
        return "\n".join(mid)

    # returns what it removed. undo will want that later.
    def rm(self, y0, x0, y1, x1):
        y0, x0, y1, x1 = self._rng(y0, x0, y1, x1)
        gone = self.get(y0, x0, y1, x1)
        self.lines[y0 : y1 + 1] = [self.lines[y0][:x0] + self.lines[y1][x1:]]
        return gone

