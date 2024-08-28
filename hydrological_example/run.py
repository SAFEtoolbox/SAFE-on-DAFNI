# -*- coding: utf-8 -*-
"""
Created on Fri May 17 09:58:34 2024

@author: ss16144
"""

import os
import numpy as np
from HyMod import hymod_sim


Sm = float(os.getenv("Sm", 200))
beta = float(os.getenv("beta", 0.5))
alfa = float(os.getenv("alfa", 0.7))
Rs = float(os.getenv("Rs", 0.05))
Rf = float(os.getenv("Rf", 0.6))


data = np.genfromtxt('/data/inputs/LeafCatch.txt', comments='%')

rain = data[0:365,0]
evap = data[0:365,1]
flow = data[0:365,2]
warmup = 30

param = np.array([Sm, beta, alfa, Rs, Rf]) # Sm (mm), beta (-), alfa (-), Rs (-), Rf (-)
flow_sim, _, _ = hymod_sim(param, rain, evap)

np.savetxt('/data/outputs/flow_sim.csv', flow_sim, delimiter = ',')
np.savetxt('/data/outputs/params.csv', param, delimiter = ',')