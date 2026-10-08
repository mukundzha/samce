#detects the position of cursor (x and y)

class Cur:
    #sets the standard
    def __init__(self,buf):
        self.b = buf
        self.y = 0
        self.x = 0
        self.want = 0

    def _len(self):
        return len(self.b.lines[self.y])
    
    def goto(self, y, x):
        self.y, self.x = self.b.clamp(y, x)
        self.want = self.x

    def left(self):
        if self.x > 0:
            self.x -= 1
        elif self.y > 0:
            self.y -= 1
            self.x = self._len()
        self.want = self.x

    def right(self):
        if self.x < self._len():
            self.x += 1
        elif self.y < self.b.nr() - 1:
            self.y += 1
            self.x = 0
        self.want = self.x

    def up(self):
        if self.y > 0:
            self.y -= 1
            self.x = min(self.want, self._len())

    def down(self):
        if self.y < self.b.nr() - 1:
            self.y += 1
            self.x = min(self.want, self._len())

    def home(self):
        self.x = 0
        self.want = 0

    def end(self):
        self.x = self._len()
        self.want = self.x
