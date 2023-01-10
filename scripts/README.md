## Overview

Following the scripts and configuration files properties in `proj-dqry` are presented in detailed.


# 1. `prepare_data.py`

The script `prepare_data.py` allows to prepare the input dataset to be processed by the `object-detector` workflow. The caracteristics of the tiles are defined by the script to set the tiles parameters for the tiling service request. _XYZ_ connector is used to fetch images with a Web Map Tiling Service _wmts_. _wmts_ allows to request images for a given year and provides base tile of 256 px that can be combined according to the given zoom level _z_. The zoom level will act on the tiles size (and tiles number) and on the pixel resolution (z15: 3.2 m/px, z16: 1.6 m/px, z17: 0.8 m/px and z18: 0.4 m/px). _x_ and _y_ coordinates of tiles on a grid are defined for the given AOI and the zoom level. This script can be used to prepare the tiles of the 'Training and evaluation' workflow and the 'Prediction' workflow. Therefore it works along the config files `config-trne.yaml` and `config-prd.yaml`.

Input ou output paths of the config files must be adapted if necessary. The `prepare_data.py` section of the _yaml_ configuration file is expected as follow:

    prepare_data.py:
        srs: "EPSG:3857"
        datasets:
            labels_shapefile: ../input/input-trne/[AOI_Shapefile]
      output_folder: ../output/output-prd
      zoom_level: [z]
 
The **srs** key provides the working geographical frame to ensure all the input data are compatible together. Specify the **zoom_level**. Set the path to the desired label shapefile (AOI) (create a new folder /proj-dqry/input/input-prd/ to the project). 

For the quarries example, the **labels_shapefile** corresponds to the tiles intersecting labels (Ground Truth) for the 'Training and evaluation' workflow: 

    [Label_Shapefile] = tlm-hr-trn-topo.shp
    
and to the tiles covering the desired AOI (_i.e._ it can be the whole Switzerland or part of it such as the footprint where SWISSIMAGE has been acquired for a given year) for the 'Prediction' workflow:

    [Label_Shapefile] = swissimage_footprint_[year].shp


The script can be run by exectuting the following command:

    $ python3  <dir_path>/scripts/prepare_data.py <dir_path>/config/config-trne.yaml

or 

    $ python3  <dir_path>/scripts/prepare_data.py <dir_path>/config/config-prd.yaml

for 'Training and evaluation' workflow and 'Prediction' respectively.

The outputs are `tiles.geojson` files corresponding to tiles polygons obtained for the given AOI and `labels.geojson` corresponding the input labels polygons. 


# 2. `prediction_filter.py`

The object detection output (**oth_predictions.geojson**) obtained via the `object-detector` scripts needs to be filtered to discard false detections and improve the aesthetic of the polygons (merge polygons belonging to a single quarry). The script `prediction_filter.py` allows to extract the prediction out of the detector _geojson_ based on a series of provided threshold values. It works along with the config file `config-prd.yaml` 

The first step going on is a clustering of the centroids of every prediction polygon. This is used as a way to maintain the scores for a further unary union of the polygons, that then uses the cluster value assigned as an aggregation method. This allows the removal of lower scores in a smart way, _i.e._, by maintaining the integrity of the final polygon. Then, predictions are filtered based on the score. Polygons that are not overlapping but are close in position are merged together. Then, based on the polygons' areas value, the smaller to the threshold value are discarded. Following, with the input of a Digital Elevation Model an elevation thresholding is processed. Finally, the predictions score is computed again taking into account of the merged polygons scores. The results of the filtering/merging process are saved in a _geojson_ file

The following images give an illustration of the extraction process showing the original and filtered predictions :

<p align="center">
<img src="../images/before.png?raw=true" width="40%">
&nbsp;
<img src="../images/after.png?raw=true" width="40%">
<br />
<i>Left : Detector predictions - Right : Threshold filtering results</i>
</p>

The value of the filtering threshold is usually obtained by the training validation set analysis or other more advanced methods.

Input ou output paths of the config file must be adapted if necessary. The script expects as input a prediction _geojson_ (`oth_prediction.geojson` obtained with `assess_prediction.py` of `object-detector`) file with all geometries containing a _score_ value normalised in _[0,1]_. The `prediction_filter.py` section of the _yaml_ configuration file is expected as follow:

    prediction_filter.py:
        input: ../output/output-prd/oth_predictions.geojson 
        dem: ../input/DEM/swiss-srtm.tif 
        elevation: [THRESHOLD VALUE]   
        score: [THRESHOLD VALUE]
        distance: [THRESHOLD VALUE] 
        area: [THRESHOLD VALUE] 
        output: ../output/output-prd/

-**input**: indicate path to the input geojson file that needs to be filtered, _i.e._ `oth_predictions.geojson` 

-**dem**: indicate the path to the DEM of Switzerland. A SRTM derived product is used and can be found in the STDL kDrive. A threshold elevation is used to discard detection above the given value. 

-**elevation**: altitude above which prediction are discard. Indeed 1st tests have shown numerous false detection due to snow cover area (reflectance value close to bedrock reflectance) or mountain bedrock exposure. By default the threshold elevation has been set to 1155.0 m.

-**score**: each polygon comes with a confidence score given by the prediction algorithm. Polygons with low scores can be discarded. By default the value is set to 0.96.

-**distance**: two polygons that are close to each other can be considered to belong to the same quarry. Those polygons can be merged into a single one. By default the buffer value is set to 8 m.

-**area**: small area polygons can be discarded assuming a quarry has a minimal area. The default value is set to 1728 m2.

-**output**: provide the path of the filtered polygons shapefile with prediction score preserved: `oth_prediction_filter_year-{year}.geojson` 

The script can be run by exectuting the following command:

   $ python3 <dir_path>/scripts/prediction-filter.py <dir_path>/config/config-prd.yaml


# 3. `detection_monitoring.py`

The script `detection_monitoring.py` has been developped in order to identified and track an object between different year datasets. It has been developped in the scope of quarries monitoring and works along with the config file `config-dm.yaml`. 

The script identify the position of polygons between different years in order to identify single object in several datasets. All the detection shape are added to a single dataframe. A union function is applied in order to merge overlapping polygons. Those polygons (single and merged) are added to a new dataframe with a unique ID attributed to each. This dataframe is then spatially (_sjoin_) compared to the initial dataframe containing all the polygons by year. The unique ID of the polygons of the second dataframe is then attributed to the intesecting polygons of the first dataframe. Therefore, overlapping polygons between years are assumed to described the same object and received the same unique ID allowing to track the object over years.

<p align="center">
<img src="../images/quarry_monitoring_strategy.png?raw=true" width="100%">
<br />
<i>Schematic representation of the object monitoring strategy.</i>
</p>

The `detection_monitoring.py` section of the _yaml_ configuration file is expected as follow:

        years: [YEAR1, YEAR2, ...]      # Provide a list of years used for detection
        datasets:
            detection: ../output/output-prd/oth_prediction_filter_year-{year}.geojson  # Final detection file, produced by prediction_filter.py 
        output_folder: ../output/output-dm
  
Input ou output paths of the config file must be adapted if necessary. The script takes as input a _geojson_ file. In the quarry monitoring case, **oth_prediction_filter_year-{year}.geojson** files produced with the script `prediction_filter.py` of the `object-detector` for different years are used. The list of years _YEARx_ required for the object monitoring must be specified.

The script can be run by exectuting the following command:

    $ python3  <dir_path>/scripts/detection_monitoring.py <dir_path>/config/config-dm.yaml

The outputs are a _geojson_ and _csv_ (**quarry_time**) files saving predictions over years with their caracteristics (ID_object, ID_feature, year, score, area, geometry). 

# 4. `plots.py`

Script to draw basic plots is provided with `plots.py` and works along with the config file `config-dm.yaml` 

The `plots.py` section of the _yaml_ configuration file is expected as follow:

    object_id: [Q1, Q2, ...]      # Provide a list of years used for detection
    plots: ['area-year'] 
    datasets:
        detection: ../output/output-dm/quarry_times.geojson  # Final detection file, produced by prediction_filter.py 
    output_folder: ../output/output-dm/plots

Input ou output paths must be adapted if necessary. The script takes as input a **`**quarry_times.geojson** file produced with the script `detection_monitoring.py`. The list of **object_id** _Qx_ must be specified and the type of plot as well. So far only **area-year** plot is available. Additionnal type of plots can be added in the future.

The script can be run by exectuting the following command:

    $ python3  <dir_path>/scripts/prediction-filter.py <dir_path>/config/config-dm.yaml

Plot(s) will be produced in _png_ format