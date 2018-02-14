from santa.src.minimizer import *
from santa.src.wrw import *
import pandas as pd

data = pd.read_csv('data/raw/train.csv')

#data = data[0:1000]

subset = data[['Latitude', 'Longitude']]
locations = [tuple(x) for x in subset.values]

weight_list = data['Weight'].tolist()

output = simple_minimizer(locations, weight_list)

output = pd.DataFrame(output)
output.to_csv('output.csv', index=False)
