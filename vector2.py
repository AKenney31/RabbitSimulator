import math


class Vector2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def add(self, vec):
        self.x += vec.x
        self.y += vec.y

    def find_unit_vector(self):
        mag = math.sqrt(math.pow(self.x, 2) + math.pow(self.y, 2))
        if mag != 0:
            self.x /= mag
            self.y /= mag

    def find_distance(self, vec):
        return math.sqrt(math.pow(self.x - vec.x, 2) + math.pow(self.y - vec.y, 2))

    def find_dot_product(self, vec):
        return (self.x * vec.x) + (self.y * vec.y)

    def set_new_direction(self, destination, current_loc):
        self.x = destination.x - current_loc.x
        self.y = destination.y - current_loc.y

    def return_tuple(self):
        return self.x, self.y
