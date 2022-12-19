
#!/bin/python
# -*- coding: utf-8 -*-

#  Proj quarry detection and time machine
#
#      Nils Hamel - nils.hamel@alumni.epfl.ch
#      Huriel Reichel
#      Clemence Herny 
#      Shanci Li
#      Alessandro Cerioni 
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
#
# 
################################################################
#  Script used to plot and visualize quarry data trough times 
#  Inputs are defined in config-dm.yaml
 

import os, sys
import logging
import logging.config
import argparse
import yaml
import geopandas as gpd
import matplotlib.pyplot as plt

# the following allows us to import modules from within this file's parent folder
sys.path.insert(0, '.')

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('root')

if __name__ == "__main__":

    # Start chronometer
    logger.info('Starting...')

    # Argument and parameter specification
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', type=str, help='Framework configuration file')
    args = parser.parse_args()
    logger.info(f"Using {args.config_file} as config file.")

    with open(args.config_file) as fp:
        cfg = yaml.load(fp, Loader=yaml.FullLoader)[os.path.basename(__file__)]

    # Load input parameters
    DETECTION = cfg['datasets']['detection']
    QUARRIES = sorted(cfg['quarries_id'])
    OUTPUT_DIR = cfg['output_folder']
    PLOTS = cfg['plots']

    # Create an output directory in case it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Load prediction 
    gdf = gpd.read_file(DETECTION)

    for PLOT in PLOTS:
        
        # Plot the quarry area vs time 
        if PLOT == 'area-year':
            logger.info(f"Plot {PLOT}")
            for QUARRY in QUARRIES:
                x = gdf.loc[gdf["id_quarry"] == QUARRY,["year"]]
                y = gdf.loc[gdf["id_quarry"] == QUARRY,["area"]]
                id = QUARRY
                
                plt.scatter(x, y, label=id)
                plt.plot(x, y, linestyle="-")
                plt.xlabel("Year")
                plt.ylabel(r"Area (m$^2$)")
                plt.ticklabel_format(axis='y', style='sci')
                plt.legend(title='Quarry ID')

            plot_path = os.path.join(OUTPUT_DIR, 'quarry_area-year.png')
            plt.savefig(plot_path)
            plt.show()