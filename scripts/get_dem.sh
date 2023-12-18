#!/bin/bash
# Download DEM tif file

mkdir -p ./input/input_det/DEM/
wget https://github.com/lukasmartinelli/swissdem/releases/download/v1.0/switzerland_dem.tif -O ./input/input_det/DEM/switzerland_dem.tif
gdalwarp -t_srs "EPSG:2056" ./input/input_det/DEM/switzerland_dem.tif ./input/input_det/DEM/switzerland_dem_EPSG2056.tif
rm ./input/input_det/DEM/switzerland_dem.tif