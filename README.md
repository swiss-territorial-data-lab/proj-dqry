## Overview

This project provides a suite of scripts and configuration files to perform quarries automatic detections in georeferenced raster images with Deep Learning method. For the object detection, tools developped in `object-detector` git repository are used. The description of the scripts are presented here: https://github.com/swiss-territorial-data-lab/object-detector

The procedure is defined in tree disctinct worflows:
* the 'Training and Evaluation' workflow allowing to train the detection model on a given image dataset (year) and evaluated to ground truth dataset reveiwed by domain experts. The detector is initially trained on _swissimage_ mosaic of 2020 (_swisstopo_) from using the _TLM_ data of _swisstopo_ as Ground Truth.
* the 'Prediction' workflow performing inference detection of quarries in a given image dataset (year) thanks to the previously trained model.
* the 'Object monitoring' workflow tracking quarry evolution over years.


## Hardware and OS requirements

The workflows have been run with Ubuntu 20.04 OS on a GPU machine with 32 Gbits RAM. The main limitation is the number of tiles to proceed and the amount of prediction. The provided requirements stand for a zoom level equal to or below 17 and for an AOI corresponding to SWISSIMAGE acquisition footprints (about a third of Switzerland surface max). For higher zoom level and/or a larger AOI, the number of data to process might lead to memory saturation. In this case either a more powerful machine will be required, or the AOI will need to be subdivided in a smaller area.

## Python libraries

The scripts have been developed with Python 3.8 by importing libraries that are listed in `requirements.in` and `requirements.txt`. Before starting to run scripts make sure the required Python libraries that have been used during the code development are installed, otherwise incompatibilities and errors could occur. A clean method to install Python libraries is to work with a virtual environment preserving the package dependencies.

* if not already done, create a dedicated Python virtual environment:
	    
      python3 -m venv <dir_path>/[name of the virtual environment]

* activate the virtual environment:

      source <dir_path>/[name of the virtual environment]/bin/activate

* install the required Python packages into the virtual environment:

      pip install -r requirements.txt

The `requirements.txt` file used for the quarries detection can be found in the `proj-dqry` repository. 

* deactivate the virtual environment if not used anymore

      deactivate


## Required input data

The input data for the ‘Training and Evaluation’ and ‘Prediction’ workflows for the quarry detection project are stored on the STDL kDrive (https://kdrive.infomaniak.com/app/drive/548133/files) with the following access path: /STDL/Common Documents/Projets/En_cours/Quarries_TimeMachine/02_Data/

In this main folder you can find subfolders:
*	DEM
    -	`swiss-srtm.tif`: DEM (spatial resolution about 25 m/px) of Switzerland produced from SRTM instrument (https://doi.org/10.5066/F7PR7TFT). The raster is used to filter the quarry detection according to elevation values.
* Learning models
    - `logs_*`: folders containing trained detection models obtained during the 'training workflow' using Ground Truth data. The learning characteristics of the algorithm can be visualized using tensorboard (see below in Processing/Run scripts). Models at several epochs have been saved. The optimum model minimize the validation loss curve across epochs. This model is used to perform the ‘Prediction’ workflow. The algorithm has been trained on SWISSIMAGE data with zoom levels from 15 (3.2 m/px) to 18 (0.4 m/px). For each zoom level subfolder a file `metrics_epoch-*.txt` is provided summing-up the metrics values (precision, recall and f1-score) obtained for the optimized model epoch. The user can either used the already trained model or performed is own model training by running the ‘Training and Evaluation’ workflow and use this produced model to detect quarries.

* Shapefiles
    -	`quarry_label_tlm_revised`: polygons shapefile of the quarries labels (TLM data) reviewed by the domain experts. The data of this file have been used as Ground Truth data to train and assess the automatic detection algorithm.
    - `swissimage_footprints_shape_year_per_year`: original SWISSIMAGE footprints and processed polygons border shapefiles for every SWISSIMAGE acquisition year.
    - `switzerland_border`: polygon shapefile of the Switzerland border. 

*	SWISSIMAGE
    - `Explanation.txt`: file explaining the main characteristics of SWISSIMAGE and the references links (written by R. Pott).


## Workflow

This section detail the procedure and the command lines to execute in order to run the 'Training and Evaluation' and 'Prediction' workflows.

### Training and Evaluation

- Working directory

The working directory can be modified but is by default:

    $ cd proj-dqry/config/

- Config and input data

Configuration files are required:

    [logging_config] = logging.conf

The logging format file can be used as provided. 

    [config_yaml] = config-trne.yaml 

The _yaml_ configuration file has been set for the object detector workflow by reading the dedicated sections. Verify and adapt, if required, the input and output paths. 

The `prepare_data.py` section of the _yaml_ configuration file is expected as follow:

    prepare_data.py:
        srs: "EPSG:2056"
        datasets:
            labels_shapefile: ../input/input-trne/[Label_Shapefile]
      output_folder: ../output/output-trne
      zoom_level: [z]

Set the path to the desired label shapefile (AOI) (create a new folder: /proj-dqry/input/input-trne/ to the project). For the training, the `labels_shapefile` corresponds to polygons of quarries defined in the TLM and manually reviewed by experts. It constitutes the ground truth. 

For the quarries example:

    [Label_Shapefile] = tlm-hr-trn-topo.shp

`prepare_data.py` set the tiles parameters for the tiling service request. _XYZ_ connector is used to fetch images with a Web Map Tiling Service _wmts_. _wmts_ allows to request images for a given year and provides base tile of 256 px that can be combined according to the given zoom level _z_. _x_ and _y_ coordinates of tiles on a grid are defined for the given AOI and the zoom level. To avoid large computation time during the training phase, only tiles intersecting labels are kept. 

The _srs_ key provides the working geographical frame to ensure all the input data are compatible together.

- Run scripts

The training and detection of objects requires the use of `object-detector` scripts. The workflow is processed in following way:

    $ python3 ../scripts/prepare_data.py [config_yaml]
    $ python3 ../../scripts/generate_tilesets.py [config_yaml]
    $ python3 ../../scripts/train_model.py [config_yaml]
    $ python3 ../../scripts/make_prediction.py [config_yaml]
    $ python3 ../../scripts/assess_predictions.py [config_yaml]

The script can be run on a sample of images by activating or not the option `debug_mode` in the _yaml_ config file. The number of tiles selected is currently hard-coded in the script `generate_tilesets.py`.  
In between `train_model.py` and `make_prediction.py` scripts execution, the output of the detection model training (`logs`) must be checked to identify the optimum epoch of the model, _i.e._ the epoch minimizing the validation loss curve. This epoch must be chosen (obtained for a given iteration number) and set as input trained model (model_weights: pth_file:./logs/[chosen model].pth) to make predictions. The optimum is dependant of the zoom level and the number of tiles involved. The file `model_final.pth` corresponds to the last iteration recorded during the training procedure.

The validation loss curve can be visualized with `tensorboard`. The library `PyTorch` must be installed (installed and activated the virtual environment).   

    tensorboard --logdir <logs folder path>/logs
And open the following link with a web browser: `http://localhost:6006`

- Output

Finally we obtained the following results in the folder /proj-dqry/output/output-trne/:

- `*_images`: folders containing downloaded images splited to the different datasets (all, train, test, validation) 
- `sample_tagged_images`: folder containing sample of tagged images and bounding boxes 
- `logs`: folder containing the files relative to the model training 
- `tiles.geojson`: tiles polygons obtained for the given AOI 
- `labels.geojson`: labels polygons obtained for the given GT
- `*_predictions.geojson`: detection polygons obtained for the different datasets (train, test, validation)
- `img_metadata.json`: images metadata file 
- `clipped_labels.geojson`: labels polygons clipped according to tiles
- `split_aoi_tiles.geojson`: tiles polygons sorted according to the dataset where it belongs  
- `COCO_*.json`: COCO annotations for each image of the datasets 
- `*_predictions_at_0dot*_threshold.pkl`: serialized pickle file of the prediction shapes for the different datasets and filtered by prediction score value (from 0 to 1). The score value can be custom in the config _yaml_ file `score_thd` for `make_prediction.py` script.  
-`*.html`: plots to evaluate the prediction results with metrics values (precision, recall, f1) and TP, FP and FN values

### Prediction

- Working directory

The working directory can be modified but is by default:

    $ cd /proj-dqry/config/

- Config and input data

Two configuration files are provided in `proj-dqry`:

    [config_yaml] = config-prd.yaml 
    [logging_config] = logging.conf

The configuration _yaml_ has been set for the object detector workflow by reading dedicated section. Verify and adapt, if required, the input and output paths.
The `prepare_data.py` section of the _yaml_ configuration file is expected as follow:

    prepare_data.py:
        srs: "EPSG:3857"
        datasets:
            labels_shapefile: ../input/input-trne/[AOI_Shapefile]
      output_folder: ../output/output-prd
      zoom_level: [z]

Set the path to the desired label shapefile (AOI) (create a new folder /proj-dqry/input/input-prd/ to the project). For the prediction, the `labels_shapefile` corresponds to the AOI on which the object detection must be performed. It can be the whole Switzerland or part of it such as the footprint where SWISSIMAGE has been acquired for a given year. 

For the quarries example:

    [Label_Shapefile] = swissimage_footprint_[year].shp

`prepare_data.py` set the tiles parameters for the tiling service request. _XYZ_ connector is used to fetch images with a Web Map Tiling Service _wmts_. _wmts_ allows to request images for a given year and provides base tile of 256 px that can be combined according to the given zoom level _z_. _x_ and _y_ coordinates of tiles on a grid are defined for the given AOI and the zoom level. To avoid large computation time during the training phase, only tiles intersecting labels are kept. 

The _srs_ key provides the working geographical frame to ensure all the input data are compatible together.

The object detection use a trained model. Copy the desired `logs_*` folder obtained during the 'Training and Evaluation' workflow into the folder proj-dqry/input/input-prd/.

      model_weights: pth_file: '../../input/input-prd/logs/model_*.pth'

Choose the relevant `model_*.pth` file, _i.e._ the one minimizing the validation loss curve (see above Training and Evaluation/Run scripts). 

-Run scripts

The prediction of objects requires the use of `object-detector` scripts. The workflow is processed in following way:

    $ python3 ../scripts/prepare_data.py [yaml_config]
    $ python3 ../../scripts/generate_tilesets.py [config_yaml]
    $ python3 ../../scripts/make_prediction.py [config_yaml]
    $ python3 ../../scripts/assess_predictions.py [config_yaml]

The script can be run on a sample of images by activating or not the option `debug_mode` in the _yaml_ config file. The number of tiles selected is currently hard-coded in the script `generate_tilesets.py`. 

- Output:

Finally we obtained the following results stored in the folder /proj-dqry/output/output-prd/:

- `oth_images`: folders containing downloaded images of an AOI to perform prediction inference
- `sample_tagged_images`: folder containing sample of tagged images and bounding boxes 
- `tiles.geojson`: tiles polygons obtained for the given AOI 
- `oth_predictions.geojson`: detection polygons obtained for the AOI
- `img_metadata.json`: images metadata file 
- `clipped_labels.geojson`: labels polygons clipped according to tiles
- `split_aoi_tiles.geojson`: tiles polygons sorted according to the dataset where it belongs  
- `COCO_oth.json`: COCO annotations for each image 
- `oth_predictions_at_0dot*_threshold.pkl`: serialized pickle file of the prediction shapes filtered by prediction score value (from 0 to 1). The score value can be custom in the config _yaml_ file `score_thd` for `make_prediction.py` script.  

- Post-processing

The object detection output (`oth_predictions.geojson`) obtained via the `object-detector` scripts needs to be filtered to discard false detections and improve the aesthetic of the polygons (merge polygons belonging to a single quarry). The script `prediction_filter.py` allows to extract the prediction out of the detector _GeoJSON_ based on a series of provided threshold values.

The first step going on is a clustering of the centroids of every prediction polygon. This is used as a way to maintain the scores for a further unary union of the polygons, that then uses the cluster value assigned as an aggregation method. This allows the removal of lower scores in a smart way, *i.e.*, by maintaining the integrity of the final polygon. Then, predictions are filtered based on the polygons' areas value. Following, with the input of a Digital Elevation Model an elevation thresholding is processed. Finally, the predictions are filtered based on the score. This score is calculated as the maximum score obtained from the polygons intersecting the merged polygons. The results of the filtering/merging are dumped in the provided output _GeoJSON_ (destination is replaced in case it exists).

The following images give an illustration of the extraction process showing the original and filtered predictions :

<p align="center">
<img src="images/before.png?raw=true" width="40%">
&nbsp;
<img src="images/after.png?raw=true" width="40%">
<br />
<i>Left : Detector predictions - Right : Threshold filtering results</i>
</p>

The value of the filtering threshold is usually obtained by the training validation set analysis or other more advanced methods.

The `prediction_filter.py` is run as follow:

- Working directory

The working directory can be modified but is by default:

    $ cd /proj-dqry/config/
    
- Config and input data

    [config_yaml] = config-prd.yaml 

The script expects a prediction _GeoJSON_ (`oth_prediction.geojson` obtained with `assess_prediction.py`) file with all geometries containing a _score_ value normalised in _[0,1]_. The `prediction_filter.py` section of the _yaml_ configuration file is expected as follow. Paths and threshold values must be adapted:

    prediction_filter.py:
        input: ../output/output-prd/oth_predictions.geojson 
        dem: ../input/DEM/swiss-srtm.tif 
        elevation: [THRESHOLD VALUE]   
        score: [THRESHOLD VALUE]
        distance: [THRESHOLD VALUE] 
        area: [THRESHOLD VALUE] 
        output: ../output/output-prd/


-`input`: indicate path to the input geojson file that needs to be filtered, _i.e._ `oth_predictions.geojson` 

-`dem`: indicate the path to the DEM of Switzerland. A SRTM derived product is used and can be found in the STDL kDrive. A threshold elevation is used to discard detection above the given value. 

-`elevation`: altitude above which prediction are discard. Indeed 1st tests have shown numerous false detection due to snow cover area (reflectance value close to bedrock reflectance) or mountain bedrock exposure. By default the threshold elevation has been set to 1155.0 m.

-`score`: each polygon comes with a confidence score given by the prediction algorithm. Polygons with low scores can be discarded. By default the value is set to 0.96.

-`distance`: two polygons that are close to each other can be considered to belong to the same quarry. Those polygons can be merged into a single one. By default the buffer value is set to 8 m.

-`area`: small area polygons can be discarded assuming a quarry has a minimal area. The default value is set to 1728 m2.

-`output`: provide the path of the filtered polygons shapefile: `oth_prediction_filter_year-{year}.geojson` 


The script `prediction_filter.py` is run as follow:

    $ python3 ../scripts/prediction-filter.py [config_yaml]


### Prediction monitoring

The 'Prediction' workflow computes object prediction on images acquired at different years. In order to monitor the detected object over years, the script `detection_monitoring.py` has been developped.

The script identify the position of polygons between different years in order to identify single object in several datasets. All the detection shape are added to a single dataframe. A union function is applied in order to merge overlapping polygons. Those polygons (single and merged) are added to a new dataframe with a unique ID attributed to each. This dataframe is then spatially (`sjoin`) compared to the initial dataframe containing all the polygons by year. The unique ID of the polygons of the second dataframe is then attributed to the intesecting polygons of the first dataframe. Therefore, overlapping polygons between years are assumed to described the same object and received the same unique ID allowing to track the object over years.

<p align="center">
<img src="images/quarry_monitoring_strategy.png?raw=true" width="100%">
<br />
<i>Schematic representation of the object monitoring strategy.</i>
</p>

The `detection_monitoring.py` is run as follow:

- Working directory

The working directory can be modified but is by default:

    $ cd /proj-dqry/config/
    
- Config and input data

    [config_yaml] = config-dm.yaml 

The `detection_monitoring.py` section of the _yaml_ configuration file is expected as follow:

        years: [YEAR1, YEAR2, ...]      # Provide a list of years used for detection
        datasets:
            detection: ../output/output-prd/oth_prediction_filter_year-{year}.geojson  # Final detection file, produced by prediction_filter.py 
        output_folder: ../output/output-dm
  
Paths must be adapted if necessary. The script takes as input a _GeoJSON_ file (`oth_prediction_filter_year-{year}.geojson`) obtained previously with the script `prediction_filter.py` for different years. The list of years required for the object monitoring must be specified.

-Run scripts

The prediction of objects requires the use of `object-detector` scripts. The workflow is processed in following way:

    $ python3 ../scripts/plots.py [config_yaml]


The outputs are a _GeoJSON_ and _csv_ (_quarry_times_) files containing prediction over years with the main caracteristics (ID_object, ID_feature, year, score, area, geometry). The prediction files computed for previous years and _quarry_times_ files can be found on the STDL kDrive (https://kdrive.infomaniak.com/app/drive/548133/files) with the following access path: /STDL/Common Documents/Projets/En_cours/Quarries_TimeMachine/03_Results/

### Plots

Script to draw basic plots is provided with `plots.py`.

- Working directory

The working directory can be modified but is by default:

    $ cd /proj-dqry/config/

- Config and input data

    [config_yaml] = config-dm.yaml 

The `plots.py` section of the _yaml_ configuration file is expected as follow:

    quarries_id: [Q1, Q2, ...]      # Provide a list of years used for detection
    plots: ['area-year'] 
    datasets:
        detection: ../output/output-dm/quarry_times.geojson  # Final detection file, produced by prediction_filter.py 
    output_folder: ../output/output-dm/plots

Paths must be adapted if necessary. The script takes as input a `quarry_times.geojson` file produced with the script `detection_monitoring.py`. The list of object_id is required and the type of plot as well. So far only 'area-year' plot is available. Additionnal type of plots can be added in the future.

-Run scripts

    $ python3 ../scripts/prediction-filter.py [config_yaml]

## Copyright and License

The pre-processing and post-processing scripts originate from the git repository `detector-interface`
  
**detector-interface** - Nils Hamel, Adrian Meyer, Huriel Reichel, Alessandro Cerioni <br >
Copyright (c) 2020-2022 Republic and Canton of Geneva

This program is licensed under the terms of the GNU GPLv3. Documentation and illustrations are licensed under the terms of the CC BY 4.0.