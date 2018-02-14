from sklearn.decomposition import FactorAnalysis

POINT_A = (0, 0)
POINT_B = (90, 0)
POINT_C = (0, 90)
POINT_D = (0, -90)

from haversine import haversine
import pandas as pd


def make_fa(locations):
    list_of_lists = []
    for point in [POINT_A, POINT_B, POINT_C, POINT_D]:
        point_list = []
        for location in locations:
            point_list.append(haversine(point, location))
        list_of_lists.append(point_list)
    return pd.DataFrame(list_of_lists)


data = pd.read_csv('data/raw/train.csv')

subset = data[['Latitude', 'Longitude']]
locations = [tuple(x) for x in subset.values]

fa = FactorAnalysis(n_components=1)

df = make_fa(locations)
df = df.T

data['fa'] = fa.fit_transform(df)
data = data.sort_values(by=['fa'])

usable = data[['GiftId', 'Weight', 'fa']]

total_weight = 0
trip_id = 0

output = []
print(data)

for index, gift_id, weight, fa in usable.itertuples():
    print(gift_id, weight, fa)
    if total_weight + weight > 1000:
        trip_id += 1
        total_weight = weight
    else:
        total_weight += weight

    output.append((gift_id, trip_id))

output = pd.DataFrame(output, columns=['GiftId', 'TripId'])
ndf = pd.concat([data, output], axis=1)
grouper = ndf.groupby('TripId')['Weight'].sum()
print(grouper)
output.to_csv('output.csv', index=False)
