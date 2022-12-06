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

    # Load input parameters
    YEAR = cfg['year']
    INPUT = cfg['input']
    DEM = cfg['dem']
    SCORE = cfg['score']
    AREA = cfg['area']
    ELEVATION = cfg['elevation']
    DISTANCE = cfg['distance']
    OUTPUT = cfg['output']

    written_files = [] 

    # import predictions GeoJSON
    INPUT_completed = INPUT.replace('{year}', str(YEAR))
    input = gpd.read_file(INPUT_completed)
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
    # print(input)
    sc = len(input)
    print(str(total - sc) + " predictions removed by score threshold")
    geo_input = gpd.GeoDataFrame(input)
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

    # Discard polygons with area under the threshold 
    geo_merge = geo_merge[geo_merge.area > AREA]
    ta = len(geo_merge)
    print(str(td - ta) + " predictions removed by area threshold")

    # Discard polygons detected above the threshold elevalation 
    r = rasterio.open(DEM)
    row, col = r.index(geo_merge.centroid.x, geo_merge.centroid.y)
    values = r.read(1)[row,col]
    geo_merge.elev = values
    geo_merge = geo_merge[geo_merge.elev < ELEVATION]
    te = len(geo_merge)
    print(str(ta - te) + " predictions removed by elevation threshold")

    print(str(te) + " predictions left")

    # Preparation of a geo df 
    data = {'id': geo_merge.index,'area': geo_merge.area, 'centroid x': geo_merge.centroid.x, 'centroid y': geo_merge.centroid.y, 'geometry': geo_merge}
    geo_tmp = gpd.GeoDataFrame(data, crs=input.crs)

    # Get the averaged prediction score of the merge polygons  
    intersection = gpd.sjoin(geo_tmp, input, how='inner')
    intersection['id'] = intersection.index
    score_final=intersection.groupby(['id']).mean()

    # Formatting the final geo df 
    data = {'id': geo_merge.index,'score': score_final['score'] , 'area': geo_merge.area, 'centroid x': geo_merge.centroid.x, 'centroid y': geo_merge.centroid.y, 'geometry': geo_merge}
    geo_final = gpd.GeoDataFrame(data, crs=input.crs)

    OUTPUT_completed = OUTPUT.replace('{year}', str(YEAR)) \
         .replace('{score}', str(SCORE)).replace('0.', '0dot') \
         .replace('{area}', str(int(AREA)))\
         .replace('{elevation}', str(int(ELEVATION))) \
         .replace('{distance}', str(int(DISTANCE)))
    geo_final.to_file(OUTPUT_completed, driver='GeoJSON')
    written_files.append(OUTPUT_completed) 

    print()
    logger.info("The following files were written. Let's check them out!")
    for written_file in written_files:
        logger.info(written_file)
    print()

    # Stop chronometer  
    toc = time.time()
    logger.info(f"Nothing left to be done: exiting. Elapsed time: {(toc-tic):.2f} seconds")

    sys.stderr.flush()
