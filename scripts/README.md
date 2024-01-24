## Overview

The following is a detailed description of the scripts contained in `proj-dqry`. They are used to process data and results as part of the automatic detection of mining extraction sites (MES, also known as quarries in this project) with the STDL's object detector.

**TOC**
- [Prepare data](#prepare-data)
- [Filter detections](#filter-detections)
- [Track detections](#track-detections)
- [Plots](#plots)
- [Get DEM](#get-dem)
- [Automatisation](#automatisation)


## Prepare data

The `prepare_data.py` script allows the user to prepare the input dataset (images and labels) to be processed by the `object-detector` workflow. Tiles characteristics are defined by the script and will be used by the `generate_tileset.py` script.  _XYZ_ connector is used to fetch images with a Web Map Tiling Service _wmts_. _wmts_ service is used to request images for a given year and provides a tile of 256 px. The zoom level _z_ affects the pixel resolution (_z_ = 15: 3.2 m/px, _z_ = 16: 1.6 m/px, _z_ = 17: 0.8 m/px and _z_ = 18: 0.4 m/px for _SWISSIMAGE 10 cm_). _x_ and _y_ coordinates of tiles on a grid are defined for a given AoI and zoom level. This script is used to prepare the tiles of the **Training and evaluation** workflow and the **Detection** workflow. 

It works along the config files `config_trne.yaml` and `config_det.yaml`. Input and output paths of the config files must be adapted if necessary. The `prepare_data.py` section of the _yaml_ configuration file is expected as follow:

```bash
prepare_data.py:
    srs: <crs> 
    datasets:
        shapefile: ./input/<shapefile>
    output_folder: ./output/<output_dir>
    zoom_level: <z>
```

The **srs** key provides the geographic framework to ensure that all the input data are compatible. The **zoom_level** must be specified (recommended between 15 and 19). The **shapefile** corresponds to the AoI to be tiled. 

The labels (ground truth) polygons are used for the **Training and evaluation** workflow: 

    <shapefile> = tlm-hr-trn-topo.shp
    
A region of Switzerland polygon is used for the **Detection** workflow:

    <shapefile> = swissimage_footprint_<YEAR>.shp

The outputs are `tiles.geojson` corresponding to shapefiles of the tiles obtained for the given AoI and `labels.geojson` corresponding to shapefiles of the input labels. 

<p align="center">
<img src="../images/tiles_example.png?raw=true" width="100%">
<br />
<i>Example of tiles obtained during the training and evaluation workflow at zoom level 16 and zoom level 17.</i>
</p>


## Filter detections

The object detection output (`oth_detections_at_0dot*_threshold.gpkg`) obtained with the `object-detector` scripts needs to be filtered to discard false detections and improve the aesthetic of the polygons (merge polygons belonging to a single MES). The `filter_detections.py` script extracts detections from _gpkg_ file according to a series of threshold values. It works along with the config file `config_det.yaml`. 

First, elevation filtering is applied using a Digital Elevation Model ([DEM](#get-dem)) as input. Detections above the elevation threshold are discarded. Detections at altitude 0 are also discarded because they are lie outside the DEM limits. Next, an algorithm ([KMeans] (https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html)) is applied to cluster polygons according to their centroids. A predefined number of clusters _k_ is set as _k_ = (number of detection / 3). Polygons are grouped according to their cluster value. Polygon attributes, such as confidence scores, are aggregated at the maximum value. This preserves the final integrity of the detection polygons by retaining detections with potentially low scores but belonging to a cluster with higher scores. This improves the final segmentation of the detected object. Be careful to keep the threshold score value relatively low (chosen value = 0.3) while running `make_detections.py` to avoid removing too many polygons that could potentially be part of the object detection. Then, the detections are filtered based on the confidence score. The detection polygons are clipped with the AoI polygon to remove odd shaped polygons that extend outwards. Next, polygons that do not overlap but are close in position are merged. Based on the surface area of the polygons, values below the threshold are eliminated. Finally, an averaged predicted score is again computed, taking into account the score of the merged polygons. The results of the filtering/merging process are saved in a _geojson_ file.

The following images illustrate the extraction process, showing the original and filtered detections:

<p align="center">
<img src="../images/filter_detections_before.png?raw=true" width="40%">
&nbsp;
<img src="../images/filter_detections_after.png?raw=true" width="40%">
<br />
<i>Left : Detections obtained with the object detector. Right : Threshold filtering results</i>
</p>

Input and output paths of the config file must be adapted if necessary. The script expects as input a detection file, `oth_detections_at_0dot*_threshold.gpkg`, obtained with the `make_detections.py` script of the `object-detector` framework. The `filter_detections.py` section of the configuration file is expected as follow:

```bash
filter_detections.py:
    year: <YEAR> 
    input: ./output/output_det/oth_detections_at_<SCORE_LOWER_THRESHOLD_0dot*>_threshold.gpkg
    shapefile: ./input/input_det/<shapefile> 
    dem: ./input/input_det/<DEM_raster>  
    elevation: <THRESHOLD_VALUE>   
    score: <THRESHOLD_VALUE>
    distance: <THRESHOLD_VALUE> 
    area: <THRESHOLD_VALUE> 
    output: ./output/output_det/oth_detections_at_0dot*_threshold_year-{year}_score-{score}_area-{area}_elevation-{elevation}_distance-{distance}.geojson
```

- **year**: year of the dataset to be filtered used as input.

- **input**: path to the input file to be filtered, _i.e._ `oth_detections_at_0dot*_threshold.gpkg`.

- **shapefile**: AoI of interest used to remove polygons located partially outside the AoI. _SWISSIMAGE_ acquisition footprint for a given year (swissimage_footprint_<YEAR>.shp) were used for this project.

- **dem**: path to a DEM of Switzerland. Product derived from SRTM is used and can be downloaded and reprojected with the `get_DEM.sh` script. An elevation threshold is used to discard detections above the given value.

- **elevation**: the altitude above which detections are discarded. Initial tests have shown that many false detections are due to snow cover (reflectance value close to bedrock reflectance) or to the exposure of the bedrock in the mountains, which are mainly observed at higher altitudes. By default, the threshold elevation has been set to 1200 m.

- **score**: each polygon is given a confidence score by the detection algorithm. Polygons with a low scores can be discarded. By default, the value is set to 0.95.

- **distance**: two polygons close to each other can be considered as belonging to the same MES. These polygons can be merged into a single polygon. By default, the buffer value is set to 10 m.

- **area**: small area polygons can be discarded by assuming that a MES has a minimum area. The default value is set to 5000 m<sup>2</sup>.

- **output**: path to the shapefile of filtered polygons with the detection score preserved. The name of the output file is formatted as: `oth_detections_at_0dot*_threshold_year-{year}_score-{score}_elevation-{elevation}_distance-{distance}_area-{area}.geojson` with '0dot*' the value of the lower score threshold of the detection chosen as 0.3 for the project.


The script can be run by executing the following command:

```bash
$ python <dir_path>/scripts/filter_detections.py <dir_path>/config/config_det.yaml
```

## Track detections

The script `track_detections.py` has been developed to identify and track an object over a multiple year datasets. It works along with the config file `config_track.yaml`.

The detection shapefiles for each year are merged. Overlapping groups of detections and non-overlapping individual detections are assigned a unique object identifier. The object identifier is then propagated to each year's detection polygons by intersection with the merged polygons. Polygons sharing the object identifier are assumed to describe the same object, allowing it to be tracked over time.

<p align="center">
<img src="../images/quarry_tracking_strategy.png" width="100%">
<br />
<i>Schematic representation of the object tracking strategy.</i>
</p>

The `track_detections.py` section of the _yaml_ configuration file is expected as follow:

```bash
track_detections.py:  
years: <[YEAR1, YEAR2, YEAR3,...]>      
datasets:
    detection: ./input/input_track/oth_detections_at_<SCORE_LOWER_THRESHOLD_0dot*>_threshold_year-<YEAR>_score-<SCORE>_elevation-<ELEVATION>_distance-<DISTANCE>_area-<AREA>.geojson  
output_folder: ./output/output_track
```

Input and output paths of the config file must be adapted if necessary. The script takes as input the _geojson_ files `oth_detections_at_<SCORE_LOWER_THRESHOLD_0dot*>_threshold_year-<YEAR>_<filters_list>.geojson` of different years produced with the script `filter_detections.py` of the `object-detector`. The list of years _YEARx_ required for the object tracking must be specified.

The script can be run by executing the following command:

```bash
$ python  <dir_path>/scripts/track_detections.py <dir_path/config/config_track.yaml
```

The outputs are a _geojson_ and _csv_ (**detections_years**) files saving the detections over the years with their characteristics (ID_object, ID_feature, year, score, area, geometry). 

## Plots

Script for drawing basic plots is supplied with `plots.py` and works along with the config file `config_track.yaml` 

The `plots.py` section of the _yaml_ configuration file is expected as follows:

```bash
plots.py:  
    object_id: <[ID_OBJECT1, ID_OBJECT2, ID_OBJECT3,...]>
    plots: ['area-year'] 
    datasets:
        detection: ./output/output_track/detections_years.geojson
    output_folder: ./output/output_track/plots
```
Input or output paths must be adapted if necessary. The script takes as input a **detections_years.geojson** file produced with the script `track_detections.py`. The list of **object_id** _ID_OBJECTx_ must be specified as well as the plot type. So far only **area-year** plot is available. Additional plots can be added in the future.

The script can be run by executing the following command:

```bash
$ python <dir_path>/scripts/filter_detections.py <dir_path>/config/config_track.yaml
```

<p align="center">
<img src="../images/quarry_area-year.png" width="100%">
<br />
<i>Object area vs time.</i>
</p>


## Get DEM

Among other filters, the detections are filtered out by elevation, requiring a DEM. For the project, the DEM of Switzerland processed by Lukas Martinelli is used. The file can be downloaded from this [repository](https://github.com/lukasmartinelli/swissdem). To comply with the CRS of the project, the file is converted from EPSG:4326 to EPSG:2056. The whole procedure is performed by the script `get_DEM.sh`.


## Automatisation

`batch_process.sh` allows the execution of a list of commands to perform the **Detection** workflow for several years. It works along with `config_det.template.yaml`.

The list of years to processed must be specified as input of the shell script: 

```bash
for year in YEAR1 YEAR2 YEAR3 ... 
```

By executing the command:

```bash
$ ./scripts/batch_process.sh
```

`config_det_{year}.yaml` will be generated for a given year, and the command list in `batch_process.sh` will be executed for the provided list of years:
 1. `prepare_data.py`
 2. `generate_tilesets.py` 
 3. `make_detections.py` 
 4. `filter_detections.py` 

The paths and values of the _yaml_ configuration file template must be adapted, if necessary.