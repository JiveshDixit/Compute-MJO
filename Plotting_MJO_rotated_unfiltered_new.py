# -*- coding: utf-8 -*-
# Copyright (c) 2024 Jivesh Dixit, P.S. II, NCMRWF
# All rights reserved.
#
# This software is licensed under MIT license.
# Contact [jdixit@govcontractor.in].


import numpy as np
import matplotlib.pyplot as plt
import xarray as xr
from matplotlib.animation import FuncAnimation
import pandas as pd
from datetime import datetime, timedelta
import os


def set_up_rmm_phase_diagram_axes(fig, draw_axes_tick_labels=True,
                                   draw_axes_titles=True, draw_rmm_phase_labels=True,
                                   draw_region_names=True, IC=None):
    
    axrmm = fig.add_subplot(1, 1, 1)

    theta = np.linspace(0, 2 * np.pi, 361)
    axrmm.plot(np.cos(theta), np.sin(theta), 'k', linewidth=2, linestyle='--')

    lines = [
        ([-4.0, -1.0], [0.0, 0.0]),  # horizontal
        ([1.0, 4.0], [0.0, 0.0]),    # horizontal
        ([0, 0], [-4.0, -1.0]),      # vertical
        ([0, 0], [1.0, 4.0]),        # vertical
        ([-4.0, -0.707], [-4.0, -0.707]),  # diagonal
        ([0.707, 4.0], [0.707, 4.0]),      # diagonal
        ([-4.0, -0.707], [4.0, 0.707]),    # diagonal
        ([0.707, 4.0], [-0.707, -4.0]),     # diagonal
    ]
    
    for i, (x, y) in enumerate(lines):
        axrmm.plot(x, y, 'k', linewidth=2, linestyle='--')


    if draw_axes_tick_labels:
        axrmm.set_xlim([-4, 4])
        axrmm.set_ylim([-4, 4])
        axrmm.set_xticks(np.arange(-4, 5, 2))
        axrmm.set_yticks(np.arange(-4, 5, 2))
        axrmm.set_xticklabels(np.arange(-4, 5, 2), fontsize=12, fontweight='bold')
        axrmm.set_yticklabels(np.arange(-4, 5, 2), fontsize=12, fontweight='bold')

    if draw_axes_titles:
        axrmm.set_xlabel('RMM1', fontsize=12, fontweight='bold')
        axrmm.set_ylabel('RMM2', fontsize=12, fontweight='bold')

    if draw_rmm_phase_labels:
        mjo_regions = {
            '1': (-3.8, -2.0),
            '2': (-2.0, -3.8),
            '3': (2.0, -3.8),
            '4': (3.5, -2.0),
            '5': (3.5, 2.0),
            '6': (2.0, 3.5),
            '7': (-2.0, 3.5),
            '8': (-3.8, 2.0)
        }
        
        for region, (x, y) in mjo_regions.items():
            axrmm.text(x, y, region, color='b', fontsize=12, fontweight='bold')

    if draw_region_names:
        region_names = {
            'Western Pacific': (0, 3.5),
            'Maritime Continent': (3.5, 0),
            'Indian Ocean': (0, -3.5),
            'Western \nHemisphere\n and Africa': (-3.5, 0),
        }
        
        for name, (x, y) in region_names.items():
            if name == 'Maritime Continent' or name == 'Western \nHemisphere\n and Africa':
                axrmm.text(x, y, name, rotation='vertical', fontsize=15, ha='center', va='center', fontweight='bold', color='darkorange', zorder=2)
            else:
                axrmm.text(x, y, name, fontsize=15, ha='center', va='center', fontweight='bold', color='darkorange', zorder=2)

    axrmm.set_aspect('equal')
    return axrmm


# def add_rmm_index_trace(RMM, axrmm, linewidth=1, alpha=1.0):
    
#     rmm1keep = RMM['RMM1']
#     rmm2keep = RMM['RMM2']
#     time_index = RMM['RMM1']['time']
#     time_index = pd.to_datetime(time_index, errors='coerce')
#     months = time_index.month

#     month_colors = {
#         1: 'r', 2: 'g', 3: 'b', 4: 'r', 5: 'g', 6: 'b', 
#         7: 'r', 8: 'g', 9: 'b', 10: 'r', 11: 'g', 12: 'b'
#     }

#     for month in range(1, 13):
#         mask = months == month
#         month_indices = np.where(mask)[0]
        
#         if len(month_indices) == 0:
#             continue
        
#         month_start_index = month_indices[0]
#         month_end_index = month_indices[-1]

#         axrmm.plot(rmm1keep[month_start_index:month_end_index + 1], 
#                    rmm2keep[month_start_index:month_end_index + 1], 
#                    color=month_colors[month], 
#                    linewidth=linewidth, 
#                    alpha=alpha)

#         if month < 12:
#             next_month_start_index = month_indices[-1] + 1
#             if next_month_start_index < len(rmm1keep) and months[next_month_start_index] == month + 1:
#                 axrmm.plot(
#                     [rmm1keep[month_end_index], rmm1keep[next_month_start_index]], 
#                     [rmm2keep[month_end_index], rmm2keep[next_month_start_index]], 
#                     color=month_colors[month + 1], 
#                     linewidth=linewidth, 
#                     alpha=alpha
#                 )



def add_rmm_index_trace(RMM, axrmm, linewidth=2, alpha=1.0):
    rmm1keep = RMM['RMM1']
    rmm2keep = RMM['RMM2']
    time_index = pd.to_datetime(RMM['RMM1']['time'], errors='coerce')
    months = time_index.month
    years = time_index.year

    month_colors = {
        1: 'r', 2: 'g', 3: 'b', 4: 'r', 5: 'g', 6: 'b',
        7: 'r', 8: 'g', 9: 'b', 10: 'r', 11: 'g', 12: 'b'
    }

    for month in range(1, 13):
        mask = (months == month)
        month_indices = np.where(mask)[0]

        if len(month_indices) == 0:
            continue

        month_start_index = month_indices[0]
        month_end_index = month_indices[-1]


        axrmm.plot(
            rmm1keep[month_start_index:month_end_index + 1],
            rmm2keep[month_start_index:month_end_index + 1],
            color=month_colors[month],
            linewidth=linewidth,
            alpha=alpha
        )


        if month < 12:
            next_month_mask = (months == (month + 1)) & (years == years[month_end_index])
        else:

            next_month_mask = (months == 1) & (years == years[month_end_index] + 1)

        if np.any(next_month_mask):
            next_month_start_index = np.where(next_month_mask)[0][0]
            

            axrmm.plot(
                [rmm1keep[month_end_index], rmm1keep[next_month_start_index]],
                [rmm2keep[month_end_index], rmm2keep[next_month_start_index]],
                color=month_colors[(month % 12) + 1],
                linewidth=linewidth,
                alpha=alpha
            )



# def add_rmm_index_trace_animation(RMM, axrmm, save_path='mjo_phase_diagram.gif', dpi=450):
    
#     rmm1keep = RMM['RMM1']
#     rmm2keep = RMM['RMM2']
#     time_index = pd.to_datetime(RMM['RMM1']['time'], errors='coerce')
#     months = time_index.month

#     month_colors = {
#         1: 'r', 2: 'g', 3: 'b', 4: 'r', 5: 'g', 6: 'b', 
#         7: 'r', 8: 'g', 9: 'b', 10: 'r', 11: 'g', 12: 'b'
#     }

#     month_names = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 
#                    'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']


    
#     for month in np.unique(months):
#         mask = months == month
#         axrmm.plot(rmm1keep[mask], rmm2keep[mask], color=month_colors[month], linewidth=3)

#         first_index = np.where(mask)[0][0]

#     for month in range(1, 12):
#         end_of_month_mask = months == month
#         start_of_next_month_mask = months == (month + 1)

#         if np.any(end_of_month_mask) and np.any(start_of_next_month_mask):
#             end_x = rmm1keep[end_of_month_mask][-1]
#             end_y = rmm2keep[end_of_month_mask][-1]
#             start_x = rmm1keep[start_of_next_month_mask][0]
#             start_y = rmm2keep[start_of_next_month_mask][0]
#             axrmm.plot([end_x, start_x], [end_y, start_y], color=month_colors[month + 1], linewidth=3)

#     scatter = axrmm.scatter([], [], s=20, color='black', edgecolors='k')
    
#     date_texts = []
#     for _ in range(len(rmm1keep)):
#         date_text = axrmm.text(0, 0, '', fontsize=10, ha='center', fontweight='bold')
#         date_texts.append(date_text)

#     def update(frame):
#         if frame < len(rmm1keep):
#             scatter.set_offsets(np.c_[rmm1keep[:frame + 1], rmm2keep[:frame + 1]])

#             for idx in range(frame + 1):  # Show all previous dates as well
#                 current_date_str = time_index[idx].strftime('%d')
#                 date_texts[idx].set_position((rmm1keep[idx], rmm2keep[idx] + 0.02))
#                 date_texts[idx].set_text(current_date_str)

#             current_title_date = time_index[frame].strftime('%Y-%m-%d')
#             axrmm.set_title(f'16 member forecast starting {forecast_date[:8]}\non: {current_title_date}', fontsize=15, fontweight='bold')

#         return scatter, *date_texts

#     ani = FuncAnimation(
#         fig, update, frames=len(rmm1keep), interval=100, blit=True
#     )

#     ani.save(save_path, writer='imagemagick', fps=2, dpi=dpi)

#     return ani


def add_rmm_index_trace_animation(RMM, axrmm, save_path='mjo_phase_diagram.gif', dpi=450):
    rmm1keep = RMM['RMM1']
    rmm2keep = RMM['RMM2']
    time_index = pd.to_datetime(RMM['RMM1']['time'], errors='coerce')
    months = time_index.month
    years = time_index.year

    month_colors = {
        1: 'r', 2: 'g', 3: 'b', 4: 'r', 5: 'g', 6: 'b',
        7: 'r', 8: 'g', 9: 'b', 10: 'r', 11: 'g', 12: 'b'
    }

    month_names = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 
                   'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

    for month in range(1, 13):
        mask = months == month
        month_indices = np.where(mask)[0]

        if len(month_indices) == 0:
            continue

        month_start_index = month_indices[0]
        month_end_index = month_indices[-1]


        axrmm.plot(
            rmm1keep[month_start_index:month_end_index + 1],
            rmm2keep[month_start_index:month_end_index + 1],
            color=month_colors[month],
            linewidth=3
        )

    dec_mask = (months == 12)
    jan_mask = (months == 1)

    if np.any(dec_mask) and np.any(jan_mask):
        dec_last_index = np.where(dec_mask)[0][-1]
        jan_first_index = np.where(jan_mask)[0][0]

        if years[jan_first_index] == years[dec_last_index] + 1:
            axrmm.plot(
                [rmm1keep[dec_last_index], rmm1keep[jan_first_index]],
                [rmm2keep[dec_last_index], rmm2keep[jan_first_index]],
                color=month_colors[month],  # Use black for the connecting line
                linewidth=3
            )


    scatter = axrmm.scatter([], [], s=20, color='black', edgecolors='k')

    date_texts = []
    for _ in range(len(rmm1keep)):
        date_text = axrmm.text(0, 0, '', fontsize=10, ha='center', fontweight='bold')
        date_texts.append(date_text)

    def update(frame):
        if frame < len(rmm1keep):
            scatter.set_offsets(np.c_[rmm1keep[:frame + 1], rmm2keep[:frame + 1]])

            for idx in range(frame + 1):
                current_date_str = time_index[idx].strftime('%d')
                date_texts[idx].set_position((rmm1keep[idx], rmm2keep[idx] + 0.02))
                date_texts[idx].set_text(current_date_str)

            current_title_date = time_index[frame].strftime('%Y-%m-%d')
            axrmm.set_title(f'16 member forecast starting {time_index[0].strftime("%Y%m%d")}\non: {current_title_date}', fontsize=15, fontweight='bold')

        return scatter, *date_texts

    ani = FuncAnimation(
        plt.gcf(), update, frames=len(rmm1keep), interval=100, blit=True
    )

    ani.save(save_path, writer='imagemagick', fps=2, dpi=dpi)

    return ani



available_months = set()


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
initial = [(datetime.strptime(forecast_date, "%Y%m%dT0000Z") - timedelta(days=i)).strftime("%Y%m%dT0000Z") for i in range(4, 0, -1)]
members = ['mem1', 'mem2', 'mem3', 'mem4']

directory = os.path.join(os.path.expanduser("~"), "work", "ISO", "MJO", "RMMs", f"{forecast_date[:8]}")

file_path_1 = os.path.join(directory, f'RMM1_CNCUM_IC_{initial[0][:8]}-{initial[-1][:8]}_FC_{forecast_date[:8]}.nc')
file_path_2 = os.path.join(directory, f'RMM2_CNCUM_IC_{initial[0][:8]}-{initial[-1][:8]}_FC_{forecast_date[:8]}.nc')

directory = os.path.join(os.path.expanduser("~"), "work", "plots", "ISO", "MJO", f"{forecast_date[:8]}")
if not os.path.exists(directory):
    os.makedirs(directory)



plot_path = os.path.join(directory, f'mjo_phase_diagram_cncum_forecast_{forecast_date[:8]}.gif')





rmm1_total = 0
rmm2_total = 0

for ini in initial:
    for member in members:
        rmm1_data = xr.open_dataset(file_path_1)[f'RMM1_{ini}_{member}']
        rmm2_data = xr.open_dataset(file_path_2)[f'RMM2_{ini}_{member}']        
        rmm1_total += rmm1_data
        rmm2_total += rmm2_data

num_entries = len(initial) * len(members)  # Total number of entries
rmm1_average = rmm1_total / num_entries
rmm2_average = rmm2_total / num_entries




fig = plt.figure(figsize=(8, 8))
axrmm = set_up_rmm_phase_diagram_axes(fig, IC=initial[0][:8])


month_colors = {
    1: 'r', 2: 'g', 3: 'b', 4: 'r', 5: 'g', 6: 'b', 
    7: 'r', 8: 'g', 9: 'b', 10: 'r', 11: 'g', 12: 'b'
}

month_names = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 
               'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']


for ini in initial:
    for member in members:
        rmm1_data = xr.open_dataset(file_path_1)[f'RMM1_{ini}_{member}']
        rmm2_data = xr.open_dataset(file_path_2)[f'RMM2_{ini}_{member}']
        RMM = {'RMM1': rmm1_data, 'RMM2': rmm2_data}
        add_rmm_index_trace(RMM, axrmm, linewidth=1, alpha=0.3)
        time_index = pd.to_datetime(rmm1_data['time'].values, errors='coerce')
        months = time_index.month
        available_months.update(months)


legend_handles = [plt.Line2D([0], [0], color=month_colors[i], lw=4) for i in available_months]


axrmm.legend(legend_handles, [month_names[i-1] for i in available_months], title="Months", loc='upper right', fontsize=10)

RMM = {'RMM1': rmm1_average, 'RMM2': rmm2_average}

add_rmm_index_trace_animation(RMM, axrmm, save_path=plot_path)

plt.show()
