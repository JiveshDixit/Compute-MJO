#!/bin/bash

# Copyright (c) 2024 Jivesh Dixit, P.S. II, NCMRWF
# All rights reserved.
#
# This software is licensed under MIT license.
# Contact [jdixit@govcontractor.in].

export PATH="/home/jdixit/anaconda3/envs/xIndices/bin/:$PATH"
module load gnu/nco/5.0.4_with_udunit

scripts=(
    "Convert_data_for_variability_removal_new.sh"
    "convert_to_nc_concatenated.py"
    "convert_to_nc_extract_both_forecast.sh"
    "RMMs_calculation.py"
    "Plotting_MJO_rotated_unfiltered_new.py"
)


execute_script() {
    script="$1"
    if [[ -f "$script" ]]; then
        echo "Executing $script..."
        if [[ "$script" == *.sh ]]; then
            bash "$script" 
        elif [[ "$script" == *.py ]]; then
            python "$script"
        else
            echo "Unsupported file type: $script"
        fi
    else
        echo "File not found: $script"
    fi
}


for script in "${scripts[@]}"; do
    execute_script "$script"
done

find /home/jdixit/work/ISO/MJO/hindcast -mindepth 1 -type d -exec rm -rf {} +


echo "All specified scripts executed."
