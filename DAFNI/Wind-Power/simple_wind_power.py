# -*- coding: utf-8 -*-
"""
Created on Wed Jul  3 13:46:20 2024

@author: ss16144
"""

import numpy as np
import xarray as xr

####
# Load power curve
#####
# This could be adapted if you just want one (or many) curves per site.
def load_power_curves(pc_array, pc_row_num):
    # Inputs:
    # Power curves .csv file
    # Outputs:
    # Interpolated power curves.
    
    pc_w = (pc_array.columns).astype(float)
    pc_p = pc_array.iloc[pc_row_num, :]
    
    # with open(path_onshore_curve) as f:
    #     for line in f:
    #         columns = line.split()
    #         pc_p.append(float(columns[1][0:8]))  # Get power curve output (CF)
    #         pc_w.append(float(columns[0][0:8]))  # Get power curve output (CF)
    
    power_curve_w = np.array(pc_w)
    power_curve_p = np.array(pc_p)
    
    pc_winds = np.linspace(0, 50, 501)  # Make it finer resolution 
    pc_power = np.interp(pc_winds, power_curve_w, power_curve_p)

    return pc_winds, pc_power

def load_wind_speed_and_take_to_hubheight(path_to_wind_speed, C1, C2, longitude, latitude, alpha, hubheight):
    # Load the dataset using xarray
    ds = xr.open_mfdataset(path_to_wind_speed, combine='by_coords')
    
    # Select the variables of interest
    data_u = ds[C1]
    data_v = ds[C2]
    
    # Extract latitude and longitude arrays
    LATS = data_u.coords['latitude'].values
    LONS = data_u.coords['longitude'].values
    
    # Find the nearest point to the specified latitude and longitude
    lon_idx = (np.abs(LONS - longitude)).argmin()
    lat_idx = (np.abs(LATS - latitude)).argmin()
    
    # Extract the data for the nearest point
    point_u = data_u[:, lat_idx, lon_idx].values
    point_v = data_v[:, lat_idx, lon_idx].values
    
    # Calculate wind speed
    speed = np.sqrt(point_u**2 + point_v**2)
    
    # Adjust wind speed to hub height
    hub_height = float(hubheight)
    reanalysis_height = float(C1[1:])
    correction_hubheight = (hub_height / reanalysis_height) ** alpha  
    speed_hubheight = speed * correction_hubheight
    
    return speed, speed_hubheight

def convert_to_wind_power(pc_winds, pc_power, speed_hubheight):
    # 'Digitize' the wind speeds in the appropriate bins in the power curve
    test = np.digitize(speed_hubheight, pc_winds, right=False)
    test[test == len(pc_winds)] = 500  # Ensure the bins don't go off the end (power is zero by then anyway)
    
    # Calculate the wind power capacity factor (average between two nearest bins)
    CF_data = 0.5 * (pc_power[test - 1] + pc_power[test])
    
    return CF_data


## write a function that runs the model with the input (X) dataset containing all the sampled parameters and inputs 


def wind_power_model_run(X, power_curves):
    #pc_path = 'C:\\Users\\ss16144\\OneDrive - University of Bristol\\Documents\\DAFNI\\1. Model Code\\Wind Power Model\\full_europe_wind_model_for_saskia\\power_onshore.csv'
    # the above should be X[0] eventually, have hard coded for now 
    power_curve_subset = power_curves.iloc[:,:-1]
    pc_winds, pc_power = load_power_curves(power_curve_subset, int(X[3]))
    if int(X[2]) == 0:
        timestep = '' 
    elif int(X[2]) == 1: 
        timestep = '_6h'
    elif int(X[2]) == 2: 
        timestep = '_daily'
    elif int(X[2]) == 3: 
        timestep = '_midnight'
        
    wind_data = '/data/inputs/' + 'ERA5_EU_1hr_uv100m_' + str(int(X[1])) + timestep + '.nc'

    print('path to wind speed data:', wind_data)
    
    if int(X[0]) == 0:
        hubheight_u = 'u10' 
        hubheight_v = 'v10'
    elif int(X[0]) == 1: 
        hubheight_u = 'u100' 
        hubheight_v = 'v100'
        
        ## manual for now 
    ### DOGGER BANK ### 
    longitude = 1.91
    latitude = 54.77
    hubheight = X[5]
    speed_100m, speed_hubheight = load_wind_speed_and_take_to_hubheight(wind_data, hubheight_u, hubheight_v, longitude, latitude, X[4], hubheight)
    WP_data = convert_to_wind_power(pc_winds, pc_power, speed_hubheight)
    WP_mean = np.mean(WP_data)

    return np.array([WP_mean])
    #return np.asarray(count)
    
