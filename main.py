import pygame
import globals as g
import random
from collections import Counter
import matplotlib.pyplot as plt

from fox import Fox
from rabbit import Rabbit
from water_src import WaterSource
from food_src import FoodSource
from vector2 import Vector2
from dna import DNA
from rock import Rock


def generate_fox():
    x = random.randint(0, g.screen_width)
    y = random.randint(0, g.screen_height)
    g.foxes.append(Fox(x, y))


def generate_food():
    while 1:
        x = random.randint(0, g.screen_width)
        y = random.randint(0, g.screen_height)
        valid = True

        for w in g.water_sources:
            if w.location.find_distance(Vector2(x, y)) <= w.radius:
                valid = False

        if valid:
            g.food.append(FoodSource(x, y))
            return


def draw_window(screen: pygame.surface):
    screen.fill(g.grass_green)
    for s in g.water_sources:
        s.draw(screen)
    for f in g.food:
        f.draw(screen)
    for r in g.rocks:
        r.draw(screen)
    for rab in g.rabbits:
        rab.draw(screen)
    for fox in g.foxes:
        fox.draw(screen)
    pygame.display.flip()


def main():
    # DNA: food_rock(30, 200), water_vision(50, 400), fox_vision(30, 70), speed(60, 130),
    # color(light, mid, dark)
    pygame.init()
    size = g.screen_width, g.screen_height
    screen = pygame.display.set_mode(size)
    # Add Water
    g.water_sources.append(WaterSource(550, 200, 100))
    g.water_sources.append(WaterSource(50, 600, 50))
    # Add Rabbits
    g.rabbits.append(Rabbit(200, 40, g.male, DNA(150, 350, 30, 80, g.light)))
    g.rabbits.append(Rabbit(400, 140, g.female, DNA(100, 200, 60, 100, g.dark)))
    g.rabbits.append(Rabbit(600, 350, g.male, DNA(40, 400, 35, 75, g.dark)))
    g.rabbits.append(Rabbit(350, 600, g.female, DNA(200, 100, 30, 70, g.mid)))
    # Add Rocks
    g.rocks.append(Rock(200, 400, 20))
    g.rocks.append(Rock(70, 70, 30))
    g.rocks.append(Rock(600, 500, 50))
    g.rocks.append(Rock(400, 600, 15))
    g.rocks.append(Rock(150, 200, 30))
    for r in g.rabbits:
        g.genes.append(r.dna)
        if r.gender == g.male:
            g.num_males += 1
        else:
            g.num_females += 1

    g.population_over_time.append(len(g.rabbits))
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                for r in g.rabbits:
                    g.lifespans.append(r.life)
                pygame.quit()
                print_data()
                graph_data()
                exit(0)

        if g.pop_timer > 10000:
            for r in g.rabbits:
                r.life += 1
            g.population_over_time.append(len(g.rabbits))
            g.pop_timer = 0
        else:
            g.pop_timer += 1

        if len(g.rabbits) > len(g.max_population):
            g.max_population = g.rabbits.copy()

        if g.food_generator > 5000 and len(g.food) < 10:
            generate_food()
            g.food_generator = 0
        elif len(g.food) < 10:
            g.food_generator += 1

        if len(g.rabbits) == 0:
            print("No More Rabbits")
            pygame.quit()
            print_data()
            graph_data()
            exit(0)
        elif len(g.rabbits) > 400:
            print("Rabbits win")
            for r in g.rabbits:
                g.lifespans.append(r.life)
            pygame.quit()
            print_data()
            graph_data()
            exit(0)

        if g.fox_spawn_numbers[g.ind] == len(g.rabbits):
            generate_fox()
            g.ind += 1

        for rab in g.rabbits:
            rab.move()

        for fox in g.foxes:
            fox.move()

        draw_window(screen)


def separate_genes():
    fox = []
    water = []
    food_rock = []
    speed = []
    col = []
    for ge in g.genes:
        water.append(ge.water_vision)
        food_rock.append(ge.food_rock_vision)
        speed.append(ge.speed)
        fox.append(ge.fox_vision)
        col.append(ge.color)
    return {"fox": fox, "water": water, "food_rock": food_rock, "speed": speed, "color": col}


def print_data():
    max_pop_male = 0
    max_pop_female = 0
    for rab in g.max_population:
        if rab.gender == g.male:
            max_pop_male += 1
        else:
            max_pop_female += 1

    gen = separate_genes()
    color = Counter(gen["color"])

    # Print statistics
    print("_______________________________Scene Statistics_______________________________")
    print("Total Rabbit Births:", len(g.genes))
    print("Total Rabbit Deaths:", g.deaths)
    print("Maximum Rabbit Population:", len(g.max_population))
    print("Num Females At Max Population:", max_pop_female)
    print("Num Males At Max Population:", max_pop_male)
    print("Num Females Total:", g.num_females)
    print("Num Males Total:", g.num_males)
    print("Max Lifespan:", max(g.lifespans))
    print("Average Lifespan:", sum(g.lifespans) / len(g.lifespans))
    print("\n____Gene Statistics____")
    print("Average Water Vision Gene:", sum(gen["water"]) / len(gen["water"]))
    print("Max Water Vision:", max(gen["water"]))
    print("Average Fox Vision Gene:", sum(gen["fox"]) / len(gen["fox"]))
    print("Max Fox Vision:", max(gen["fox"]))
    print("Average Food/Rock Vision Gene:", sum(gen["food_rock"]) / len(gen["food_rock"]))
    print("Max Food/Rock Vision", max(gen["food_rock"]))
    print("Average Speed Gene:", sum(gen["speed"]) / len(gen["speed"]))
    print("Fastest speed (Lower values are best):", min(gen["speed"]))
    print("Percent Light Color:", color[g.light] / sum(color.values()))
    print("Percent Mid Color:", color[g.mid] / sum(color.values()))
    print("Percent Dark Color:", color[g.dark] / sum(color.values()))


def graph_data():
    # Set up lists and dictionaries for gene plots
    gen = separate_genes()
    water_gene = Counter(gen["water"])
    fox_gene = Counter(gen["fox"])
    speed_gene = Counter(gen["speed"])
    food_rock_gene = Counter(gen["food_rock"])
    color_gene = Counter(gen["color"])

    # Plot figure 1
    plt.figure(1)

    plt.subplot(211)
    plt.title("Population Over Time")
    plt.plot(g.population_over_time)

    plt.subplot(212)
    plt.title("Deaths By Category")
    categories = ['Hydration Deaths', 'Hunger Deaths', 'Fox Deaths']
    values = [g.thirst_deaths, g.hunger_deaths, g.fox_deaths]
    plt.bar(categories, values)

    # Plot Figure 2: Bar graphs of gene statistics
    plt.figure(2)

    plt.subplot(421)
    plt.title("Water Gene")
    plt.bar(water_gene.keys(), water_gene.values())

    plt.subplot(422)
    plt.title("Food/Rock Gene")
    plt.bar(food_rock_gene.keys(), food_rock_gene.values())

    plt.subplot(423)
    plt.title("Fox Gene")
    plt.bar(fox_gene.keys(), fox_gene.values())

    plt.subplot(424)
    plt.title("Speed Gene")
    plt.bar(speed_gene.keys(), speed_gene.values())

    plt.subplot(425)
    plt.title("Color Gene")
    plt.bar(color_gene.keys(), color_gene.values())

    # Plot Figure 3: Scatter plots of gene statistics over time
    plt.figure(3)

    plt.subplot(421)
    plt.title("Water")
    plt.plot(gen["water"])

    plt.subplot(422)
    plt.title("Food/Rock")
    plt.plot(gen["food_rock"])

    plt.subplot(423)
    plt.title("Fox")
    plt.plot(gen["fox"])

    plt.subplot(424)
    plt.title("Speed")
    plt.plot(gen["speed"])

    plt.subplot(425)
    plt.title("Color")
    plt.plot(gen["color"])

    # Plot Figure 4: Box and whiskers
    plt.figure(4)

    plt.subplot(221)
    plt.title("Life Spans")
    plt.boxplot(g.lifespans)

    plt.subplot(222)
    plt.title("Food/Rock Vision")
    plt.boxplot(gen["food_rock"])

    plt.subplot(223)
    plt.title("Water Vision")
    plt.boxplot(gen["water"])

    plt.subplot(224)
    plt.title("Fox Vision")
    plt.boxplot(gen["fox"])

    plt.show()


if __name__ == "__main__":
    main()
