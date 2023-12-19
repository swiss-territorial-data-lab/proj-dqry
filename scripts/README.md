## Overview

Following, the scripts contained in `proj-dqry` are presented in detailed. The allow to pre- and post-process the data to perform Mineral Extraction Sites (MES, also refered as quarry in this project) automatic detection.

**TOC**
- [Prepare data](#prepare-data)
- [Filter detections](#filter-detections)
- [Detections monitoring](#detections-monitoring)
- [Plots](#plots)
- [Get DEM](#get-dem)
- [Automatisation](#automatisation)


## Prepare data

The `prepare_data.py` script allows the user to prepare the input dataset (image and labels) to be processed by the `object-detector` workflow. Tiles characteristics are defined by the script and will be used by the script `generate_tileset.py`.  _XYZ_ connector is used to fetch images with a Web Map Tiling Service _wmts_. _wmts_ allows to request of images for a given year and provides a base tile of 256 px that can be combined according to the given zoom level _z_. The zoom level will act on the tiles size (and tiles number) and the pixel resolution (z15: 3.2 m/px, z16: 1.6 m/px, z17: 0.8 m/px and z18: 0.4 m/px for _SWISSMAGE 10 cm_). _x_ and _y_ coordinates of tiles on a grid are defined for the given AoI and the zoom level. This script can be used to prepare the tiles of the **Training and evaluation** workflow and the **Detection** workflow. 

It works along the config files `config_trne.yaml` and `config_det.yaml`. Input and output paths of the config files must be adapted if necessary. The `prepare_data.py` section of the _yaml_ configuration file is expected as follow:

```bash
prepare_data.py:
    srs: [crs] 
    datasets:
        labels_shapefile: ./input/[Label_Shapefile]
    output_folder: ./output/
    zoom_level: [z]
```

The **srs** key provides the working geographical frame to ensure all the input data are compatible. The **zoom_level** must be specified (recommanded between 15 and 19). The **labels_shapefile** corresponds to the AoI to be tiled. 

The labels (Ground Truth) are used for the **Training and evaluation** workflow: 

    [Label_Shapefile] = tlm-hr-trn-topo.shp
    
and a given area (_i.e._ it can be the whole of Switzerland, or part of it, such as the footprint where SWISSIMAGE has been acquired for a given year) for the **Detection** workflow:

    [Label_Shapefile] = AoI_[YEAR].shp

for **Training and evaluation** and **Detection** workflows respectively.

The outputs are `tiles.geojson` files corresponding to tiles shapefile obtained for the given AoI and `labels.geojson` corresponding to the input labels shapefile. 

<p align="center">
<img src="../images/tiles_example.png?raw=true" width="100%">
<br />
<i>Example of tiles obtained during the Training and evaluation workflow at zoom level 16 and zoom level 17.</i>
</p>


## Filter detections

The object detection output (`oth_detections_at_0dot*_threshold.gpkg`) obtained via the `object-detector` scripts needs to be filtered to discard false detections and improve the aesthetic of the polygons (merge polygons belonging to a single MES). The script `filter_detections.py` allows the extraction of the detection out of the detection file _gpkg_ based on a series of provided threshold values. It works along with the config file `config_det.yaml`. 

First, elevation filtering is applied using a Digital Elevation Model ([DEM](#get-dem)) as input. Detections above the threshold elevation are discarded (detection at altitude 0 are also discarded because they are located outside of the DEM limits). Next, an algorithm ([KMeans] (https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html)) is applied to cluster polygons according to their centroids. A predefined number of clusters _k_ must be defined. It was set to _k_ = (number of detection / 3), but the influence of this parameter can be explored by the end-user. The polygons are aggregated together according to their cluster value. The other attributes of the polygons, for instance, the detection scores, are aggregated to the maximum value. This preserves the final integrity of detection polygons by keeping detection with potentially low scores but belonging to a cluster with higher scores. This improves the final segmentation of the detected object. Be careful to keep the threshold score value relatively low while running `make_detections.py` to avoid removing too many polygons that could potentially be part of the object detection. Then the detections are filtered based on the score. The detection polygons are clipped with the AoI polygon to remove odd shape polygons spreading outside. Following, polygons that are non-overlapping but are close in position are merged. Based on the polygons' area, values smaller than the threshold are discarded. Finally, an averaged predicted score is computed again taking into account the merged polygons scores. The results of the filtering/merging process are saved in a _geojson_ file.

The following images give an illustration of the extraction process showing the original and filtered detections :

<p align="center">
<img src="../images/filter_detections_before.png?raw=true" width="40%">
&nbsp;
<img src="../images/filter_detections_after.png?raw=true" width="40%">
<br />
<i>Left : Detector detections - Right : Threshold filtering results</i>
</p>

The values of the filtering thresholds are usually obtained by analyzing the output of the detection.

Input and output paths of the config file must be adapted if necessary. The script expects as input a detection file (`oth_detections_at_0dot*_threshold.gpkg` obtained with `make_detections.py` of `object-detector`) file with all geometries containing a _score_ value normalized in _[0,1]_. The `filter_detections.py` section of the _yaml_ configuration file is expected as follow:

```bash
filter_detections.py:
    year:[YEAR] 
    input: ./output/output_det_/oth_detections_at_0dot*_threshold.gpkg
    labels_shapefile: ./input/input_det/[AoI_Shapefile] 
    dem: ./input/input_det/[DEM_raster]  
    elevation: [THRESHOLD VALUE]   
    score: [THRESHOLD VALUE]
    distance: [THRESHOLD VALUE] 
    area: [THRESHOLD VALUE] 
    output: ./output/output_det_/oth_detection_at_0dot*_threshold_year-[YEAR]_score-{score}_area-{area}_elevation-{elevation}_distance-{distance}.geojson
```

-**year**: year of the dataset used as input for filtering

-**input**: indicate the path to the input file that needs to be filtered, _i.e._ `oth_detections_at_0dot*_threshold.gpkg`

-**labels_shapefile**: AoI of interest is used to remove polygons that are located partially outside the AoI. For the project, we used the _SWISSIMAGE_ acquisition footprint for a given year (AoI_[YEAR].shp).

-**dem**: indicate the path to a DEM of Switzerland. SRTM-derived product is used and can be download and reprojected with script `get_DEM.sh`. A threshold elevation is used to discard detection above the given value.

-**elevation**: altitude above which detections are discarded. Indeed 1st tests have shown numerous false detection due to snow cover area (reflectance value close to bedrock reflectance) or mountain bedrock exposure that are mainly observed at altitude. By default, the threshold elevation has been set to 1200.0 m.

-**score**: each polygon comes with a confidence score given by the detection algorithm. Polygons with low scores can be discarded. By default, the value is set to 0.95.

-**distance**: two polygons that are close to each other can be considered to belong to the same MES. Those polygons can be merged into a single one. By default, the buffer value is set to 10 m.

-**area**: small area polygons can be discarded assuming a MES has a minimal area. The default value is set to 5000 m<sup>2</sup>.

-**output**: provide the path of the filtered polygons shapefile with the detection score preserved. The output file name will be formated as: `oth_detection_at_0dot*_threshold_year-{year}_score-{score}_elevation-{elevation}_distance-{distance}_area-{area}.geojson`.


The script can be run by executing the following command:

```bash
$ python3 <dir_path>/scripts/filter_detections.py <dir_path>/config/config_det.yaml
```

## Detections monitoring

The script `detections_monitoring.py` has been developed to identify and track an object between different year datasets. It works along with the config file `config_dm.yaml`.

The script identifies the position of polygons between different years to identify a single object in several datasets. All the detection shapes are added to a single data frame. A union function is applied to merge overlapping polygons. Those polygons (single and merged) are added to a new data frame with a unique ID attributed to each. This data frame is then spatially (_sjoin_) compared to the initial data frame containing all the polygons by year. The unique ID of the polygons of the second data frame is then attributed to the intersecting polygons of the first data frame. Therefore, overlapping polygons between years are assumed to describe the same object and receive the same unique ID allowing us to track the object over years.

<p align="center">
<img src="../images/quarry_tracking_strategy.png" width="100%">
<br />
<i>Schematic representation of the object monitoring strategy.</i>
</p>

The `detection_monitoring.py` section of the _yaml_ configuration file is expected as follow:

```bash
detection_monitoring.py:  
years: [YEAR1, YEAR2, YEAR3,...]       
datasets:
    detection: ./input/input_dm/oth_detection_at_0dot*_threshold_year-{year}_score-[SCORE]_elevation-[elevation]_distance-[distance]_area-[area].geojson  
output_folder: ./output/output_dm
```

Input and output paths of the config file must be adapted if necessary. The script takes as input a _geojson_ file. `oth_detection_at_0dot*_threshold_year-{year}_[filters_list].geojson` files of different years produced with the script `filter_detections.py` of the `object-detector` are used. The list of years _YEARx_ required for the object monitoring must be specified.

The script can be run by executing the following command:

```bash
$ python3  <dir_path>/scripts/detection_monitoring.py <dir_path>/config/config_dm.yaml
```

The outputs are a _geojson_ and _csv_ (**quarry_time**) files saving detections over the years with their characteristics (ID_object, ID_feature, year, score, area, geometry). 

## Plots

Script to draw basic plots is provided with `plots.py` and works along with the config file `config_dm.yaml` 

The `plots.py` section of the _yaml_ configuration file is expected as follows:

```bash
plots.py:  
    object_id: [ID_OBJECT1, ID_OBJECT2, ID_OBJECT3,...] 
    plots: ['area-year'] 
    datasets:
        detection: ./output/output_dm/quarry_times.geojson
    output_folder: ./output/output_dm/plots
```
Input or output paths must be adapted if necessary. The script takes as input a **quarry_times.geojson** file produced with the script `detections_monitoring.py`. The list of **object_id** _ID_OBJECTx_ must be specified and the plot type. So far only **area-year** plot is available. Additional plots can be added in the future.

The script can be run by executing the following command:

```bash
$ python3  <dir_path>/scripts/filter_detections.py <dir_path>/config/config_dm.yaml
```

Plot(s) will be produced in _png_ format

<p align="center">
<img src="../images/quarry_area-year.png" width="100%">
<br />
<i>Quarries area vs time.</i>
</p>


## Get DEM

Among other filters, the detections are filtered out by elevation, requiring a DEM. For the project the DEM of Switzerland processed by Lukas Martinelli is used. The file can be downloaded from this [repository](https://github.com/lukasmartinelli/swissdem). To comply with the CRS of the project, the file is converted from EPSG:4326 to EPSG:2056. The whole procedure is performed by the script `batch_process.sh`.


## Automatisation

`batch_process.sh` allows the execution of a list of commands to perform the **Detection** workflow for several years. It works along with `config_det.template.yaml`.

The list of years to process must be specified as input of the shell script: 

```bash
for year in YEAR1 YEAR2 YEAR3 ... 
```

By executing the command:

```bash
$ ./scripts/batch_process.sh
```

`config_det_[YEAR].yaml` will be generated for a given year, and the command list in `batch_process.sh` will be executed for the provided list of years:
 1. `prepare_data.py`
 2. `generate_tilesets.py` 
 3. `make_detections.py` 
 4. `filter_detections.py` 

The paths and value of the _yaml_ configuration file template must be adapted, if necessary.