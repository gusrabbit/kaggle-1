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

    pd_locations = pd.Series(locations)
    locations_uncovered = pd.Series(locations).notnull()

    distance_from_sp = distance_from_starting_point(pd_locations)
    min_pos = distance_from_sp[locations_uncovered].idxmin()

    while locations_uncovered.any():
        print('calculating trip..')
        used_points, min_pos = create_trip(min_pos, weight_list, pd_locations[locations_uncovered])
        for gift_id in used_points:
            output_list.append((gift_id, trip_id))

        locations_uncovered[used_points] = False
        trip_id += 1
        print('quantity of presents calculated', len(output_list))

    return output_list


def create_trip(starting_point, weight_list, locations):
    weight = weight_list[starting_point]
    used_points = [starting_point]
    sp = starting_point

    while True:
        df = get_distances(locations[sp], locations)
        if df[~df.index.isin(used_points)].any():
            sp = df[~df.index.isin(used_points)].idxmin()
        else:
            return used_points, sp
        test_weight = weight + weight_list[sp]
        if test_weight <= 1000:
            used_points.append(sp)
            weight = test_weight
            print('used point', sp, weight)
        else:
            return used_points, sp


def get_distances(starting_point, pd_locations):
    locations = pd_locations.values
    distance = []
    for location in locations:
        distance.append(haversine(starting_point, location))

    return pd.Series(distance, index=pd_locations.index)
