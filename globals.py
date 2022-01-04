# Define Global Variables
import dna

screen_width = 700
screen_height = 700

male = "M"
female = "F"
light = "Light"
mid = "Mid"
dark = "Dark"
food_generator = 0

rabbits = []
water_sources = []
foxes = []
food = []
rocks = []

fox_spawn_numbers = [6, 15, 30, 60, 70, 100, 200, 9000000000]
ind = 0

pop_timer = 0
deaths = 0
thirst_deaths = 0
hunger_deaths = 0
fox_deaths = 0
num_males = 0
num_females = 0
max_population = []
population_over_time = []
genes = []
lifespans = []

r_light = (166, 111, 111)
r_mid = (105, 68, 68)
r_dark = (77, 50, 50)
grass_green = (27, 207, 84)
food_green = (7, 112, 40)
water_blue = (14, 90, 204)
fox_orange = (247, 144, 0)
rock_gray = (96, 88, 97)
