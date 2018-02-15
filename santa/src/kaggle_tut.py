from haversine import haversine
import pandas as pd

NORTH_POLE = (90, 0)
WEIGHT_LIMIT = 1000.0


def bb_sort(ll):
    print(ll)
    s_limit = 5000
    optimal = False
    ll = [[0, NORTH_POLE, 10]] + ll[:] + [[0, NORTH_POLE, 10]]
    while not optimal:
        optimal = True
        for i in range(1, len(ll) - 2):
            lcopy = ll[:]
            lcopy[i], lcopy[i + 1] = ll[i + 1][:], ll[i][:]
            if path_opt_test(ll[1:-1]) > path_opt_test(lcopy[1:-1]):
                # print("swap")
                ll = lcopy[:]
                optimal = False
                s_limit -= 1
                if s_limit < 0:
                    optimal = True
                    break
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


gifts = pd.read_csv("data/raw/train.csv")

gifts[['lat', 'lon']] = gifts[['Latitude', 'Longitude']].round()

trips = gifts.sort_values(by=['lat', 'lon'])
trips.reset_index(drop=True, inplace=True)
output = []
trip_id = 0
total_weight = 0.0

for index, gift_id, weight in trips[['GiftId', 'Weight']].itertuples():
    if total_weight + weight > 1000:
        trip_id += 1
        total_weight = weight
    else:
        total_weight += weight
    output.append((gift_id, trip_id))

output = pd.DataFrame(output, columns=['GiftId', 'TripId'])
trips = pd.concat([trips, output], axis=1)

trips_number = output['TripId'].max() + 1
bm = 0.0

for i in range(trips_number):

    a = trips[trips['TripId'] == i]
    b = bb_sort(a)
    if path_opt_test(a) <= path_opt_test(b):

        bm += path_opt_test(a)

    else:

        bm += path_opt_test(b)

print(bm)
