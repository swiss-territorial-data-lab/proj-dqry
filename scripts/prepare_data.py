#!/bin/python
# -*- coding: utf-8 -*-

#  Detector interface
#
#      Nils Hamel - nils.hamel@alumni.epfl.ch
#      Huriel Reichel
#      Copyright (c) 2020 Republic and Canton of Geneva
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
import argparse
import yaml
import os, sys
import geopandas as gpd
import csv

from shapely.geometry import Polygon

def compose_tiles( csv_row, tile_split ):

    """
    Overview :

    This function is responsible of transforming the provided bounding box,
    through the CSV row (dict), into rectangular tiles covering the bounding
    box.

    The amount of tile is deduced from the split value, which gives, when
    squared, the amount of computed tiles. The tiles are Polygon returned
    through a list.

    Parameter :

    csv_row : DictReader row

        CSV row giving the bounding box (x_min, y_min, x_max, y_max).

    tile_split : integer value

        Bounding box split value. Providing one produce one tile covering the
        bounding box. Providing two lead to four equal tiles covering the
        bounding box.

    Return :

    List : Shaply polygon list

        Return the tiles geometry through a list of polygons.
    """

    # Compose bounding box origin
    org_x = float( csv_row['x_min'] )
    org_y = float( csv_row['y_min'] )

    # Compute tiles edge
    egde_x = ( float( csv_row['x_max'] ) - float( csv_row['x_min'] ) ) / tile_split
    egde_y = ( float( csv_row['y_max'] ) - float( csv_row['y_min'] ) ) / tile_split

    # Initialise polygon list
    poly_list=[]

    # Parsing x-axis
    for x in range( tile_split ):

        # Parsing y-axis
        for y in range( tile_split ):

            # Compose and append polygon
            poly_list.append( Polygon( [

                ( org_x + egde_x * ( x     ), org_y + egde_y * ( y     ) ),
                ( org_x + egde_x * ( x + 1 ), org_y + egde_y * ( y     ) ),
                ( org_x + egde_x * ( x + 1 ), org_y + egde_y * ( y + 1 ) ),
                ( org_x + egde_x * ( x     ), org_y + egde_y * ( y + 1 ) ),
                ( org_x + egde_x * ( x     ), org_y + egde_y * ( y     ) )

            ] ) )

    # Return polygon list
    return poly_list

if __name__ == "__main__":

    # Argument and parameter specification
    parser = argparse.ArgumentParser(description="Front-end for data preparation in the context of thermal panels detection (STDL.PROJ-TPNL)")
    parser.add_argument('--config', type=str, help='Framework configuration file')
    parser.add_argument('--logger', type=str, help='Log configuration file', default='logging.conf')
    args = parser.parse_args()

    # Section : Preliminar
    #
    # This section checks the configuration files and inputs the yaml file
    # containing the configuration.

    # Chronometer
    tic = time.time()

    try:

        # Logger configuration used to format script output
        logging.config.fileConfig('logging.conf')
        logger = logging.getLogger('root')

    except:

        # Display message & abort
        print('Unable to access logger configuration file')
        sys.stderr.flush()
        sys.exit(1)
   
    try:
        print(args.config)
        # Import configuration file (YAML file)
        with open(args.config) as fp:
            cfg = yaml.load(fp, Loader=yaml.FullLoader)[os.path.basename(__file__)]
            print(os.path.basename(__file__))
        # Logging info
        logger.info(f"Using {args.config} as config file.")
        
    except:
    
        # Logging info & abort
        logger.error(f"Unable to access {args.config} configuration file")
        sys.stderr.flush()
        sys.exit(1)

    # Check YAML key
    if 'output_folder' in cfg:

        # Create output directory if missing
        if not os.path.exists(cfg['output_folder']):

            # Create directory
            print(cfg['output_folder'])
            os.makedirs(cfg['output_folder'])

            # Logging info
            logger.info(f"Created output directory")

    else:

        # Logging info & abort
        logger.error("Key <output_folder> missing")
        sys.stderr.flush()
        sys.exit(1)

    # Check YAML key
    if not 'srs' in cfg:

        # Logging info & abort
        logger.error("Key <srs> missing")
        sys.stderr.flush()
        sys.exit(1)

    # Check YAML key
    if not 'label' in cfg:

        # Logging info & abort
        logger.error("Missing label key")
        sys.stderr.flush()
        sys.exit(1)

    # Check YAML key
    if not 'tiling' in cfg:

        # Logging info & abort
        logger.error("Missing tiling key")
        sys.stderr.flush()
        sys.exit(1)

    # Section : Label
    #
    # This section is dedicated to labels importation from the specified source
    # geographic file.

    # Check YAML key
    if 'shapefile' in cfg['label']:

        # Import label geometries from shapefile
        geo_label = gpd.read_file( cfg['label']['shapefile'] )

        # Logging info
        logger.info(f"Read from \"{cfg['label']['shapefile']}\" :")
        logger.info(f"\t{len(geo_label)} label(s) imported")

    else:

        # Logging info & abort
        logger.error("Missing source in label")
        sys.stderr.flush()
        sys.exit(1)

    # Match label and tiling coordinate frame
    geo_label = geo_label.to_crs( cfg['srs'] )

    # Logging info
    logger.info(f"SRS {cfg['srs']} forced for label(s)")

    # Section : Tiles
    #
    # This section is dedicated to tile definition importation and process
    # according to the specified source.

    # Check YAML key
    if 'csv' in cfg['tiling']:

        # Check YAML key
        if not 'split' in cfg['tiling']:

            # Logging info & abort
            logger.error("Missing split key in tiling")
            sys.stderr.flush()
            sys.exit(1)

        # Initialise tiling geometry
        geo_tiling = gpd.GeoDataFrame()

        # Import CSV data for tiling computation
        with open( cfg['tiling']['csv'], newline='') as csvfile:

            # Read CSV by dictionnary
            csvdata = csv.DictReader(csvfile, delimiter=',')

            # Initialise index
            index=0

            # Iterate over CSV rows
            for row in csvdata:

                # Compute polygon list
                poly_list = compose_tiles( row, cfg['tiling']['split'] )

                # Parsing polygon list
                for poly in poly_list:

                    # Retreive polygon bounding box
                    poly_bbox = poly.bounds

                    # Compose tile synthetic coordinates
                    syn_x = int( poly_bbox[0] )
                    syn_y = int( poly_bbox[1] )

                    # Add tile geometry
                    geo_tiling.loc[index,'geometry'] = poly

                    # Add tile required columns
                    geo_tiling.loc[index,'id'   ] = f"({syn_x}, {syn_y}, 0)"
                    geo_tiling.loc[index,'title'] = f"XYZ tile ({syn_x}, {syn_y}, 0)"

                    # Update index
                    index = index + 1

        # Logging info
        logger.info(f"Read from \"{cfg['tiling']['csv']}\" :")
        logger.info(f"\t{index} tile(s) imported")

    elif 'shapefile' in cfg['tiling']:

        # Import tiles definition
        geo_tiling = gpd.read_file( cfg['tiling']['shapefile'] )

        # Remove all columns #
        geo_tiling = geo_tiling.loc[:, ['geometry']]

        # Iterates over geometries
        for index in range(len(geo_tiling.index)):

            # Get bounding box
            poly_bbox = geo_tiling.loc[index,'geometry'].bounds

            # Compose tile synthetic coordinates
            syn_x = int( poly_bbox[0] )
            syn_y = int( poly_bbox[1] )

            # Add tile required columns
            geo_tiling.loc[index,'id'   ] = f"({syn_x}, {syn_y}, 0)"
            geo_tiling.loc[index,'title'] = f"XYZ tile ({syn_x}, {syn_y}, 0)"

        # Logging info
        logger.info(f"Read from \"{cfg['tiling']['shapefile']}\" :")
        logger.info(f"\t{len(geo_tiling.index)} tile(s) imported")

    else:

        # Logging info & abort
        logger.error("Missing source in tiling")
        sys.stderr.flush()
        sys.exit(1)

    # set geographical frame of tiling geometry
    geo_tiling = geo_tiling.to_crs( crs = cfg['srs'] )

    # Logging info
    logger.info(f"SRS {cfg['srs']} forced for tile(s)")

    # Duplicate geodataframe (be sure to work on a copy, the original being exported at the end)
    geo_label_shrink = geo_label.copy()

    # Section : Filter and export
    #
    # This section is dedicated to tile and label linked process and result
    # exportation in the output directory.

    # Note : Shrink label geometries
    #
    # As a spatial "inner" join is made considering tiles and labels to only
    # consider labelled tiles, shrinking the labels a bit allows to avoid
    # keeping tiles that are only "touched" by a label but without a proper and
    # relevant intersection.
    geo_label_shrink['geometry'] = geo_label_shrink['geometry'].scale( xfact=0.9, yfact=0.9, origin='centroid' )

    # Spatial join based on label to eliminate empty tiles (keeping only tiles with at least one clear label)
    geo_tiling = gpd.sjoin(geo_tiling, geo_label_shrink, how="inner")

    # Drop spatial join duplicated geometries based on 'id' column
    geo_tiling.drop_duplicates(subset=['id'],inplace=True)

    # Logging info
    logger.info(f"Removed empty and quasi-empty tiles :")
    logger.info(f"\t{len(geo_tiling)} tile(s) remaining")

    # Filtering columns on label dataframe
    geo_label = geo_label.loc[:, ['geometry']]

    # Filtering columns on tiling dataframe
    geo_tiling = geo_tiling.loc[:, ['geometry', 'id', 'title']]

    # Export labels into geojson, forcing epsg:4326 standard
    geo_label.to_crs(epsg='4326').to_file(os.path.join(cfg['output_folder'],'labels.geojson'),driver='GeoJSON')

    # Export tiles into geojson, forcing epsg:4326 standard
    geo_tiling.to_crs(epsg='4326').to_file(os.path.join(cfg['output_folder'],'tiles.geojson'),driver='GeoJSON')

    # logging info    
    logger.info(f"Written files in output directory :")
    logger.info(f"\tlabels.geojson")
    logger.info(f"\ttiles.geojson")

    # Chronometer
    toc = time.time()

    # Display summary
    logger.info(f"Completed in {(toc-tic):.2f} seconds")

    # Flush error output
    sys.stderr.flush()

