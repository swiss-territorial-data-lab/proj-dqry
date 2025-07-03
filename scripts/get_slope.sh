#!/bin/bash

mkdir -p ./data/slope/
wget https://github.com/lukasmartinelli/swissdem/releases/download/v1.0/switzerland_slope.tif -O ./data/slope/switzerland_slope.tif
gdalwarp -t_srs "EPSG:2056" ./data/slope/switzerland_slope.tif ./data/slope/switzerland_slope_EPSG2056.tif
rm ./data/slope/switzerland_slope.tif