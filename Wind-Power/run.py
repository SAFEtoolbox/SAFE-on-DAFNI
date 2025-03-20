import pandas as pd
import numpy as np
import os
from simple_wind_power import *



power_curves = pd.read_csv('/data/inputs/offshore_normalised_pc.csv')


wind_height = int(float(os.getenv("wind_height", 0)))
year = int(float(os.getenv("year", 1940)))
timestep = int(float(os.getenv("timestep", 0)))
pc = int(float(os.getenv("pc", 0)))
alpha = float(os.getenv("alpha", 0.14))
hubheight = float(os.getenv("hubheight", 100))
ID = int(float(os.getenv("ID", 0)))

X = np.asarray([wind_height, year, timestep, pc, alpha, hubheight, ID ]) 

print('intput parameters:', X)

outputs = wind_power_model_run(X, power_curves)
param = np.array([wind_height, year, timestep, pc, alpha, hubheight, ID]) 

np.savetxt('/data/outputs/params_' + str(ID) + '.csv', param, delimiter = ',')
np.savetxt('/data/outputs/output_' + str(ID) + '.csv', outputs, delimiter = ',')
