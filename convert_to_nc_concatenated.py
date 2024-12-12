# -*- coding: utf-8 -*-
# Copyright (c) 2024 Jivesh Dixit, P.S. II, NCMRWF
# All rights reserved.
#
# This software is licensed under MIT license.
# Contact [jdixit@govcontractor.in].

import xarray as xr
import os
from datetime import datetime, timedelta




directory = os.path.join(os.path.expanduser("~"), "work", "ISO", "MJO","hindcast")
if not os.path.exists(directory):
    os.makedirs(directory)


src_base = directory
target_base = directory


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


start_date = (datetime.strptime(forecast_date, "%Y%m%dT%H%MZ") + timedelta(days=-130))
end_date = (datetime.strptime(forecast_date, "%Y%m%dT%H%MZ") + timedelta(days=-4))


members = ['mem1']


for member in members:
    current_date = start_date
    all_data = [] 

    while current_date <= end_date:

        current_folder = os.path.join(src_base, current_date.strftime("%Y%m%dT0000Z"), member, "1")

        

        if os.path.isdir(current_folder):

            current_file = os.path.join(current_folder, f"cplfca_{current_date.strftime('%Y%m%d')}_{member}.nc")

            
            if os.path.isfile(current_file):
                ds_current = xr.open_dataset(current_file).rename({'t':'time', 'latitude':'lat', 'longitude':'lon', 'p':'level'})

                ds_current_subset = ds_current.isel(time=slice(0, 7)).sel(level=[200, 850]).drop_vars(['toa'], errors='ignore')

                all_data.append(ds_current_subset)

        current_date += timedelta(days=7)


    if all_data:
        final_concatenated = xr.concat(all_data, dim='time')
        print(final_concatenated.time.values)
        output_file = os.path.join(target_base, f"final_concatenated_{member}_{start_date.strftime('%Y%m%d')}-{end_date.strftime('%Y%m%d')}.nc")
        final_concatenated.to_netcdf(output_file)
        print(f"Final concatenated file saved for {member}: {output_file}")