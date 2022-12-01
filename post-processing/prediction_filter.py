#!/bin/python
# -*- coding: utf-8 -*-

#  prediction-thresholding
#
#      Nils Hamel - nils.hamel@alumni.epfl.ch
#      Huriel Reichel - huriel.reichel@protonmail.com
#      Alessandro Cerioni
#      Copyright (c) 2020-2022 Republic and Canton of Geneva
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import logging.config
import time
import geopandas as gpd
import pandas as pd
import rasterio
import argparse
import yaml
import os, sys, inspect
from sklearn.cluster import KMeans

# the following allows us to import modules from within this file's parent folder
sys.path.insert(0, '.')

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('root')

if __name__ == "__main__":

    # Chronometer
    tic = time.time()
    logger.info('Starting...')

    # argument parser
    parser = argparse.ArgumentParser(description="The script filter the prediction results of the quarry project (STDL.proj-dqry)")
    parser.add_argument('config_file', type=str, help='input geojson path')
    args = parser.parse_args()

    logger.info(f"Using {args.config_file} as config file.")

    with open(args.config_file) as fp:
        cfg = yaml.load(fp, Loader=yaml.FullLoader)[os.path.basename(__file__)]

    INPUT = cfg['input']
    DEM = cfg['dem']
    SCORE = cfg['score']
    AREA = cfg['area']
    ELEVATION = cfg['elevation']
    DISTANCE = cfg['distance']
    OUTPUT = cfg['output']

    # import predictions GeoJSON
    input = gpd.read_file(INPUT)
    input = input.to_crs(2056)
    total = len(input)

    # Centroid of every prediction polygon
    centroids = gpd.GeoDataFrame()
    centroids.geometry = input.representative_point()

    # KMeans Unsupervised Learning
    centroids = pd.DataFrame({'x': centroids.geometry.x, 'y': centroids.geometry.y})
    k = int( ( len(input) / 3 ) + 1 )
    cluster = KMeans(n_clusters=k, algorithm = 'auto', random_state = 1)
    model = cluster.fit(centroids)
    labels = model.predict(centroids)
    print("KMeans algorithm computed with k = " + str(k))

    # Dissolve and Aggregate
    input['cluster'] = labels
    input = input.dissolve(by = 'cluster', aggfunc = 'max')
    total = len(input)

    # filter by score
    input = input[input['score'] > SCORE]
    sc = len(input)
    print(str(total - sc) + " predictions removed by score threshold")

    # Create empty data frame
    geo_merge = gpd.GeoDataFrame()

    # Merge close labels using buffer and unions
    geo_merge = input.buffer( +DISTANCE, resolution = 2 )
    geo_merge = geo_merge.geometry.unary_union
    geo_merge = gpd.GeoDataFrame(geometry=[geo_merge], crs = input.crs )
    geo_merge = geo_merge.explode(index_parts = True).reset_index(drop=True)
    geo_merge = geo_merge.buffer( -DISTANCE, resolution = 2 )
    td = len(geo_merge)
    print(str(sc - td) + " difference to clustered predictions after union")

    geo_merge = geo_merge[geo_merge.area > AREA]
    ta = len(geo_merge)
    print(str(td - ta) + " predictions removed by area threshold")

    r = rasterio.open(DEM)
    row, col = r.index(geo_merge.centroid.x, geo_merge.centroid.y)
    values = r.read(1)[row,col]
    geo_merge.elev = values
    geo_merge = geo_merge[geo_merge.elev < ELEVATION]
    te = len(geo_merge)
    print(str(ta - te) + " predictions removed by elevation threshold")

    print(str(te) + " predictions left")

    OUTPUT_completed = OUTPUT.replace('{score}', str(SCORE)).replace('0.', '0dot') \
         .replace('{area}', str(int(AREA)))\
         .replace('{elevation}', str(int(ELEVATION))) \
         .replace('{distance}', str(int(DISTANCE)))
    geo_merge.to_file(OUTPUT_completed, driver='GeoJSON')
