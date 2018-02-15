from haversine import haversine
import pandas as pd

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


def wrw_single_trip(weight, location_a, location_b):
    return weight * haversine(location_a, location_b)


def trip_optimizer(df):
    output = []
    location_a = STARTING_POINT
    truth_table = pd.Series(df['TripId']).notnull()
    while truth_table.any():
        max_wrw = 0
        temp_df = df[['GiftId', 'Weight', 'Latitude', 'Longitude']]
        print(temp_df)
        print(truth_table)
        temp_df = temp_df[truth_table]
        for index, gift_id, weight, latitude, longitude in temp_df.itertuples():
            location_b = (latitude, longitude)
            wrw = wrw_single_trip(weight, location_a, location_b)
            if wrw > max_wrw:
                max_wrw = wrw
                output_gift_id = gift_id

        output.append(output_gift_id)
        truth_table[output_gift_id] = False

    return output
