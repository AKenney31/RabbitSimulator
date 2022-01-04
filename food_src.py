import globals as g
import pygame
from vector2 import Vector2


class FoodSource:
    def __init__(self, x, y):
        self.location = Vector2(x, y)
        self.radius = 15
        self.meals = 0

    def draw(self, screen):
        pygame.draw.circle(screen, g.food_green, self.location.return_tuple(), self.radius)

    def eat(self):
        self.meals += 1
        if self.meals > 1 and self in g.food:
            g.food.remove(self)
