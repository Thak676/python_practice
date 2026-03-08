
from Circle import Circle

class XP(Circle):
    def __init__(self, x, y, value):
        super().__init__(x, y, 2, (0, 0, 255)) # Blue, small
        self.value = value
