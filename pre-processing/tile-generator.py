#!/bin/python
# -*- coding: utf-8 -*-

#  tile-generator
#
#      Nils Hamel - nils.hamel@alumni.epfl.ch
#      Huriel Reichel
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

import argparse
import os, sys
import math
import geopandas as gpd
from shapely.geometry import Polygon, LineString, Point

if __name__ == "__main__":

    # Argument and parameter specification
    parser = argparse.ArgumentParser(description="Tile generator tool (STDL)")
    parser.add_argument('--labels' , type=str  , help='Label geographic file')
    parser.add_argument('--size'   , type=int  , help='Tile size in meters' )
    parser.add_argument('--x-shift', type=float, help='Grid shift factor', default=0.)
    parser.add_argument('--y-shift', type=float, help='Grid shift factor', default=0.)
    parser.add_argument('--output' , type=str  , help='Output directory', default='.')
    args = parser.parse_args()

    # Import labels
    geo_data = gpd.read_file( args.labels )

    shift_x = int(+round( args.size * args.x_shift ))
    shift_y = int(+round( args.size * args.y_shift ))

    # Prevent duplicated tiles
    dupl = []

    # Bootstrap tiles
    geo_tiling = gpd.GeoDataFrame()

    # Indexation
    indexation = 0

    # Parsing label geometries
    for index, row in geo_data.iterrows():

        # Extract geometry vertex
        bbox = row['geometry'].bounds

        # round bounding box
        bbox_rlx = math.floor( ( bbox[0] - shift_x ) / args.size ) * args.size + shift_x
        bbox_rly = math.floor( ( bbox[1] - shift_y ) / args.size ) * args.size + shift_y
        bbox_rhx = math.ceil ( ( bbox[2] - shift_x ) / args.size ) * args.size + shift_x
        bbox_rhy = math.ceil ( ( bbox[3] - shift_y ) / args.size ) * args.size + shift_y

        # create grid over the rounded bounding box
        for x in range( bbox_rlx, bbox_rhx, args.size ):

            # create grid over the rounded bounding box
            for y in range( bbox_rly, bbox_rhy, args.size ):

                # compute tile lower corner
                g_x = x;
                g_y = y;

                # Prevent tile duplication
                if ( g_x, g_y ) not in dupl:

                    # Add tile definition
                    geo_tiling.loc[indexation,'geometry'] = Polygon( [ ( g_x, g_y ), ( g_x + args.size, g_y ), ( g_x + args.size, g_y + args.size ), ( g_x, g_y + args.size ), ( g_x, g_y ) ] )

                    # Update index
                    indexation = indexation + 1

                    # Add tile to duplication stack
                    dupl.append( ( g_x, g_y ) )

    # Assign CRS to tiling dataframe
    geo_tiling = geo_tiling.set_crs( crs = geo_data.crs )

    # Remove empty tile, i.e. tiles that are not part of the label(s) mapping
    geo_tiling = gpd.sjoin( geo_tiling, geo_data, how="inner" )

    # Drop dublicated tiles
    geo_tiling.drop_duplicates(subset=['geometry'],inplace=True)

    # Filtering columns on tiling dataframe
    geo_tiling = geo_tiling.loc[:, ['geometry']]

    # Export tiles definitions
    geo_tiling.to_file( os.path.join( args.output, f'tiles_{args.size}_{shift_x}_{shift_y}.shp'))


