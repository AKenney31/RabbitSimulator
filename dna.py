from dataclasses import dataclass, field


@dataclass(frozen=True)
class DNA:
    food_rock_vision: int       # Distance from food and rocks that the rabbit can see it from
    water_vision: int           # Distance from water that the rabbit can see it from
    fox_vision: int             # Distance from fox that the rabbit can see it from
    speed: int                  # Amount of frames until the rabbit moves. Higher = slower. 100 max
    color: str                  # Color determines how well the rabbit can camouflage
