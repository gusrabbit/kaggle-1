import pandas as pd
from haversine import haversine

# Initialize constantss
NORTH_POLE = (90, 0)
WEIGHT_LIMIT = 1000.0


def bb_sort(ll):
    """


    :param ll:
    :return:
    """
    print('ll')
    print(ll)
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


def prepare_trip(limit_):
    trips = gifts[gifts['TripId'] == 0]
    trips = trips.sort_values(['i', 'j', 'Longitude', 'Latitude'])
    trips = trips[0:limit_]
    t_ = 0
    while len(trips.GiftId) > 0:
        g = []
        t_ += 1
        w_ = 0.0
        for i in range(len(trips.GiftId)):
            if (w_ + float(trips.iloc[i, 3])) <= WEIGHT_LIMIT:
                w_ += float(trips.iloc[i, 3])
                g.append(trips.iloc[i, 0])
        gifts.loc[gifts['GiftId'].isin(g), 'TripId'] = t_
        trips = gifts[gifts['TripId'] == 0]
        trips = trips.sort_values(['i', 'j', 'Longitude', 'Latitude'])
        trips = trips[0:limit_]

    ou_ = open("submission_opt" + str(limit_) + " " + str(n) + ".csv", "w")
    ou_.write("TripId,GiftId\n")
    bm = 0.0

    for s_ in range(1, t_ + 1):
        trip = gifts[gifts['TripId'] == s_]
        trip = trip.sort_values(['Latitude', 'Longitude'], ascending=[0, 1])

        a = []
        for x_ in range(len(trip.GiftId)):
            a.append([trip.iloc[x_, 0], (trip.iloc[x_, 1], trip.iloc[x_, 2]), trip.iloc[x_, 3]])
        b = bb_sort(a)
        if path_opt_test(a) <= path_opt_test(b):
            print("TripId", s_, "No Change", path_opt_test(a), path_opt_test(b))
            bm += path_opt_test(a)
            for y_ in range(len(a)):
                ou_.write(str(s_) + "," + str(a[y_][0]) + "\n")
        else:
            print("TripId ", s_, "Optimized", path_opt_test(a) - path_opt_test(b))
            bm += path_opt_test(b)
            for y_ in range(len(b)):
                ou_.write(str(s_) + "," + str(b[y_][0]) + "\n")
    ou_.close()
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
