from sklearn.decomposition import FactorAnalysis
from santa.src.minimizer import *
from santa.src.wrw import *
from haversine import haversine
import pandas as pd

# Points used for FactorAnalysis
POINT_A = (0, 0)
POINT_B = (90, 0)
POINT_C = (0, 90)
POINT_D = (0, -90)


def make_fa(locations):
    """
    Make Factor Analysis
    :param locations: Locations

    :return: npArray with FactorAnalysis
    :rtype: numpy Array
    """
    list_of_lists = []
    for point in [POINT_A, POINT_B, POINT_C, POINT_D]:
        point_list = []
        for location in locations:
            point_list.append(haversine(point, location))
        list_of_lists.append(point_list)

    df = pd.DataFrame(list_of_lists)
    df = df.T

    return FactorAnalysis(n_components=1).fit_transform(df)


def make_lat_lon_fa(locations):
    """
    Make Factor Analysis for Latitude and Longitude.

    :param locations: Locations

    :return: npArray with FactorAnalysis
    :rtype: numpy Array
    """
    df = pd.DataFrame(locations)
    # df = df.T

    return FactorAnalysis(n_components=1).fit_transform(df)


def categorize_lat_lon(locations):
    df = pd.DataFrame(locations, columns=['Lat', 'Lon']).round()
    truth_table = create_cat_truth_table()

    categorized_series = df.apply(categorize_df_lat_lon, axis=1, args=(truth_table,))
    return categorized_series


def categorize_df_lat_lon(df_line, truth_table):
    return truth_table[(truth_table['Lat'] == df_line['Lat']) & (truth_table['Lon'] == df_line['Lon'])]['Cat'].values[0]


def create_cat_truth_table():
    truth_table = []
    cat = 0
    for i in range(-90, 91):
        for j in range(-180, 181):
            truth_table.append((i, j, cat))
            cat += 1

    return pd.DataFrame(truth_table, columns=['Lat', 'Lon', 'Cat'])


def create_trip_output_from_ordered_df(data):
    usable = data[['GiftId', 'Weight', 'fa']]

    total_weight = 0
    trip_id = 0

    output = []

    for index, gift_id, weight, fa in usable.itertuples():
        if total_weight + weight > 1000:
            trip_id += 1
            total_weight = weight
        else:
            total_weight += weight

        output.append((gift_id, trip_id))
        pd.DataFrame(output, columns=['GiftId', 'TripId'])


def trip_optimizer_routine(df):
    trips_number = df['TripId'].max() + 1
    output = []

    for i in range(trips_number):
        temp_df = df[df['TripId'] == i]
        output.extend(trip_optimizer(temp_df))
    return pd.DataFrame(output, columns=['GiftId', 'TripId'])


data = pd.read_csv('data/raw/train.csv')
subset = data[['Latitude', 'Longitude']]
locations = [tuple(x) for x in subset.values]

data['fa'] = categorize_lat_lon(locations)
data = data.sort_values(by=['fa'])
data = data.reset_index(drop=True)

output = create_trip_output_from_ordered_df(data)
data = data.drop(columns=['GiftId'])

ndf = pd.concat([data, output], axis=1)

output = trip_optimizer_routine(ndf)
output.to_csv('output.csv', index=False)
