# -*- coding: utf-8 -*-
"""
Created on Fri Sep 13 10:29:10 2024

@author: ss16144
"""
## define model parameters, doing it like this because I am unsure how to interact with the parameters when they are read directly in from a json file 
data = {
    "metadata": {
        "title": "A simple model using the river Thames",
        "description": "This model uses river Thames inflows. However it does not represent the Thames Water system or use any data from TWUL.",
        "minimum_version": "0.4"
    },
    "timestepper": {
        "start": "2100-01-01",
        "end": "2199-01-01",
        "timestep": 1
    },
    "scenarios": [
        {
            "name": "demand",
            "size": 1
        }
    ],
    "nodes": [
        {
            "name": "catchment1",
            "type": "catchment",
            "flow": "flow"
        },
        {
            "name": "river1",
            "type": "link"
        },
        {
            "name": "mrf1",
            "type": "rivergauge",
            "mrf": 0.6,
            "mrf_cost": -1000
        },
        {
            "name": "term1",
            "type": "output"
        },
        {
            "name": "reservoir1",
            "type": "storage",
            "max_volume": 200,
            "initial_volume": 200,
            "cost": -10
        },
        {
            "name": "abs1",
            "type": "link",
            "max_flow": 3.5
        },
        {
            "name": "demand1",
            "type": "output",
            "max_flow": "demand_max_flow",
            "cost": -500
        }
    ],
    "edges": [
        ["catchment1", "river1"],
        ["river1", "mrf1"],
        ["mrf1", "term1"],
        ["river1", "abs1"],
        ["abs1", "reservoir1"],
        ["reservoir1", "demand1"]
    ],
    "parameters": {
        "flow_factor": {
            "name": "flow_factor",
            "type": "constant",
            "value": 0.0864
        },
        "flow_cumecs": {
              "type": "dataframe",
              "url": "../data/inputs/thames_stochastic_flow.gz",
              "column": "flow",
              "index_col": "Date",
              "parse_dates": True
        },
        "flow": {
            "type": "aggregated",
            "agg_func": "product",
            "parameters": ["flow_cumecs", "flow_factor"]
        },
        "demand_baseline": {
            "type": "constant",
            "values": 1.7
        },
        "demand_profile": {
            "type": "monthlyprofile",
            "values": [0.9, 0.9, 0.9, 0.9, 1.2, 1.2, 1.2, 1.2, 0.9, 0.9, 0.9, 0.9]
        },
        "demand_max_flow": {
            "type": "aggregated",
            "agg_func": "product",
            "parameters": [
                "demand_baseline",
                "demand_profile",
                "demand_saving_factor",
                "demand_growth_factor"
            ]
        },
        "level1": {
            "type": "monthlyprofile",
            "values": [0.8, 0.85, 0.9, 0.92, 0.90, 0.85, 0.80, 0.70, 0.65, 0.7, 0.75, 0.8]
        },
        "level2": {
            "type": "monthlyprofile",
            "values": [0.5, 0.55, 0.6, 0.62, 0.60, 0.55, 0.50, 0.40, 0.35, 0.4, 0.45, 0.5]
        },
        "demand_saving_level" : {
            "type": "controlcurveindex",
            "storage_node": "reservoir1",
            "control_curves": [
                "level1",
                "level2"
            ]
        },
        "demand_saving_factor" : {
            "type": "indexedarray",
            "index_parameter": "demand_saving_level",
            "params": [
                "level0_factor",
                "level1_factor",
                "level2_factor"
            ]
        },
        "level0_factor": {
            "type": "constant",
            "values": 1.0
        },
        "level1_factor": {
            "type": "monthlyprofile",
            "values": [0.95, 0.95, 0.95, 0.95, 0.90, 0.90, 0.90, 0.90, 0.95, 0.95, 0.95, 0.95]
        },
        "level2_factor": {
            "type": "monthlyprofile",
            "values": [0.8, 0.8, 0.8, 0.8, 0.75, 0.75, 0.75, 0.75, 0.8, 0.8, 0.8, 0.8]
        },
        "demand_growth_factor": {
            "type": "constant",
            "values" : 1.0

        }
    }
}

import os
from pywr.model import Model
from pywr.recorders import TablesRecorder
import numpy as np
import click
import pandas
from Pywr import run
#import logging

#logger = logging.getLogger(__name__)
#logger.setLevel(logging.DEBUG)

mfr_cost = float(os.getenv("mfr_cost", 0.18))
res_cost = float(os.getenv("res_cost", 0.56))
demand_cost = float(os.getenv("demand_cost", 0.26))
mfr = float(os.getenv("mfr", 0.6))
demand_baseline = float(os.getenv("demand_baseline", 1.7))
restriction_scenario = int(float(os.getenv("restriction_scenario", 0)))
time_period = int(float(os.getenv("time_period", 0)))
ID = int(float(os.getenv("ID", 0)))


data['nodes'][2]['mrf_cost'] = ((1 - (res_cost + demand_cost )) * -5335)
data['nodes'][4]['cost'] = (res_cost *-16)
data['nodes'][6]['cost'] = (demand_cost  *- 1882)  
data['nodes'][2]['mrf'] = mfr
data['parameters']['demand_baseline']['values'] = demand_baseline
if restriction_scenario == 0:    
    data['parameters']['level1_factor']['values'] =  [0.95, 0.95, 0.95, 0.95, 0.90, 0.90, 0.90, 0.90, 0.95, 0.95, 0.95, 0.95]
    data['parameters']['level2_factor']['values'] =  [0.8, 0.8, 0.8, 0.8, 0.75, 0.75, 0.75, 0.75, 0.8, 0.8, 0.8, 0.8]
if restriction_scenario == 1:    
    data['parameters']['level1_factor']['values'] =  [0.8, 0.8, 0.8, 0.8, 0.75, 0.75, 0.75, 0.75, 0.8, 0.8, 0.8, 0.8]
    data['parameters']['level2_factor']['values'] =  [0.3, 0.3, 0.3, 0.3, 0.25, 0.25, 0.25, 0.25, 0.3, 0.3, 0.3, 0.3]
if restriction_scenario == 2:    
    data['parameters']['level1_factor']['values'] =  [1,1,1,1,1,1,1,1,1,1,1,1]
    data['parameters']['level2_factor']['values'] =  [0.95, 0.95, 0.95, 0.95, 0.90, 0.90, 0.90, 0.90, 0.95, 0.95, 0.95, 0.95]
if time_period == 0: 
    data['timestepper']['start'] = '2100-01-01'
    data['timestepper']['end'] = '2133-01-01'
elif time_period == 1:
    data['timestepper']['start'] = '2133-01-01'
    data['timestepper']['end'] = '2166-01-01'
elif time_period == 2: 
    data['timestepper']['start'] = '2166-01-01'
    data['timestepper']['end'] = '2199-01-01'

output = run(data) ### should i change this so that it outputs one metric? or calculate this from the h5 file? 
np.savetxt('/data/outputs/output_' + str(ID) + '.csv', output, delimiter = ',')
param = np.array([mfr_cost, res_cost, demand_cost, mfr, demand_baseline, restriction_scenario, time_period, ID])
np.savetxt('/data/outputs/params_' + str(ID) + '.csv', param, delimiter = ',')