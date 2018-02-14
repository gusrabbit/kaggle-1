from haversine import haversine
import pandas as pd

STARTING_POINT = (90, 0)


def distance_matrix(locations):
    distance_line = []
    distance_matrix = []
    for location_a in locations:
        for location_b in locations:
            distance_line.append(haversine(location_a, location_b))
        distance_matrix.append(distance_line)

    return pd.DataFrame(distance_matrix)


def distance_from_starting_point(locations):
    distance = []
    for location in locations:
        distance.append(haversine(STARTING_POINT, location))

    return pd.Series(distance)


def simple_minimizer(locations, weight_list):
    output_list = []
    trip_id = 0

    locations_uncovered = locations
    locations_uncovered[:] = True

    distance_from_sp = distance_from_starting_point(locations)
    min_pos = distance_from_sp[locations_uncovered].idxmin()

    while locations_uncovered.any():


        dt_mx = distance_matrix(locations)
        used_points = create_trip(min_pos, dt_mx, weight_list)
        for gift_id in used_points:
            output_list.append((gift_id, trip_id))

        locations_uncovered[used_points] = False
        trip_id += 1

    return output_list


def create_trip(starting_point, distance_matrix, weight_list):
    weight = weight_list[starting_point]
    used_points = [starting_point]

    while True:
        starting_point = distance_matrix[starting_point].idxmin()
        test_weight = weight + weight_list[starting_point]
        if test_weight <= 1000:
            used_points.append(starting_point)

    return used_points
