import pandas as pd
import time
from haversine import haversine

# Initialize constantss
NORTH_POLE = (90, 0)
WEIGHT_LIMIT = 1000.0


def bb_sort(ll):
    """


    :param ll:
    :return:
    """

    ll = [[0, NORTH_POLE, 10]] + ll[:] + [[0, NORTH_POLE, 10]]
    for i in range(1, len(ll) - 2):
        lcopy = ll[:]
        lcopy[i], lcopy[i + 1] = ll[i + 1][:], ll[i][:]
        if path_opt_test(ll[1:-1]) > path_opt_test(lcopy[1:-1]):
            ll = lcopy[:]
    return ll[1:-1]


def path_opt_test(llo):
    f_ = 0.0
    d_ = 0.0
    l_ = NORTH_POLE
    for i in range(len(llo)):
        d_ += haversine(l_, llo[i][1])
        f_ += d_ * llo[i][2]
        l_ = llo[i][1]
    d_ += haversine(l_, NORTH_POLE)
    f_ += d_ * 10  # sleigh weight for whole trip
    return f_


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
    trip_id = 0
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
        trip_list.extend([trip_id] * len(g))

        # Adjusts id for next trip
        trip_id += 1

        # The amount of lines that were used may vary due to weight carried
        line_counter += len(g)

    # Inserts tripIds
    trips['TripId'] = pd.Series(trip_list, index=trips.index)

    print('took:', time.time() - time_a)
    print(line_counter)

    bm = 0.0
    x = []

    for s_ in range(0, trip_id):
        trip = trips[trips['TripId'] == s_]
        trip = trip.sort_values(['Latitude', 'Longitude'], ascending=[0, 1])

        a = []
        for x_ in range(len(trip.GiftId)):
            a.append([trip.iloc[x_, 0], (trip.iloc[x_, 1], trip.iloc[x_, 2]), trip.iloc[x_, 3]])
        b = bb_sort(a)
        if path_opt_test(a) <= path_opt_test(b):
            print("TripId", s_, "No Change", path_opt_test(a), path_opt_test(b))
            bm += path_opt_test(a)
            for y_ in range(len(a)):
                x.append((s_, a[y_][0]))
        else:
            print("TripId ", s_, "Optimized", path_opt_test(a) - path_opt_test(b))
            bm += path_opt_test(b)
            for y_ in range(len(b)):
                x.append((s_, b[y_][0]))

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
