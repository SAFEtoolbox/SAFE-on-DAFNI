
import numpy as np
import matplotlib.pyplot as plt
import xarray as xr

####
# Load power curve
#####
def load_power_curves(pc_array, pc_row_num):
    pc_w = (pc_array.columns).astype(float)
    pc_p = pc_array.iloc[pc_row_num, :]
    
    power_curve_w = np.array(pc_w)
    power_curve_p = np.array(pc_p)
    
    pc_winds = np.linspace(0, 50, 501)  # Make it finer resolution 
    pc_power = np.interp(pc_winds, power_curve_w, power_curve_p)

    return pc_winds, pc_power

def load_wind_speed_and_take_to_hubheight(path_to_wind_speed, C1, C2, longitude, latitude, alpha, hubheight):
    ds = xr.open_mfdataset(
    path_to_wind_speed,
    combine="by_coords"
    ).load()

    # Select the variables of interest
    point_u = ds[C1].values
    point_v = ds[C2].values
    
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


def wind_power_model_run(X, power_curves):
    power_curve_subset = power_curves.iloc[:,:-1]
    pc_winds, pc_power = load_power_curves(power_curve_subset, int(X[3]))
    if int(X[1]) == 0:
        timestep = '' 
    elif int(X[1]) == 1: 
        timestep = '_6h'
    elif int(X[1]) == 2: 
        timestep = '_daily'
    elif int(X[1]) == 3: 
        timestep = '_midnight'
        
    wind_data = f'C:\\Users\\Salwe001\\OneDrive - Universiteit Utrecht\\Documents\\papers\\usaris\\code\\ERA5_timestep_point\\' + 'ERA5_EU_1hr_uv100m_' + str(int(X[5])) + timestep + '.nc'
    if int(X[0]) == 0:
        hubheight_u = 'u10' 
        hubheight_v = 'v10'
    elif int(X[0]) == 1: 
        hubheight_u = 'u100' 
        hubheight_v = 'v100'
        
    # Dogger Bank
    longitude = 1.91
    latitude = 54.77
    hubheight = X[4]
    speed_100m, speed_hubheight = load_wind_speed_and_take_to_hubheight(wind_data, hubheight_u, hubheight_v, longitude, latitude, X[2], hubheight)
    WP_data = convert_to_wind_power(pc_winds, pc_power, speed_hubheight)
    # calculate output metrics 
    WP_mean = np.mean(WP_data)
    WP_median = np.median(WP_data)
    max_length = 0  # Longest consecutive length
    current_length = 0  # Current streak of consecutive values below the threshold
    event_lengths = []  # Store all event lengths
    num_events = 0  # Count total number of events
    threshold = 0.1  # Threshold value
    
    for value in WP_data:
        if value < threshold:
            if current_length == 0:  
                num_events += 1  # Start of a new event
            current_length += 1  # Increment current streak
            max_length = max(max_length, current_length)  # Update max length if needed
        else:
            if current_length > 0:
                event_lengths.append(current_length)  # Store completed event length
            current_length = 0  # Reset streak
    
    # Normalize max_length
    max_length = (max_length / len(WP_data)  ) 
    days_in_year = 366 if len(WP_data) in [1464, 8784, 366] else 365

    # Convert max_length from fraction of the year to days
    max_length_days = max_length * days_in_year
    
    # Compute average event length
    
    avg_length = np.mean(event_lengths) if event_lengths else 0
    avg_length = (avg_length/ len(WP_data) ) * days_in_year
    
    return np.array([ WP_mean,WP_median,  max_length_days, avg_length, num_events])

    
