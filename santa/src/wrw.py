from haversine import haversine

# lyon = (45.7597, 4.8422)
# paris = (48.8567, 2.3508)
# haversine(lyon, paris)

STARTING_POINT = (90, 0)
SLEIGH_WEIGHT = 10


def wrw_calculator(weights, locations):
    point_a = STARTING_POINT
    wrw = 0

    for location in locations:
        wrw += (sum(weights) + SLEIGH_WEIGHT) * haversine(point_a, location)
        point_a = location

    wrw += SLEIGH_WEIGHT * haversine(point_a, STARTING_POINT)

    return wrw
