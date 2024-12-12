#!/bin/bash


# Copyright (c) 2024 Jivesh Dixit, P.S. II, NCMRWF
# All rights reserved.
#
# This software is licensed under MIT license.
# Contact [jdixit@govcontractor.in].


export PATH="/home/jdixit/anaconda3/envs/xIndices/bin/:$PATH"
module load pbs
module load alps/6.4.3-6.0.4.1_2.1__g92a2fc0.ari
module load precompiled/xconv/1.93

SERVER="$USER@192.168.0.98"
remote_base="/Cray_Archival/home/erfprod/data/erfgc2/forecast"
local_base="/home/erfprod/data/erfgc2/forecast"
target_base="$HOME/work/ISO/MJO/hindcast"


today=${1:-$(date +%Y-%m-%d)}
weekday=$(date -d "$today" +%u)
last_thursday=$(date -d "$today -$(( (weekday + 3) % 7 )) days" +%Y%m%d)
start_date=$(date -d "$last_thursday - 130 days" +%Y%m%d)
end_date=$(date -d "$last_thursday - 4 days" +%Y%m%d)

echo "Start Date: $start_date"
echo "End Date: $end_date"





current="$start_date"
while [ "$current" -le "$end_date" ]; do
    dir_name="${current}T0000Z"

    for member in mem1; do
        file_name="cplfca.pf${current}"
        remote_file="$remote_base/$dir_name/$member/1/$file_name"
        local_file="$local_base/$dir_name/$member/1/$file_name"
        target_dir="$target_base/$dir_name/$member/1"
        mkdir -p "$target_dir"


        if ssh -o StrictHostKeyChecking=no "$SERVER" "[ -f $remote_file ]"; then
            echo "Processing remote file: $remote_file"
            target_file="$target_dir/${file_name:0:6}_${dir_name:0:8}_${member}.nc"
            ssh -o StrictHostKeyChecking=no "$SERVER" "~/Concatenated_hindcast_ERP/subset.tcl -i $remote_file -o $target_file -xs 0 -xe 360 -xi 2.5 -ys 15 -ye -15 -yi 2.5" && \
            echo "Remote processing complete for $remote_file"
        elif [ -f "$local_file" ]; then
            echo "Remote file not found, processing local file: $local_file"
            target_file="$target_dir/${file_name:0:6}_${dir_name:0:8}_${member}.nc"
            ~/Concatenated_hindcast_ERP/subset.tcl -i "$local_file" -o "$target_file" -xs 0 -xe 360 -xi 2.5 -ys 15 -ye -15 -yi 2.5 && \
            echo "Local processing complete for $local_file"
        else
            echo "File not found on server or locally: $file_name"
        fi
    done


    current=$(date -d "$current + 7 days" +%Y%m%d)
done

echo "Data processing complete."