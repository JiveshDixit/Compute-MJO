#!/bin/bash

# Copyright (c) 2024 Jivesh Dixit, P.S. II, NCMRWF
# All rights reserved.
#
# This software is licensed under MIT license.
# Contact [jdixit@govcontractor.in].


module load gnu/nco/5.0.4_with_udunit
module load pbs
module load alps/6.4.3-6.0.4.1_2.1__g92a2fc0.ari
module load precompiled/xconv/1.93



if [ -z "$1" ]; then
    today=$(date +%Y-%m-%d)
else
    today="$1"
fi


weekday=$(date -d "$today" +%u)


if [ "$weekday" -eq 4 ]; then

    LAST_THURSDAY=$(date -d "$today" +%Y%m%d)
else

    days_to_subtract=$(( (weekday + 3) % 7))  # Add 7 to ensure we get the last Thursday
    LAST_THURSDAY=$(date -d "$today -$days_to_subtract days" +%Y%m%d)
fi


GIVEN_DATE="${1:-$LAST_THURSDAY}"
END_DATE=$(date -d "$GIVEN_DATE - 1 days" +%Y%m%d)
START_DATE=$(date -d "$GIVEN_DATE - 4 days" +%Y%m%d)




src_base="/home/erfprod/data/erfgc2/forecast"
target_base="$HOME/work/ISO/MJO/prediction"

for member in mem1 mem2 mem3 mem4; do

    current_date="$START_DATE"
    while [ "$current_date" -le "$END_DATE" ]; do
        DIR_NAME="${current_date}T0000Z"
        src_folder="$src_base/$DIR_NAME"


        if [[ ! -d "$src_folder" ]]; then
            echo "Source folder not found: $src_folder"
            current_date=$(date -d "$current_date + 1 day" +%Y%m%d)
            continue
        fi


        folder_name=$(basename "$src_folder")


        file_name="cplfca.pf${current_date}"
        source_file="$src_folder/$member/1/$file_name"


        echo "Checking for source file: $source_file"


        target_dir="$target_base/$folder_name/$member/1/"
        mkdir -p "$target_dir"


        if [[ -f "$source_file" ]]; then
            ~/Concatenated_hindcast_ERP/subset.tcl -i "$source_file" -o "$target_dir${file_name}_${current_date}_${member}.nc" -xs 0 -xe 360 -xi 2.5 -ys 15 -ye -15 -yi 2.5 && \
            echo "Copied $source_file to $target_dir"
        else
            echo "File $source_file not found"
            current_date=$(date -d "$current_date + 1 day" +%Y%m%d)
            continue
        fi


        second_date=$(date -d "$current_date + 18 days" +"%Y%m%d")


        second_file_name="cplfca.pf${second_date}"
        second_source_file="$src_folder/$member/1/$second_file_name"


        echo "Checking for second source file: $second_source_file"


        if [[ -f "$second_source_file" ]]; then
            ~/Concatenated_hindcast_ERP/subset.tcl -i "$second_source_file" -o "$target_dir${second_file_name}_${second_date}_${member}.nc" -xs 0 -xe 360 -xi 2.5 -ys 15 -ye -15 -yi 2.5 && \
            echo "Copied $second_source_file to $target_dir"
        else
            echo "File $second_source_file not found"
            current_date=$(date -d "$current_date + 1 day" +%Y%m%d)
            continue
        fi


        first_output_file="${target_dir}/${file_name}_${current_date}_${member}.nc"
        second_output_file="${target_dir}/${second_file_name}_${second_date}_${member}.nc"
        concatenated_file="${target_dir}/concatenated_${current_date}_${second_date}_${member}.nc"

        ncrcat -O "$first_output_file" "$second_output_file" "$concatenated_file" && \
        echo "Concatenated files into $concatenated_file"


        current_date=$(date -d "$current_date + 1 day" +%Y%m%d)
    done
done
