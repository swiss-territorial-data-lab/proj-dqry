## Overview

Following the scripts and configuration files properties contained in `proj-dqry` are presented in detailed.


## 1. `prepare_data.py`

The script `prepare_data.py` allows the user to prepare the input dataset to be processed by the `object-detector` workflow. The characteristics of the tiles are defined by the script to set the tiles parameters for the tiling service request. _XYZ_ connector is used to fetch images with a Web Map Tiling Service _wmts_. _wmts_ allows to request images for a given year and provides a base tile of 256 px that can be combined according to the given zoom level _z_. The zoom level will act on the tiles size (and tiles number) and on the pixel resolution (z15: 3.2 m/px, z16: 1.6 m/px, z17: 0.8 m/px and z18: 0.4 m/px for SWISSMAGE 10 cm). _x_ and _y_ coordinates of tiles on a grid are defined for the given AOI and the zoom level. This script can be used to prepare the tiles of the 'Training and evaluation' workflow and the 'Prediction' workflow. It works along the config files `config-trne.yaml` and `config-prd.yaml`.

Input and output paths of the config files must be adapted if necessary. The `prepare_data.py` section of the _yaml_ configuration file is expected as follow:

    prepare_data.py:
        srs: [crs] 
        datasets:
            labels_shapefile: ../input/input-trne/[AOI_Shapefile]
      output_folder: ../output/output-prd
      zoom_level: [z]
 
The **srs** key provides the working geographical frame to ensure all the input data are compatible together. Specify the **zoom_level**. Set the path to the desired label shapefile (AOI) (create a new folder /proj-dqry/input/input-prd/ to the project). 

For the quarry case, the **labels_shapefile** corresponds to the tiles intersecting labels (Ground Truth) for the 'Training and evaluation' workflow: 

    [Label_Shapefile] = tlm-hr-trn-topo.shp
    
and to the tiles covering the desired AOI (_i.e._ it can be the whole Switzerland or part of it such as the footprint where SWISSIMAGE has been acquired for a given year) for the 'Prediction' workflow:

    [Label_Shapefile] = swissimage_footprint_[year].shp


The script can be run by exectuting the following command:

    $ python3  <dir_path>/scripts/prepare_data.py <dir_path>/config/config-trne.yaml

or 

    $ python3  <dir_path>/scripts/prepare_data.py <dir_path>/config/config-prd.yaml

for 'Training and evaluation' workflow and 'Prediction' respectively.

The outputs are `tiles.geojson` files corresponding to tiles polygons obtained for the given AOI and `labels.geojson` corresponding the input labels polygons. 

<p align="center">
<img src="../images/tiles_example.png?raw=true" width="100%">
<br />
<i>Example of tiles obtained during the 'Training and evaluation' at zoom level 16 and zoom level 17.</i>
</p>



## 2. `prediction_filter.py`

The object detection output (**oth_predictions.geojson**) obtained via the `object-detector` scripts needs to be filtered to discard false detections and improve the aesthetic of the polygons (merge polygons belonging to a single quarry). The script `prediction_filter.py` allows to extract the prediction out of the detector _geojson_ based on a series of provided threshold values. It works along with the config file `config-prd.yaml` 

First, with the input of a Digital Elevation Model, an elevation threshold is applied above what prediction are discarded (predictions at altitude 0 are also discarded because they are located outside of DEM limits). Following, an alogrithm (KMeans Unsupervised Learning) is applied to cluster polygons according to their centroids. This is used as a way to maintain the scores for a further unary union of the polygons, that then uses the cluster value assigned as an aggregation method. This allows the removal of lower scores in a smart way, _i.e._, by maintaining the integrity of the final polygon. Be careful to keep the threshold score value low while running `make_prediction.py` to obtain better results. Then, predictions are filtered based on the score. Polygons that are not overlapping but are close in position are merged together. Based on the polygons' area value, the smaller to the threshold value is discarded. Finally, an averaged predicted score is computed again taking into account the merged polygons scores. The results of the filtering/merging process are saved in a _geojson_ file.

The following images give an illustration of the extraction process showing the original and filtered predictions :

<p align="center">
<img src="../images/prediction_filter_before.png?raw=true" width="40%">
&nbsp;
<img src="../images/prediction_filter_after.png?raw=true" width="40%">
<br />
<i>Left : Detector predictions - Right : Threshold filtering results</i>
</p>

The values of the filtering thresholds are usually obtained by analysing the predictions output.

Input and output paths of the config file must be adapted if necessary. The script expects as input a prediction _geojson_ (`oth_prediction.geojson` obtained with `assess_prediction.py` of `object-detector`) file with all geometries containing a _score_ value normalised in _[0,1]_. The `prediction_filter.py` section of the _yaml_ configuration file is expected as follow:

    prediction_filter.py:
        year:[YEAR] 
        input: ../output/output-prd/oth_predictions.geojson 
        dem: ../input/DEM/swiss-srtm.tif 
        elevation: [THRESHOLD VALUE]   
        score: [THRESHOLD VALUE]
        distance: [THRESHOLD VALUE] 
        area: [THRESHOLD VALUE] 
        output: ../output/output-prd/

-**year**: year of the dataset used as input for filtering

-**input**: indicate path to the input geojson file that needs to be filtered, _i.e._ `oth_predictions.geojson`

-**dem**: indicate the path to the DEM of Switzerland. A SRTM derived product is used and can be found in the STDL kDrive. A threshold elevation is used to discard detection above the given value.

-**elevation**: altitude above which predictions are discarded. Indeed 1st tests have shown numerous false detection due to snow cover area (reflectance value close to bedrock reflectance) or mountain bedrock exposure that are mainly observed in altitude.. By default the threshold elevation has been set to 1200.0 m.

-**score**: each polygon comes with a confidence score given by the prediction algorithm. Polygons with low scores can be discarded. By default the value is set to 0.95.

-**distance**: two polygons that are close to each other can be considered to belong to the same quarry. Those polygons can be merged into a single one. By default the buffer value is set to 8 m.

-**area**: small area polygons can be discarded assuming a quarry has a minimal area. The default value is set to 2000 m2.

-**output**: provide the path of the filtered polygons shapefile with prediction score preserved. The output file name will be formated as: `oth_prediction_filter_year-{year}_score-{score}_elevation-{elevation}_distance-{distance}_area-{area}.geojson`.


The script can be run by executing the following command:

    $ python3 <dir_path>/scripts/prediction-filter.py <dir_path>/config/config-prd.yaml


## 3. `detection_monitoring.py`

The script `detection_monitoring.py` has been developed in order to identify and track an object between different year datasets. It has been developed in the scope of the quarries monitoring project and works along with the config file `config-dm.yaml`.

The script identifies the position of polygons between different years in order to identify a single object in several datasets. All the detection shapes are added to a single dataframe. A union function is applied in order to merge overlapping polygons. Those polygons (single and merged) are added to a new dataframe with a unique ID attributed to each. This dataframe is then spatially (_sjoin_) compared to the initial dataframe containing all the polygons by year. The unique ID of the polygons of the second dataframe is then attributed to the intersecting polygons of the first dataframe. Therefore, overlapping polygons between years are assumed to describe the same object and receive the same unique ID allowing to track the object over years.

<p align="center">
<img src="../images/quarry_monitoring_strategy.png?raw=true" width="100%">
<br />
<i>Schematic representation of the object monitoring strategy.</i>
</p>

The `detection_monitoring.py` section of the _yaml_ configuration file is expected as follow:

    detection_monitoring.py:  
    years: [YEAR1, YEAR2, YEAR3,...]       
    datasets:
        detection: ../output/output-prd/'oth_prediction_filter_year-{year}_score-[SCORE]_elevation-[elevation]_distance-[distance]_area-[area].geojson'  
    output_folder: ../output/output-dm
  
Input and output paths of the config file must be adapted if necessary. The script takes as input a _geojson_ file. In the quarry monitoring case, **oth_prediction_filter_year-{year}_[filters_list].geojson** files produced with the script `prediction_filter.py` of the `object-detector` for different years are used. The list of years _YEARx_ required for the object monitoring must be specified.

The script can be run by executing the following command:

    $ python3  <dir_path>/scripts/detection_monitoring.py <dir_path>/config/config-dm.yaml

The outputs are a _geojson_ and _csv_ (**quarry_time**) files saving predictions over years with their caracteristics (ID_object, ID_feature, year, score, area, geometry). 

## 4. `plots.py`

Script to draw basic plots is provided with `plots.py` and works along with the config file `config-dm.yaml` 

The `plots.py` section of the _yaml_ configuration file is expected as follow:

    plots.py:  
    object_id: [ID_OBJECT1, ID_OBJECT2, ID_OBJECT3,...] 
    plots: ['area-year'] 
    datasets:
        detection: ../output/output-dm/quarry_times.geojson
    output_folder: ../output/output-dm/plots

Input ou output paths must be adapted if necessary. The script takes as input a **quarry_times.geojson** file produced with the script `detection_monitoring.py`. The list of **object_id** _ID_OBJECTx_ must be specified and the type of plot as well. So far only **area-year** plot is available. Additional plots can be added in the future.

The script can be run by executing the following command:

    $ python3  <dir_path>/scripts/prediction-filter.py <dir_path>/config/config-dm.yaml

Plot(s) will be produced in _png_ format

<p align="center">
<img src="../images/quarries_area-year.png?raw=true" width="100%">
<br />
<i>Quarries area vs time.</i>
</p>