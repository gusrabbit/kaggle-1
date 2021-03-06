import pandas as pd
import time
from haversine import haversine
from santa.src.wrw import *

# Initialize constants
NORTH_POLE = (90, 0)
WEIGHT_LIMIT = 1000.0


def bb_sort(gifts_data, key):
    """

    :param gifts_data:
    :return:
    """

    # Initializes range length
    length = len(gifts_data) - key

    # Start optimization loop
    for i in range(length):
        # Creates a copy of gifts_data
        copied_gifts = gifts_data[:]  # [:] is used to copy the list

        # Switches order of elements on list
        copied_gifts[i], copied_gifts[i + key] = gifts_data[i + key], gifts_data[i]

        # Check which of the lists produce an optimal path
        if path_opt_test(gifts_data) > path_opt_test(copied_gifts):
            # Alters original set in case found a more efficient path
            gifts_data = copied_gifts[:]  # [:] is used to copy the list

    return gifts_data


def complex_sort(gifts_data):
    """

    :param gifts_data:
    :return:
    """

    # Initializes range length
    length = len(gifts_data) - 1

    # Start optimization loop
    for i in range(length):
        # Creates a copy of gifts_data
        copied_gifts_1 = gifts_data[:]  # [:] is used to copy the list

        # Creates a copy of gifts_data
        copied_gifts_2 = gifts_data[:]  # [:] is used to copy the list

        # Creates a copy of gifts_data
        copied_gifts_3 = gifts_data[:]  # [:] is used to copy the list

        original = path_opt_test(gifts_data)

        # Switches order of elements on list
        copied_gifts_1[i], copied_gifts_1[i + 1] = gifts_data[i + 1], gifts_data[i]
        copy_1 = path_opt_test(copied_gifts_1)

        # Switches order of elements on list
        if i < length - 1:
            copied_gifts_2[i], copied_gifts_2[i + 2] = gifts_data[i + 2], gifts_data[i]
            copy_2 = path_opt_test(copied_gifts_2)

            # Switches order of elements on list
            if i < length - 2:
                copied_gifts_3[i], copied_gifts_3[i + 3] = gifts_data[i + 3], gifts_data[i]
                copy_3 = path_opt_test(copied_gifts_3)
                minimum_value = min(original, copy_1, copy_2, copy_3)
            else:
                minimum_value = min(original, copy_1, copy_2)

        else:
            minimum_value = min(original, copy_1)

        # Check which of the lists produce an optimal path
        if original == minimum_value:
            pass
        elif copy_1 == minimum_value:
            gifts_data = copied_gifts_1[:]  # [:] is used to copy the list
        elif copy_2 == minimum_value:
            gifts_data = copied_gifts_2[:]  # [:] is used to copy the list
        elif copy_3 == minimum_value:
            gifts_data = copied_gifts_3[:]  # [:] is used to copy the list

    return gifts_data


def path_opt_test(llo):
    wrw = 0.0
    distance = 0.0
    location = NORTH_POLE
    for element in llo:
        distance += haversine(location, element[1])
        wrw += distance * element[2]
        location = element[1]
    distance += haversine(location, NORTH_POLE)
    wrw += distance * 10  # sleigh weight for whole trip
    return wrw


gifts = pd.read_csv("../data/raw/train.csv")
gifts['TripId'] = 0
gifts['i'] = 0
gifts['j'] = 0


def prepare_data(n):
    # Divide dataset in 4 ? why?
    i_ = 0
    for i in range(90, -90, int(-180 / n)):
        i_ += 1
        j_ = 0
        for j in range(180, -180, int(-360 / n)):
            gifts.loc[
                (gifts['Latitude'] > (i - 180 / n)) & (gifts['Latitude'] < i) & (gifts['Longitude'] > (j - 360 / n)) & (
                        gifts['Longitude'] < (j)), 'i'] = i_

            gifts.loc[
                (gifts['Latitude'] > (i - 180 / n)) & (gifts['Latitude'] < i) & (gifts['Longitude'] > (j - 360 / n)) & (
                        gifts['Longitude'] < (j)), 'j'] = j_


def prepare_trip(max_gifts_per_trip):
    """

    :param max_gifts_per_trip: Maximum amount of gifts per trip
    :return:
    """
    time_a = time.time()

    # Create trips DataFrame, which is a sorted Gifts DataFrame
    trips = gifts.sort_values(['i', 'j', 'Longitude', 'Latitude'])

    # Get length of DataFrame
    length = trips.shape[0]

    # Initialize Variables
    line_counter = 0
    max_trip = 0
    trip_list = []

    # Put gifts into DataFrame according to DataFrame order considering a max gifts per trip
    while line_counter < length:
        g = []
        weight = 0.0

        # Initializes temporary DataFrame that will be used to calculate weight
        df = trips[line_counter:line_counter + max_gifts_per_trip]

        # Loop to check if there weight is within limits
        for i in range(df.shape[0]):
            if weight + df.iloc[i, 3] <= WEIGHT_LIMIT:
                weight += float(df.iloc[i, 3])
                g.append(df.iloc[i, 0])
            else:
                break

        # Adjusts original
        trip_list.extend([max_trip] * len(g))

        # Adjusts id for next trip
        max_trip += 1

        # The amount of lines that were used may vary due to weight carried
        line_counter += len(g)

    # Inserts tripIds
    trips['TripId'] = pd.Series(trip_list, index=trips.index)

    print('took:', time.time() - time_a)
    print(line_counter)

    bm = 0.0
    x = []
    count = []

    for trip_id in range(0, max_trip):
        trip = trips[trips['TripId'] == trip_id]
        trip = trip.sort_values(['Latitude', 'Longitude'], ascending=[0, 1])

        a = []
        for index, gift_id, latitude, longitude, weight, *rest in trip.itertuples():
            a.append((gift_id, (latitude, longitude), weight))
        b = bb_sort(a, 1)
        c = bb_sort(a, 2)
        d = bb_sort(a, 3)
        e = trip_optimizer(trip, 1)
        f = trip_optimizer(trip, 2)
        g = trip_optimizer(trip, 3)
        h = trip_optimizer(trip, 4)
        i = complex_sort(a)

        path_a = path_opt_test(a)
        path_b = path_opt_test(b)
        path_c = path_opt_test(c)
        path_d = path_opt_test(d)
        path_e = path_opt_test(e)
        path_f = path_opt_test(f)
        path_g = path_opt_test(g)
        path_h = path_opt_test(h)
        path_i = path_opt_test(i)

        max_index = pd.Series([path_a, path_b, path_c, path_d, path_e, path_f, path_g, path_h, path_i]).idxmin()

        print(trip_id, max_index)
        count.append(max_index)

        if path_opt_test(a) <= path_opt_test(b):
            bm += path_opt_test(a)
            for y_ in range(len(a)):
                x.append((a[y_][0], trip_id))
        else:
            bm += path_opt_test(b)
            for y_ in range(len(b)):
                x.append((b[y_][0], trip_id))

    print(pd.Series(count).value_counts())
    print('took:', time.time() - time_a)

    output = pd.DataFrame(x, columns=['GiftId', 'TripId'])
    output.to_csv('output_shootout.csv', index=False)

    return bm


n = 1.11
limit_ = 70
prepare_data(n)
bm = prepare_trip(limit_)

benchmark = 12506999134.2
if bm < benchmark:
    print(n, limit_, "Improvement", bm, bm - benchmark, benchmark)
else:
    print(n, limit_, "Try again", bm, bm - benchmark, benchmark)
