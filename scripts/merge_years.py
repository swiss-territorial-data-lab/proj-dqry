import argparse
import os
import sys
import time
import yaml

import fiona
import geopandas as gpd
import pandas as pd

sys.path.insert(0, '.')
import functions.misc as misc
from functions.constants import DONE_MSG

from loguru import logger
logger = misc.format_logger(logger)


if __name__ == "__main__":

    # Chronometer
    tic = time.time()
    logger.info('Starting...')

    # Argument and parameter specification
    parser = argparse.ArgumentParser(description="The script merge the detections obtained with the object-detector for each year")
    parser.add_argument('config_file', type=str, help='input geojson path')
    args = parser.parse_args()

    logger.info(f"Using {args.config_file} as config file.")

    with open(args.config_file) as fp:
        cfg = yaml.load(fp, Loader=yaml.FullLoader)[os.path.basename(__file__)]

    # Load input parameters
    WORKING_DIR = cfg['working_directory']
    YEARS = cfg['years']
    LAYER = cfg['layer']
    OVERWRITE = cfg['overwrite']
    FILE = cfg['file']

    os.chdir(WORKING_DIR)
    logger.info(f'Working directory set to {WORKING_DIR}')

    written_files = [] 
    detections_final_gdf = gpd.GeoDataFrame()

    feature = f'detections_MES.gpkg'

    if OVERWRITE:
        try:
            os.remove(feature)
            logger.warning(f'File {feature} exists and will be overwrite.')
        except OSError:
            pass

    for year in YEARS: 
        layer = LAYER.replace('{year}', str(year))
        path = str(year) + '/' + layer
        if os.path.exists(path): 
            detections_gdf = gpd.read_file(path)
            if FILE=='layers':
                detections_gdf.to_file(feature, layer=str(layer), driver='GPKG')
            elif FILE=='concatenate':
                detections_final_gdf = pd.concat([detections_final_gdf, detections_gdf], ignore_index=True)
        else:
            logger.warning(f'The file {path} does not exist. Moving on to the next year.')
            pass

    if FILE=='concatenate':
        detections_final_gdf.to_file(feature, driver='GPKG')

    logger.info("The following files were written. Let's check them out!")
    for written_file in written_files:
        logger.info(written_file)

    # Stop chronometer  
    toc = time.time()
    logger.info(f"Nothing left to be done: exiting. Elapsed time: {(toc-tic):.2f} seconds")

    sys.stderr.flush()