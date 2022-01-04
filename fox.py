import math
import random

import pygame

import globals as g

from vector2 import Vector2


class Fox:
    def __init__(self, x, y):
        self.location = Vector2(x, y)
        self.hunger = 100
        self.radius = 20
        self.direction = Vector2(0, 1)

        self.currently_eating_timer = 0
        self.move_timer = 0
        self.hunger_timer = 0

        self.currently_eating = False
        self.hunting = False
        self.rab = None
        self.checked_camo = False
        self.escaped_rabbits = []

    def draw(self, screen):
        pygame.draw.circle(screen, g.fox_orange, self.location.return_tuple(), self.radius)

    def hunt_rabbit(self):
        dist = self.location.find_distance(self.rab.location)
        if dist > 40:
            self.hunting = False
            self.rab = None
            self.checked_camo = False
            return False
        elif self.rab.hiding:
            self.hunting = False
            self.rab = None
            self.checked_camo = False
            return False
        elif self.rab.camouflaging and not self.checked_camo:
            r = random.random()
            r *= 100
            if self.rab.camouflaging:
                if self.rab.dna.color == g.light:
                    if r > 80:
                        print("escaped")
                        self.escaped_rabbits.append(self.rab)
                        self.hunting = False
                        self.rab = None
                        self.checked_camo = False
                        return False
                elif self.rab.dna.color == g.mid:
                    if r > 60:
                        print("escaped")
                        self.escaped_rabbits.append(self.rab)
                        self.hunting = False
                        self.rab = None
                        self.checked_camo = False
                        return False
                else:
                    if r > 40:
                        print("escaped")
                        self.escaped_rabbits.append(self.rab)
                        self.hunting = False
                        self.rab = None
                        self.checked_camo = False
                        return False
                self.checked_camo = True
        elif dist < self.rab.radius:
            g.fox_deaths += 1
            self.rab.be_eaten()
            self.eat()
            self.checked_camo = False
            return True
        else:
            self.direction.set_new_direction(self.rab.location, self.location)
            return True

    def check_for_rabbits(self):
        for r in g.rabbits:
            if not r.hiding and r not in self.escaped_rabbits:
                dist = self.location.find_distance(r.location)
                if dist < r.radius:
                    self.rab = r
                    self.rab.be_eaten()
                    self.eat()
                    return False

                if dist < 40:
                    vec = Vector2(r.location.x - self.location.x, r.location.y - self.location.y)
                    vec.find_unit_vector()
                    cos_ang = vec.find_dot_product(self.direction)
                    if -1 <= cos_ang <= 1:
                        ang = math.acos(cos_ang)
                        ang = math.degrees(ang)
                        if ang < 45:
                            self.rab = r
                            self.hunting = True
                            return True
        return False

    def set_direction(self):
        if self.currently_eating:
            self.eat()
            return

        if not self.hunting:
            if self.check_for_rabbits():
                if not self.currently_eating:
                    if self.hunt_rabbit():
                        return
        elif self.hunt_rabbit():
            return

        if not self.currently_eating:
            # The random number will determine whether the fox keeps moving in the same direction or changes course
            rand = random.randint(0, 500)
            if rand < 20:
                rand_x = random.randint(0, g.screen_width)
                rand_y = random.randint(0, g.screen_height)
                self.direction.x = rand_x
                self.direction.y = rand_y
                self.direction.set_new_direction(Vector2(rand_x, rand_y), self.location)

    def update_escaped_rabbits(self):
        for rab in self.escaped_rabbits:
            if not rab.camouflaging:
                self.escaped_rabbits.remove(rab)

    def die(self):
        g.foxes.remove(self)

    def eat(self):
        self.currently_eating = True
        self.hunger = 100
        self.hunger_timer = 0
        self.direction.x = 0
        self.direction.y = 0
        self.currently_eating_timer += 1
        if self.currently_eating_timer > 15:
            # Finish eating
            self.currently_eating_timer = 0
            self.currently_eating = False
            self.hunting = False
            self.rab.die()
            self.rab = None

    def move(self):
        if self.move_timer > 70:

            # Implement hunger
            if self.hunger_timer > 20:
                self.hunger -= 1
                self.hunger_timer = 0

            if self.hunger < 0:
                self.die()

            # Update the escaped rabbits
            self.update_escaped_rabbits()

            # Set new direction of travel
            self.set_direction()

            # Make direction a unit vector
            self.direction.find_unit_vector()

            # Increment location based on new direction
            self.location.add(self.direction)

            # Increment event timers
            self.hunger_timer += 1
            self.move_timer = 0
        else:
            self.move_timer += 1

