#!/bin/python
# -*- coding: utf-8 -*-

#  Proj quarry detection and time machine
################################################################
#  Script used to run automatically Prediction workflow for quarries detection
#  Inputs are defined in config-prd.template.yaml


echo 'Run batch processes to make quarries prediction over several years'

for year in YEAR1 YEAR2 YEAR3 ...       #list of years to process 
do
    echo ' '
    echo '-----------'
    echo Year = $year
    sed 's/#YEAR#/$year/g' config-prd.template.yaml > config-prd_$year.yaml
    sed -i "s/SWISSIMAGE_YEAR/$year/g" config-prd_$year.yaml
    echo ' '
    echo 'prepare_data.py'
    python3 ../scripts/prepare_data.py config-prd_$year.yaml
    echo ' '
    echo 'generate_tilesets.py'
    python3 ../../object-detector/scripts/generate_tilesets.py config-prd_$year.yaml
    echo ' '
    echo 'make_prediction.py'
    python3 ../../object-detector/scripts/make_predictions.py config-prd_$year.yaml
    echo ' '
    echo 'prediction_filter.py'
    python3 ../scripts/prediction_filter.py config-prd_$year.yaml
done