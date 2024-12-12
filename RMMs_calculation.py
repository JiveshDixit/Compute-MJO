# -*- coding: utf-8 -*-
# Copyright (c) 2024 Jivesh Dixit, P.S. II, NCMRWF
# All rights reserved.
#
# This software is licensed under MIT license.
# Contact [jdixit@govcontractor.in].

import numpy as np
import xarray as xr
import dask.array as da
from dask.diagnostics import ProgressBar
from xeofs.single import EOF, EOFRotator
import scipy.signal as signal
import pandas as pd
from datetime import datetime, timedelta
import os


uwnd850_clim = xr.open_dataset('/home/jdixit/Calculate_Model_MJO/Climatology_u_850_1993-2015_regridded.nc')['u'].sel(lat=slice(15, -15)).mean(('lat')).squeeze()
uwnd200_clim = xr.open_dataset('/home/jdixit/Calculate_Model_MJO/Climatology_u_200_1993-2015_regridded.nc')['u'].sel(lat=slice(15, -15)).mean(('lat')).squeeze()
olr_clim = xr.open_dataset('/home/jdixit/Calculate_Model_MJO/Climatology_olr_1993-2015_regridded.nc')['olr'].sel(lat=slice(15, -15)).mean(('lat')).squeeze()


uwnd850_std = xr.open_dataset('/home/jdixit/Calculate_Model_MJO/Standard_dev_Obs/uwnd850_standard_deviation_obs_ncep_r2_1979-2001.nc')['uwnd'].mean(('lat'))

uwnd200_std = xr.open_dataset('/home/jdixit/Calculate_Model_MJO/Standard_dev_Obs/uwnd200_standard_deviation_obs_ncep_r2_1979-2001.nc')['uwnd'].mean(('lat'))

olr_std = xr.open_dataset('/home/jdixit/Calculate_Model_MJO/Standard_dev_Obs/olr_standard_deviation_obs_ncep_r2_1979-2001.nc')['olr'].mean(('lat'))

def get_latest_thursday():
    today = datetime.now()
    if today.weekday() == 3:
        latest_thursday = today
    else:
        days_since_thursday = (today.weekday() - 3) % 7
        latest_thursday = today - timedelta(days=days_since_thursday)
    return latest_thursday


latest_thursday_date = get_latest_thursday()


forecast_date = (datetime.strptime(latest_thursday_date.strftime('%Y%m%d'), '%Y%m%d')).strftime("%Y%m%dT0000Z")

initial = [(datetime.strptime(forecast_date, "%Y%m%dT%H%MZ") - timedelta(days=i)).strftime("%Y%m%dT0000Z") for i in range(4, 0, -1)]
members = ['mem1', 'mem2', 'mem3', 'mem4']


initial_date = (datetime.strptime(forecast_date, "%Y%m%dT%H%MZ") + timedelta(days=-120)).strftime("%Y%m%d")

end_date     = (datetime.strptime(forecast_date, "%Y%m%dT%H%MZ") + timedelta(days=-1)).strftime("%Y%m%d")

running_mean_start_ic = (datetime.strptime(forecast_date, "%Y%m%dT%H%MZ") + timedelta(days=-130)).strftime("%Y%m%d")
running_mean_end_ic = (datetime.strptime(forecast_date, "%Y%m%dT%H%MZ") + timedelta(days=-4)).strftime("%Y%m%d")


# past120_path = os.path.join(os.path.expanduser("~"), "forecast/Removal", f'final_concatenated_mem1_{running_mean_start_ic}-{running_mean_end_ic}.nc')

past120_path = os.path.join(os.path.expanduser("~"), "work", "ISO", "MJO","hindcast", f'final_concatenated_mem1_{running_mean_start_ic}-{running_mean_end_ic}.nc')

# past120_path = os.path.join(os.path.expanduser("~"), "forecast/Removal", f'final_concatenated_mem1_{running_mean_start_ic}-{running_mean_end_ic}.nc')



uwnd850_past120 = xr.open_dataset(past120_path)['u'].sel(level=850, time=slice(initial_date, end_date)).mean(('lat')).squeeze()
uwnd200_past120 = xr.open_dataset(past120_path)['u'].sel(level=200, time=slice(initial_date, end_date)).mean(('lat')).squeeze()
olr_past120 = xr.open_dataset(past120_path)['olr'].sel(time=slice(initial_date, end_date)).mean(('lat')).squeeze()


day_of_year = uwnd850_past120['time'].dt.dayofyear

uwnd850_past120_anom = (uwnd850_past120 - uwnd850_clim.sel(dayofyear=day_of_year))/uwnd850_std
uwnd200_past120_anom = (uwnd200_past120 - uwnd200_clim.sel(dayofyear=day_of_year))/uwnd200_std
olr_past120_anom = (olr_past120  - olr_clim.sel(dayofyear=day_of_year))/olr_std





uwnd850_forecast_anom = {}
uwnd200_forecast_anom = {}
olr_forecast_anom = {}

for num, ini in enumerate(initial):
    uwnd850_forecast_anom[ini] = {}
    uwnd200_forecast_anom[ini] = {}
    initial_date = datetime.strptime(ini, "%Y%m%dT%H%MZ").strftime("%Y%m%d")

    end_date     = (datetime.strptime(ini, "%Y%m%dT%H%MZ") + timedelta(days=18)).strftime("%Y%m%d")

    olr_forecast_anom[ini] = {}
    for member in members:


        forecast_path = os.path.join(os.path.expanduser("~"), "work", "ISO", "MJO","prediction", f'{ini}/{member}/1/concatenated_{initial_date}_{end_date}_{member}.nc')


        uwnd850_forecast = xr.open_dataset(forecast_path)['u']\
            .rename({'t':'time', 'latitude':'lat', 'longitude':'lon', 'p':'level'}).drop_vars(['toa'], errors='ignore')\
            .sel(level=850, time=slice((datetime.strptime(ini, "%Y%m%dT%H%MZ") + timedelta(days=4-num)).strftime("%Y%m%d"), \
            (datetime.strptime(ini, "%Y%m%dT%H%MZ") + timedelta(days=35-num)).strftime("%Y%m%d"))).mean(('lat')).squeeze()

        uwnd200_forecast = xr.open_dataset(forecast_path)['u']\
            .rename({'t':'time', 'latitude':'lat', 'longitude':'lon', 'p':'level'}).drop_vars(['toa'], errors='ignore')\
            .sel(level=200, time=slice((datetime.strptime(ini, "%Y%m%dT%H%MZ") + timedelta(days=4-num)).strftime("%Y%m%d"), \
            (datetime.strptime(ini, "%Y%m%dT%H%MZ") + timedelta(days=35-num)).strftime("%Y%m%d"))).mean(('lat')).squeeze()

        olr_forecast = xr.open_dataset(forecast_path)['olr']\
            .rename({'t':'time', 'latitude':'lat', 'longitude':'lon'}).drop_vars(['toa'], errors='ignore')\
            .sel(time=slice((datetime.strptime(ini, "%Y%m%dT%H%MZ") + timedelta(days=4-num)).strftime("%Y%m%d"), \
            (datetime.strptime(ini, "%Y%m%dT%H%MZ") + timedelta(days=35-num)).strftime("%Y%m%d"))).mean(('lat')).squeeze()

        day_of_year = uwnd850_forecast['time'].dt.dayofyear

        uwnd850_forecast_anom[ini][member] = (uwnd850_forecast - uwnd850_clim.sel(dayofyear=day_of_year))/uwnd850_std
        uwnd200_forecast_anom[ini][member] = (uwnd200_forecast - uwnd200_clim.sel(dayofyear=day_of_year))/uwnd200_std
        olr_forecast_anom[ini][member] = (olr_forecast - olr_clim.sel(dayofyear=day_of_year))/olr_std







uwnd850_concat = {}
uwnd200_concat = {}
olr_concat = {}

for ini in initial:
    uwnd850_concat[ini] = {}
    uwnd200_concat[ini] = {}
    olr_concat[ini] = {}
    for member in members:
        uwnd850_concat[ini][member] = xr.concat((uwnd850_past120_anom, uwnd850_forecast_anom[ini][member]), dim='time')
        uwnd200_concat[ini][member] = xr.concat((uwnd200_past120_anom, uwnd200_forecast_anom[ini][member]), dim='time')      
        olr_concat[ini][member] = xr.concat((olr_past120_anom, olr_forecast_anom[ini][member]), dim='time')



# def subtract_lagged_120_day_mean(data, data1):

#     lagged_mean = data1.rolling(time=120, min_periods=1).mean(skipna=True)
#     print(lagged_mean.time, len(lagged_mean))
#     return data - lagged_mean


def subtract_lagged_120_day_mean(data, data1):

    forecast_start=pd.to_datetime(data.time.values[0]).strftime('%Y-%m-%d')
    forecast_end=pd.to_datetime(data.time.values[-1]).strftime('%Y-%m-%d')

    lagged_mean = data1.rolling(time=120, min_periods=1).mean(skipna=True).shift(time=1)
    lagged_mean = lagged_mean.sel(time=slice(forecast_start,forecast_end))

    print(lagged_mean.time, len(lagged_mean))
    return data - lagged_mean




rmm1_std = 4.31881234
rmm2_std = 4.18007485


rmm1 = {}
rmm2 = {}

eofs_modes = xr.open_dataset('/home/jdixit/Calculate_Model_MJO/EOFs_OLR_NCEI_Uwnd_NCEP_r2_rotated_1980-2023.nc')['components']


import xarray as xr
import os


directory = os.path.join(os.path.expanduser("~"), "work", "ISO", "MJO", "RMMs", f'{forecast_date[:8]}')

if not os.path.exists(directory):
    os.makedirs(directory)

file_path_1 = os.path.join(directory, f'RMM1_CNCUM_IC_{initial[0][:8]}-{initial[-1][:8]}_FC_{forecast_date[:8]}.nc')
file_path_2 = os.path.join(directory, f'RMM2_CNCUM_IC_{initial[0][:8]}-{initial[-1][:8]}_FC_{forecast_date[:8]}.nc')


rmm1_data = {}
rmm2_data = {}

for ini in initial:
    rmm1_data[ini] = {}
    rmm2_data[ini] = {}
    for member in members:

        uwnd850_forecast_anom_to_project = subtract_lagged_120_day_mean(uwnd850_forecast_anom[ini][member], uwnd850_concat[ini][member])
        uwnd200_forecast_anom_to_project = subtract_lagged_120_day_mean(uwnd200_forecast_anom[ini][member], uwnd200_concat[ini][member])
        olr_forecast_anom_to_project = subtract_lagged_120_day_mean(olr_forecast_anom[ini][member], olr_concat[ini][member])

        # uwnd850_forecast_anom_to_project = uwnd850_forecast_anom[ini][member]
        # uwnd200_forecast_anom_to_project = uwnd200_forecast_anom[ini][member]
        # olr_forecast_anom_to_project = olr_forecast_anom[ini][member]


        combined_anomalies_zonal = xr.concat(
            [uwnd850_forecast_anom_to_project, uwnd200_forecast_anom_to_project, olr_forecast_anom_to_project], 
            dim='variable', coords='minimal', compat='override'
        ).transpose('time', 'lon', 'variable')


        rmm1 = -xr.dot(combined_anomalies_zonal, eofs_modes)[:, 0] / rmm1_std
        rmm2 = xr.dot(combined_anomalies_zonal, eofs_modes)[:, 1] / rmm2_std

        rmm1.name = f'RMM1_{ini[:8]}_{member}'
        rmm2.name = f'RMM2_{ini[:8]}_{member}'

        rmm1_data[ini][member] = rmm1
        rmm2_data[ini][member] = rmm2


combined_rmm1 = xr.Dataset(
    {f'RMM1_{ini}_{member}': rmm1_data[ini][member] for ini in rmm1_data for member in rmm1_data[ini]}
)
combined_rmm2 = xr.Dataset(
    {f'RMM2_{ini}_{member}': rmm2_data[ini][member] for ini in rmm2_data for member in rmm2_data[ini]}
)

if os.path.exists(file_path_1):
    os.remove(file_path_1)
if os.path.exists(file_path_2):
    os.remove(file_path_2)


combined_rmm1.to_netcdf(file_path_1, mode='w')
combined_rmm2.to_netcdf(file_path_2, mode='w')