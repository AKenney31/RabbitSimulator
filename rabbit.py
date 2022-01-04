import pygame
import math
import random
import globals as g
from vector2 import Vector2
from dna import DNA


class Rabbit:
    def __init__(self, x, y, gender, dna: DNA):
        self.location = Vector2(x, y)
        self.direction = Vector2(x, y)
        self.known_water = []

        self.gender = gender
        self.dna = dna
        self.hydration = 100
        self.hunger = 100
        self.radius = 10 if gender == g.female else 13
        self.life = 0

        # Event Timers
        self.last_mated = 0
        self.move_timer = 51
        self.hunger_timer = 0
        self.thirst_timer = 0
        self.currently_drinking_timer = 0
        self.currently_eating_timer = 0
        self.quadrant_timer = 0
        self.currently_mating_timer = 0

        # Event Trackers
        self.hiding = False
        self.camouflaging = False
        self.thirsty = False
        self.hungry = False
        self.currently_drinking = False
        self.currently_eating = False
        self.currently_mating = False
        self.being_eaten = False
        self.food = None
        self.lover = None
        self.rock = None

    def draw(self, screen):
        if not self.hiding:
            if self.dna.color == g.light:
                pygame.draw.circle(screen, g.r_light, self.location.return_tuple(), self.radius)
            elif self.dna.color == g.mid:
                pygame.draw.circle(screen, g.r_mid, self.location.return_tuple(), self.radius)
            else:
                pygame.draw.circle(screen, g.r_dark, self.location.return_tuple(), self.radius)

    # Outline: Main Movement Driver Methods, Go To Methods, Check For Methods, Event Methods, Quadrant Methods
    # Main Movement Driver Methods
    def move(self):
        if self.move_timer > self.dna.speed:
            # If the rabbit has not found all the water sources, search for water in its line of sight
            if len(self.known_water) < len(g.water_sources):
                self.check_for_water()

            # Decrement the rabbit's hydration
            if self.thirst_timer > 15:
                self.hydration -= 1
                self.thirst_timer = 0

            # Decrement the rabbit's hunger
            if self.hunger_timer > 20:
                self.hunger -= 1
                self.hunger_timer = 0

            # Rabbit dies if it's hunger or hydration runs out
            if self.hydration < 0:
                g.thirst_deaths += 1
                self.die()
            elif self.hunger < 0:
                g.hunger_deaths += 1
                self.die()

            # Set the rabbit's thirst to true if rabbit's hydration is below 25%
            if self.hydration < 25:
                self.thirsty = True

            # Set the rabbit's hunger to true if the rabbit's hunger is below 25%
            if self.hunger < 25:
                self.hungry = True

            # Increment all the rabbit's event timer
            self.thirst_timer += 1
            self.hunger_timer += 1
            self.move_timer = 0
            self.last_mated += 1

            # Find the new direction of the rabbit
            self.set_direction()

            # Make the new direction a unit vector
            self.direction.find_unit_vector()

            # Increment the rabbit's location
            if not self.hiding and not self.camouflaging:
                self.location.add(self.direction)
        else:
            self.move_timer += 1

    def set_direction(self):
        # if an event is happening, just call the function and return
        if self.being_eaten:
            return

        if self.currently_drinking:
            self.drink()
            return

        if self.currently_eating:
            self.eat()
            return

        if self.currently_mating:
            self.mate()
            return

        if self.thirsty:
            if self.go_to_nearest_known_water():
                return

        if self.hungry:
            if not self.food:
                if self.check_for_food() and not self.currently_eating:
                    self.go_to_food()
                    return
            else:
                self.go_to_food()
                return

        if self.check_for_foxes():
            if self.hiding or self.camouflaging:
                return

            if self.rock:
                self.go_to_rock()
                return
            elif self.check_for_rocks():
                self.go_to_rock()
                return
            else:
                self.camouflaging = True
                return

        else:
            if self.rock:
                self.rock.occupants -= 1
            self.rock = None
            self.hiding = False
            self.camouflaging = False

        if self.last_mated > 300:
            if not self.lover:
                if self.check_for_rabbits() and not self.currently_mating:
                    self.go_to_lover()
                    return
            else:
                self.go_to_lover()
                return

        # To make the rabbits a little smarter, If no events are occurring, they will look for food even if they are
        # not hungry. As long as their hunger is below 70%, they will eat nearby food.
        if self.hunger < 70:
            if not self.food:
                if self.check_for_food() and not self.currently_eating:
                    self.go_to_food()
                    return
            else:
                self.go_to_food()
                return

        # This is needed because check for food and check for rabbits can set the rabbit to be eating or mating and
        # still return to this function. We do not want to proceed if the rabbit is eating or mating. Since the
        # water is handled slightly different, it is not needed in this statement
        if self.currently_eating or self.currently_mating:
            return

        # If the rabbit has not yet found a new direction of movement, it will explore "randomly"
        # The random number will determine whether the rabbit stands still or moves in a random direction
        rand = random.randint(0, 500)
        if rand < 20:
            rand_x = random.randint(0, g.screen_width)
            rand_y = random.randint(0, g.screen_height)
            self.direction.set_new_direction(Vector2(rand_x, rand_y), self.location)

    # Go To Methods
    def go_to_nearest_known_water(self):
        if len(self.known_water) == 0:
            return False
        shortest_dist = [g.screen_width, None]
        for w in self.known_water:
            dist = self.location.find_distance(w.location) - w.radius
            if dist < shortest_dist[0]:
                shortest_dist[0] = dist
                shortest_dist[1] = w

        # If the rabbit is at the water, call the drinking method
        if shortest_dist[0] + shortest_dist[1].radius <= shortest_dist[1].radius:
            self.drink()
            return True

        self.direction.set_new_direction(shortest_dist[1].location, self.location)
        return True

    def go_to_rock(self):
        if self.hiding:
            return

        if self.rock.occupants < self.rock.capacity:
            self.rock = None
            return
        dist = self.location.find_distance(self.rock.location)
        # If the rabbit is at the food source, call the drinking method
        if dist <= self.rock.radius:
            self.hiding = True
            return

        self.direction.set_new_direction(self.rock.location, self.location)
        return

    def go_to_food(self):
        if self.food not in g.food:
            self.food = None
            return
        dist = self.location.find_distance(self.food.location)
        # If the rabbit is at the food source, call the drinking method
        if dist <= self.food.radius:
            self.eat()
            return

        self.direction.set_new_direction(self.food.location, self.location)
        return

    def go_to_lover(self):
        if self.lover.currently_mating:
            self.lover = None
            return
        elif self.lover.hiding:
            self.lover = None
            return

        dist = self.location.find_distance(self.lover.location)

        # If the rabbit is near his lover, call the mate method
        if dist <= self.lover.radius + 15:
            self.lover.lover = self
            self.lover.mate()
            self.mate()
            return

        self.direction.set_new_direction(self.lover.location, self.location)
        return

    # Check For Methods
    def check_for_water(self):
        for w in g.water_sources:
            if w not in self.known_water:
                dist = self.location.find_distance(w.location) - w.radius
                if dist < self.dna.water_vision:
                    vec = Vector2(w.location.x - self.location.x, w.location.y - self.location.y)
                    vec.find_unit_vector()
                    cos_ang = vec.find_dot_product(self.direction)
                    if -1 <= cos_ang <= 1:
                        ang = math.acos(cos_ang)
                        ang = math.degrees(ang)
                        if ang < 90:
                            print("water found")
                            self.known_water.append(w)

    def check_for_food(self):
        for f in g.food:
            dist = self.location.find_distance(f.location)

            if dist < f.radius:
                # If they're already on a food, then just eat it and skip the rest of the steps
                self.food = f
                self.eat()
                return False

            if dist < self.dna.food_rock_vision:
                vec = Vector2(f.location.x - self.location.x, f.location.y - self.location.y)
                vec.find_unit_vector()
                cos_ang = vec.find_dot_product(self.direction)
                if -1 <= cos_ang <= 1:
                    ang = math.acos(cos_ang)
                    ang = math.degrees(ang)
                    if ang < 90:
                        print("Food Found")
                        self.food = f
                        return True
        return False

    def check_for_rocks(self):
        for r in g.rocks:
            if r.occupants < r.capacity:
                dist = self.location.find_distance(r.location)
                if dist < r.radius:
                    # If they're already on a rock, then hide
                    r.occupants += 1
                    self.rock = r
                    self.hiding = True
                    return True

                if dist < self.dna.food_rock_vision:
                    vec = Vector2(r.location.x - self.location.x, r.location.y - self.location.y)
                    vec.find_unit_vector()
                    cos_ang = vec.find_dot_product(self.direction)
                    if -1 <= cos_ang <= 1:
                        ang = math.acos(cos_ang)
                        ang = math.degrees(ang)
                        if ang < 90:
                            print("Rock Found")
                            self.rock = r
                            return True
        return False

    def check_for_rabbits(self):
        for r in g.rabbits:
            if r != self and r.gender != self.gender and r.last_mated > 250 and not r.currently_mating and not r.hiding:
                dist = self.location.find_distance(r.location)

                if dist < r.radius:
                    # Lover found call mate and return
                    self.lover = r
                    self.lover.lover = self
                    self.lover.mate()
                    self.mate()
                    return False

                if dist < 100:
                    vec = Vector2(r.location.x - self.location.x, r.location.y - self.location.y)
                    vec.find_unit_vector()

                    cos_ang = vec.find_dot_product(self.direction)
                    if -1 <= cos_ang <= 1:
                        ang = math.acos(cos_ang)
                        ang = math.degrees(ang)
                        if ang < 90:
                            print("Lover Found")
                            self.lover = r
                            return True
        return False

    def check_for_foxes(self):
        for f in g.foxes:
            dist = self.location.find_distance(f.location)
            if dist < self.dna.fox_vision:
                return True
        return False

    # Event Methods
    def eat(self):
        # The rabbit will eat the source for the equivalent of 15 moves
        self.currently_eating = True
        self.direction.x = 0
        self.direction.y = 0
        self.currently_eating_timer += 1
        if self.currently_eating_timer > 15:
            # Finish eating
            self.food.eat()
            self.food = None
            self.currently_eating = False
            self.hungry = False
            self.hunger = 100

    def drink(self):
        # The rabbit will stand still at the edge of the water source for the equivalent of 15 moves
        self.currently_drinking = True
        self.direction.x = 0
        self.direction.y = 0
        self.currently_drinking_timer += 1
        if self.currently_drinking_timer > 15:
            # Finish drinking
            self.currently_drinking = False
            self.thirsty = False
            self.hydration = 100

    def mate(self):
        # The rabbit will stand still and mate for the equivalent of 15 moves
        self.currently_mating = True
        self.direction.x = 0
        self.direction.y = 0
        self.currently_mating_timer += 1
        if self.currently_mating_timer > 15:
            # Finish mating
            print("Finished Mating")
            lover_dna = self.lover.dna
            self.lover = None
            if self.gender == g.female:
                new_dna = generate_dna(self.dna, lover_dna)
                g.genes.append(new_dna)
                gen = random.randint(1, 2)
                if gen == 1:
                    g.num_males += 1
                else:
                    g.num_females += 1
                g.rabbits.append(Rabbit(self.location.x, self.location.y, g.male if gen == 1 else g.female, new_dna))
            self.currently_mating = False
            self.last_mated = 0
            self.currently_mating_timer = 0

    def be_eaten(self):
        self.being_eaten = True
        self.direction.x = 0
        self.direction.y = 0

    def die(self):
        g.deaths += 1
        if self in g.rabbits:
            g.lifespans.append(self.life)
            g.rabbits.remove(self)


# Generate new DNA for newly birthed rabbit
def generate_dna(dna1: DNA, dna2: DNA):
    # DNA: food_rock(30, 200), water_vision(50, 400), fox_vision(30, 70), speed(60, 130),
    # color(light, mid, dark)

    # fox
    r = random.random() * 100
    fox = dna1.fox_vision if 0 <= r <= 45 else dna2.fox_vision
    fox = random.randint(30, 70) if r >= 90 else fox

    # water
    r = random.random() * 100
    water = dna1.water_vision if 0 <= r <= 45 else dna2.water_vision
    water = random.randint(50, 400) if r >= 90 else water

    # food_rock
    r = random.random() * 100
    food_rock = dna1.food_rock_vision if 0 <= r <= 45 else dna2.food_rock_vision
    food_rock = random.randint(30, 200) if r >= 90 else food_rock

    # speed
    r = random.random() * 100
    speed = dna1.speed if 0 <= r <= 45 else dna2.speed
    speed = random.randint(60, 130) if r >= 90 else speed

    # color
    r = random.random() * 100
    col = dna1.color if 0 <= r <= 45 else dna2.color
    if r >= 90:
        c = random.randint(1, 3)
        if c == 1:
            col = g.light
        elif c == 2:
            col = g.mid
        else:
            col = g.dark

    return DNA(food_rock, water, fox, speed, col)
