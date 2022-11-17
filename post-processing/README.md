## Overview

This script allows to extract the prediction out of the detector _GeoJSON_ based on a series of provided threshold values.

The first step going on is a clustering of the centroids of every prediction polygon. This is used as a way to maintain the scores for a further unary union of the polygons, that then uses the cluster value assigned as an aggregation method. This allows the removal of lower scores in a smarter way, *i.e.*, by maintaining the integrity of the final polygon. Then, predictions are filtered based on the polygons' areas value. Following, with the input of a Digital Elevation Model an elevation thresholding is processed. Finally, the predictions are filtered based on score. This score is calculated as the maximum score obtained from the polygons intersecting the merged polygons.

It is important to mention that this sequence was modified on the 26th of November 2021. Predictions weren't once aesthetic, especially with smaller tiles. As the old procedure was used for the delivery of results before, it is for now maintaned in the past-filter branch of this repository.
## Usage

The script expects then a prediction _GeoJSON_ file with all geometries containing a _score_ value normalised in _[0,1]_ and the filtering threshold :

    $ python prediction-thresholding.py --input [prediction GeoJSON]
    				         --dem [digital elevation model GeoTiff]
                                    --score [threshold value]
                                    --area [threshold value]
                                    --distance [threshold value]
                                    --output [Output GeoJSON]

The results of the filtering/merging are dumped in the provided output _GeoJSON_ (destination is replaced in case it exists).

The following images give an illustration of the extraction process showing the original and filtered predictions :

<p align="center">
<img src="doc/before.png?raw=true" width="35%">
&nbsp;
<img src="doc/after.png?raw=true" width="35%">
<br />
<i>Left : Detector predictions - Right : Threshold filtering results</i>
</p>

The value of the filtering threshold is usually obtained by the training validation set analysis or other more advanced methods.
