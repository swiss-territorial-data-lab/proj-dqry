
import logging
import logging.config
import time
import argparse
import yaml
import os, sys, inspect
import requests
import geopandas as gpd
import pandas as pd
import morecantile
import json
import numpy as np
import csv
from tqdm import tqdm
# import fct_misc
import re

from shapely.geometry import box
from shapely.geometry import Polygon

# the following allows us to import modules from within this file's parent folder
sys.path.insert(0, '.')

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('root')

if __name__ == "__main__":

    # Start chronometer
    tic = time.time()
    logger.info('Starting...')

    # Argument and parameter specification
    parser = argparse.ArgumentParser(description="Time machine script (STDL.proj-dqry)")
    parser.add_argument('config_file', type=str, help='Framework configuration file')
    args = parser.parse_args()

    logger.info(f"Using {args.config_file} as config file.")
 
    with open(args.config_file) as fp:
        cfg = yaml.load(fp, Loader=yaml.FullLoader)[os.path.basename(__file__)]

    # Load input parameters
    OUTPUT_DIR = cfg['output_folder']
    YEARS = cfg['years']
    YEAR1 = YEARS[0]
    YEAR2 = YEARS[-1]
    DETECTION1 = cfg['datasets']['detection']
    DETECTION1 = DETECTION1.replace('{year}', str(YEAR1))
    DETECTION2 = cfg['datasets']['detection']
    DETECTION2 = DETECTION2.replace('{year}', str(YEAR2))

    # Create an output directory in case it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    written_files = []

    # Load detections 
    logger.info('Read detection table...')
    d1 = gpd.read_file(DETECTION1)
    d2 = gpd.read_file(DETECTION2)
    # print(d1)
    # print(d2)
    
    logger.info('Compare spatial intersection between detection of 2 years...')
    print('Year 1 = ', YEAR1)
    print('Year 2 = ', YEAR2)
    # Polygon intesection
    intersection = gpd.sjoin(d1,d2,how='inner') 
    intersection1 = gpd.sjoin(d1,d2,how='left')
    intersection2 = gpd.sjoin(d1,d2,how='right')
    # print(intersection)
    # print(intersection1)
    # print(intersection2)
    feature_path = os.path.join(OUTPUT_DIR, 'intersection-inner')
    intersection.to_file(feature_path, driver='GeoJSON')
    written_files.append(feature_path) 
    feature_path = os.path.join(OUTPUT_DIR, 'intersection-left')
    intersection1.to_file(feature_path, driver='GeoJSON')
    written_files.append(feature_path) 
    feature_path = os.path.join(OUTPUT_DIR, 'intersection-right')
    intersection2.to_file(feature_path, driver='GeoJSON')
    written_files.append(feature_path) 


    unique_id_list = [] 
    exist_ds = [] 
    n = 0

    # Open a csv file to store the evolution of querry by year 
    csv_path = os.path.join(OUTPUT_DIR, 'intersection.csv')
    f = open(csv_path, 'w', encoding='UTF8', newline='')
    writer = csv.writer(f)  
    header = ('id_quarry', 'id_feature', 'year', 'status', 'score', 'area', 'centroid_x', 'centroid_y', 'geometry')
    writer.writerow(header)
    written_files.append(csv_path) 

    for row in d1.itertuples():
        id = row.id
        n = n + 1
        unique_id = n
        year = YEAR1
        status = 'exist'
        score = row.score
        area = row.area
        centroidx = row.centroidx
        centroidy = row.centroidy

        geom = row.geometry
      
        info = (unique_id, id, year, status, score, area, centroidx, centroidy, geom)
        exist_ds.append(info) 
        writer.writerow(info)

        unique_id_list.append(unique_id)
    nb1 = len(unique_id_list)

    df = gpd.GeoDataFrame(exist_ds) 
    intersection_exp = intersection.explode(index_parts=False,ignore_index=True)

    for row in intersection.itertuples():
        id = row.id_right
        id_search =  row.id_left
        for i in df.index:
            if df[1][i] == id_search: 
                unique_id = df[0][i]
        year = YEAR2
        status = 'evolution'
        score = row.score_right 
        area = row.area_right
        centroidx = row.centroidx_right 
        centroidy = row.centroidy_right
        geom = row.geometry

        info = (unique_id, id, year, status, score, area, centroidx, centroidy, geom)
        writer.writerow(info)
    
    nb12 = len(intersection)

    intersection2 = intersection2.fillna(value=0)
    n = unique_id_list[-1]
    for row in intersection2.itertuples():

        if row.index_left == 0:
            id = row.id_right
            n =  n + 1
            unique_id =  n
            year = YEAR2
            status = 'new'
            area = row.area_right 
            score = row.score_right
            centroidx = row.centroidx_right
            centroidy = row.centroidy_right 
            geom = row.geometry

            info = (unique_id, id, year, status, score, area, centroidx, centroidy, geom)
            writer.writerow(info)

            unique_id_list.append(unique_id) 
    nb2 = len(unique_id_list) - nb1

    logger.info("Quarry detection comparison has been performed")
    print('- Quarry detection in', YEAR1, ' = ', nb1)
    print('- New quarry detection in', YEAR2, ' = ', nb2)
    print('- Quarry detected over the 2 years', nb12)

    print()
    logger.info("The following files were written. Let's check them out!")
    for written_file in written_files:
        logger.info(written_file)
    print()

    # Stop chronometer  
    toc = time.time()
    logger.info(f"Nothing left to be done: exiting. Elapsed time: {(toc-tic):.2f} seconds")

    sys.stderr.flush()