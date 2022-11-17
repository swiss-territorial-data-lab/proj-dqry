## Overview

This script allows to create a user-specified tiles that covers the polygons specified through a _shapefile_.

## Usage

The script is used based on a _shapefile_ containing one or more polygons :

    $ python3 tile-generator.py --labels [polygon_shapefile] 
                                --size [tile_size]
                                --output [output_directory]
                                [--x-shift/--y-shift [grid origin shift]]


The _size_ allows to specify the width (and height) of the tile to produce. This value is interpreted into perspective of the geographical coordinates of the labels _shapefile_.

The output directory is used to dump the _shapefile_ containing the computed tiles. The name of each file is generated according to the provided parameters.

The _shift_ value allows to translate the origin of the grid on which tiles are attached. The default value is zero. The shifts are specified in proportion of the specified tile _size_.

The following illustrations give examples of computed tiles of _50m_ size with two value of shifts using buildings as labels :

<p align="center">
<img src="../images/tile-example-1.webp?raw=true" width="35%">
&nbsp;
<img src="../images/tile-example-2.webp?raw=true" width="35%">
<br />
<i>Obtained tiles of 50m using building as labels</i>
</p>

This script can also be considered of low amount of large scale labels to obtain covering tiles as shown on the following examples :

<p align="center">
<img src="../images/tile-example-3.webp?raw=true" width="35%">
&nbsp;
<img src="../images/tile-example-4.webp?raw=true" width="35%">
<br />
<i>Tiled cover of a large area with 5000m and 2500m tiles</i>
</p>

The script also ensures that no duplicated tiles are exported in the output _shapefile_.
