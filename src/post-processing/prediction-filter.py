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

import geopandas as gpd
import pandas as pd
import rasterio
import argparse
from sklearn.cluster import KMeans

# argument parser
pm_argparse = argparse.ArgumentParser()

pm_argparse.add_argument( '-i', '--input',     type=str,                         help='input geojson path' )
pm_argparse.add_argument( '-d', '--dem',       type=str,                         help='input DEM path' )
pm_argparse.add_argument( '-o', '--output',    type=str,                         help='output geojson path' )
pm_argparse.add_argument( '-a', '--area' ,     type=float,     default = 1728.,  help='area threshold. Default to 1728' )
pm_argparse.add_argument( '-s', '--score',     type=float,     default = 0.96  ,  help='score threshold. Default to 0.96' )
pm_argparse.add_argument( '-e', '--elevation', type=float,     default = 1155. , help='elevation threshold. Default to 1155' )
pm_argparse.add_argument( '--distance',        type=float,     default = 8,      help="distance for union. Default to 8")

pm_args = pm_argparse.parse_args()

# import predictions GeoJSON
input = gpd.read_file(pm_args.input)
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
input = input[input['score'] > pm_args.score]
sc = len(input)
print(str(total - sc) + " predictions removed by score threshold")

# Create empty data frame
geo_merge = gpd.GeoDataFrame()

# Merge close labels using buffer and unions
geo_merge = input.buffer( +pm_args.distance, resolution = 2 )
geo_merge = geo_merge.geometry.unary_union
geo_merge = gpd.GeoDataFrame(geometry=[geo_merge], crs = input.crs )
geo_merge = geo_merge.explode(index_parts = True).reset_index(drop=True)
geo_merge = geo_merge.buffer( -pm_args.distance, resolution = 2 )
td = len(geo_merge)
print(str(sc - td) + " difference to clustered predictions after union")

geo_merge = geo_merge[geo_merge.area > pm_args.area]
ta = len(geo_merge)
print(str(td - ta) + " predictions removed by area threshold")

r = rasterio.open(pm_args.dem)
row, col = r.index(geo_merge.centroid.x, geo_merge.centroid.y)
values = r.read(1)[row,col]
geo_merge.elev = values
geo_merge = geo_merge[geo_merge.elev < pm_args.elevation]
te = len(geo_merge)
print(str(ta - te) + " predictions removed by elevation threshold")

print(str(te) + " predictions left")

geo_merge.to_file(pm_args.output, driver='GeoJSON')
