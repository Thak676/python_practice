
from Circle import Circle

class Projectile(Circle):
    def __init__(self, x, y, r, color, velocity):
        super().__init__(x, y, r, color)
        self.velocity = velocity

    def update(self):
        self.x += self.velocity.x
        self.y += self.velocity.y
