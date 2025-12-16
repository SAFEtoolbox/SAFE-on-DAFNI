# -*- coding: utf-8 -*-
"""
Created on Fri Sep 13 10:37:10 2024

@author: ss16144
"""

from pywr.model import Model
from pywr.recorders import TablesRecorder
import numpy as np
import click
import pandas

def run(data):
    # Run the model
    model = Model.load(data)
    #logger = logging.getLogger(__name__)
    #logger.setLevel(logging.DEBUG)
    # Add a storage recorder
    TablesRecorder(model, "thames_output.h5", parameters=[p for p in model.parameters])

    # Run the model
    stats = model.run()
    print(stats)
    stats_df = stats.to_dataframe()
    print(stats_df)
    
    
    dfs = {}
    for name, df in TablesRecorder.generate_dataframes("thames_output.h5"):
        dfs[name] = df
        
    start_date = data['timestepper']['start'] 
    end_date = data['timestepper']['end'] 
    date_series = pandas.date_range(start=start_date, end=end_date, freq='D')
    dfs['reservoir1'].set_index(date_series, inplace=True)
    summer_res_data = dfs['reservoir1'][dfs['reservoir1'].index.month.isin([6, 7, 8])]
    winter_res_data = dfs['reservoir1'][dfs['reservoir1'].index.month.isin([12, 1, 2])]
### example metric 
    output_metric_summer = summer_res_data.mean()
    output_metric_winter = winter_res_data.mean()
    count_below_threshold_mrf = (dfs['mrf1'] < data['nodes'][2]['mrf']).sum()
    count_below_threshold_dem = (dfs['demand1'] < data['parameters']['demand_baseline']['values']).sum()
    count_equals_two = (dfs['demand_saving_level'] == 2).sum()
    
    return np.asarray(output_metric_summer), np.asarray(output_metric_winter), np.asarray(count_below_threshold_mrf), np.asarray(count_equals_two), np.asarray(count_below_threshold_dem)
        

    # keys_to_plot = (
    #     "time_taken_before",
    #     "solver_stats.bounds_update_nonstorage",
    #     "solver_stats.bounds_update_storage",
    #     "solver_stats.objective_update",
    #     "solver_stats.lp_solve",
    #     "solver_stats.result_update",
    #     "time_taken_after",
    # )

    # keys_to_tabulate = (
    #     "timesteps",
    #     "time_taken",
    #     "solver",
    #     "num_scenarios",
    #     "speed",
    #     "solver_name" "solver_stats.total",
    #     "solver_stats.number_of_rows",
    #     "solver_stats.number_of_cols",
    #     "solver_stats.number_of_nonzero",
    #     "solver_stats.number_of_routes",
    #     "solver_stats.number_of_nodes",
    # )

    # values = []
    # labels = []
    # explode = []
    # solver_sub_total = 0.0
    # for k in keys_to_plot:
    #     v = stats_df.loc[k][0]
    #     values.append(v)
    #     label = k.split(".", 1)[-1].replace("_", " ").capitalize()
    #     explode.append(0.0)
    #     if k.startswith("solver_stats"):
    #         labels.append("Solver - {}".format(label))
    #         solver_sub_total += v
    #     else:
    #         labels.append(label)

    # values.append(stats_df.loc["solver_stats.total"][0] - solver_sub_total)
    # labels.append("Solver - Other")
    # explode.append(0.0)

    # values.append(stats_df.loc["time_taken"][0] - sum(values))
    # values = np.array(values) / sum(values)
    # labels.append("Other")
    # explode.append(0.0)