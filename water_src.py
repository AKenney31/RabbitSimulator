import globals as g
import pygame
from vector2 import Vector2


class WaterSource:
    def __init__(self, x, y, rad):
        self.location = Vector2(x, y)
        self.radius = rad

    def draw(self, screen):
        pygame.draw.circle(screen, g.water_blue, self.location.return_tuple(), self.radius)
