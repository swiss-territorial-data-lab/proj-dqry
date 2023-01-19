## Overview

This document provides a detailed description of the procedure to run `proj-dqry` and perform quarries automatic detections. For object detection, tools developed in `object-detector` git repository are used. The description of the scripts are presented here: https://github.com/swiss-territorial-data-lab/object-detector

The procedure is defined in three distinct workflows:
*  'Training and Evaluation' workflow allows to train the detection model on a given image dataset (year) and evaluate to ground truth dataset reviewed by domain experts. The detector is initially trained on _swissimage_ mosaic of 2020 (_swisstopo_) from using the _TLM_ data of _swisstopo_ as Ground Truth.
*  'Prediction' workflow performing inference detection of quarries in a given image dataset (year) thanks to the previously trained model.
*  'Detection monitoring' workflow tracking quarry evolution over years.

Configuration files are used to set the variables parameters. They must be adapted if required. In **config** folder config files relative to `proj-dqry` and `object-detector` are present, one for each workflow type:

1. Training and evaluation: `config-trne.yaml`
2. Predictions: `config-prd.yaml`
3. Detection monitoring: `config-dm.yaml`

A config file dedicated to set the parameters of the detectron2 algorithm is also provided: `detectron2_config_dqry.yaml`

 A synthetic list of command lines to run the whole project can be found at the end of the document.


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


## Input data

The input data for the ‘Training and Evaluation’ and ‘Prediction’ workflows for the quarry detection project are stored on the STDL kDrive (https://kdrive.infomaniak.com/app/drive/548133/files) with the following access path: /STDL/Common Documents/Projets/En_cours/Quarries_TimeMachine/02_Data/

In this main folder you can find subfolders:
*    DEM
	-    `swiss-srtm.tif`: DEM (spatial resolution about 25 m/px) of Switzerland produced from SRTM instrument (https://doi.org/10.5066/F7PR7TFT). The raster is used to filter the quarry detection according to elevation values.
* Learning models
	- `logs_*`: folders containing trained detection models obtained during the 'training workflow' using Ground Truth data. The learning characteristics of the algorithm can be visualized using tensorboard (see below in Processing/Run scripts). Models at several iterations have been saved. The optimum model minimizes the validation loss curve across iteration. This model is used to perform the ‘Prediction’ workflow. The algorithm has been trained on SWISSIMAGE 10 cm 2020 mosaic for zoom levels 15 (3.2 m/px) to 18 (0.4 m/px). For each zoom level subfolder a file `metrics_ite-*.txt` is provided summing-up the metrics values (precision, recall and f1-score) obtained for the optimized model. The user can either used the already trained model or perform his own model training by running the ‘Training and Evaluation’ workflow and use this produced model to detect quarries.
It is important to note that the training procedure has random components and therefore the training results might differ from the ones provided.

* Shapefiles
	-    `quarry_label_tlm_revised`: polygon shapefile of the quarries labels (TLM data) reviewed by the domain experts. The data of this file have been used as Ground Truth data to train and assess the automatic detection algorithm.
	- `swissimage_footprints_shape_year_per_year`: original SWISSIMAGE footprints and processed polygons border shapefiles for every SWISSIMAGE acquisition year.
	- `switzerland_border`: polygon shapefile of the Switzerland border.

*    SWISSIMAGE
	- `Explanation.txt`: file explaining the main characteristics of SWISSIMAGE and the reference links.


## Workflows

This section detail the procedure and the command lines to execute in order to run the 'Training and Evaluation' and 'Prediction' workflows.

### Training and Evaluation

- Working directory

The working directory can be modified but by default is:

    $ cd proj-dqry/config/

- Config and input data

Configuration files are required:

    [logging_config] = logging.conf

The logging format file can be used as provided. 

    [config_yaml] = config-trne.yaml 

The _yaml_ configuration file has been set for the object detector workflow by reading the dedicated sections. Verify and adapt, if necessary, the input and output paths. 

- Run scripts

The training and detection of objects requires the use of `object-detector` scripts. The workflow is processed in following way:

    $ python3 ../scripts/prepare_data.py [config_yaml]
    $ python3 ../../scripts/generate_tilesets.py [config_yaml]
    $ python3 ../../scripts/train_model.py [config_yaml]
    $ python3 ../../scripts/make_prediction.py [config_yaml]
    $ python3 ../../scripts/assess_predictions.py [config_yaml]

The fisrt script to run is [`prepare_data.py`](/../scripts/README.md) in order to create tiles and labels files that will be then used by the object detector scripts. The `prepare_data.py` section of the _yaml_ configuration file is expected as follow:

    prepare_data.py:
        srs: "EPSG:2056"
        datasets:
            labels_shapefile: ../input/input-trne/[Label_Shapefile]
      output_folder: ../output/output-trne
      zoom_level: [z]

Set the path to the desired label shapefile (AOI) (create a new folder: /proj-dqry/input/input-trne/ to the project). For training, the **labels_shapefile** corresponds to polygons of quarries defined in the TLM and manually reviewed by experts. It constitutes the ground truth.

For the quarries example:

	[Label_Shapefile] = tlm-hr-trn-topo.shp

Specify the zoom level _z_. The zoom level will act on the tiles size (and tiles number) and on the pixel resolution. We advise to use zoom level between 16 (1.6 m/px) and 17 (0.8 m/px).
The **srs** key provides the working geographical frame to ensure all the input data are compatible together.

Then, by running `generate_tilesets.py` the images will be downloaded from a _WMTS_ according to the tiles characteristics defined previously. A _XYZ_ connector is used to access _SWISSIMAGE_ for a given year. Be careful to set the desired year in the url:

      https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.swissimage-product/default/[YEAR]/3857/{z}/{x}/{y}.jpeg

A **debug mode** can be activated in order to run the script on a sample of images to perform some test for instance. The number of images sampled is hard-coded in the script. The images will be split in three datasets: _trn_, _tst_ and _val_ to perform the training. The ground truth with reviewed labels is provided as input.

The algorithm is trained with the script `train_model.py` calling detectron2 algorithm. For object detection, instance segmentation is used `COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_1x.yaml`. The model characteristics can be tuned by modifying parameters in `detectron2_config_dqry.yaml`.
Especially pay attention to the **MAX_ITER** and **STEPS** values (Last **STEPS** < **MAX_ITER**). Choose a number of iterations to ensure robust model training. The model training evolution can be monitored with a `tensorboard`. The library `PyTorch` must be installed (installed and activated in the virtual environment). The validation loss curve can be visualized and the optimum iteration of the model, _i.e._ the iteration minimizing the validation loss curve can be identified. This iteration corresponds to the optimum and must be set as input trained model for `make_predictions.py` (model_weights: pth_file:./logs/[chosen model].pth). The optimum is dependent on the zoom level and the number of tiles involved. The file `model_final.pth` corresponds to the last iteration recorded during the training procedure. Trained model at different iterations are saved in folder **logs**.


    tensorboard --logdir <logs folder path>/logs
Open the following link with a web browser: `http://localhost:6006`

Predictions come with a confidence score [0 to 1]. Predictions with low score can be discarded by setting a threshold value for `make_predictions.py` script **score_thd** (verify the influence of threshold changing on final prediction). 
Finally, the detection capabilities of the model are evaluated with `assess_prediction.py` by computed metrics, _precision_, _recall_ and _f1_ score based on the inventory of TP, FP and FN detections. The predictions obtained are compared with the Ground Truth labels.

- Output

Finally we obtained the following results in the folder /proj-dqry/output/output-trne/:

- `*_images`: folders containing downloaded images splitted to the different datasets (all, train, test, validation)
- `sample_tagged_images`: folder containing sample of tagged images and bounding boxes
- `logs`: folder containing the files relative to the model training
- `tiles.geojson`: tiles polygons obtained for the given AOI
- `labels.geojson`: labels polygons obtained for the given GT
- `*_predictions.geojson`: detection polygons obtained for the different datasets (train, test, validation)
- `img_metadata.json`: images metadata file
- `clipped_labels.geojson`: labels polygons clipped according to tiles
- `split_aoi_tiles.geojson`: tiles polygons sorted according to the dataset where it belongs  
- `COCO_*.json`: COCO annotations for each image of the datasets
- `*_predictions_at_0dot*_threshold.pkl`: serialized pickle file of the prediction shapes for the different datasets and filtered by prediction score value (from 0 to 1). The score value can be customized in the config _yaml_ file `score_thd` for `make_prediction.py` script (verify the influence of threshold changing on final prediction).
-`*.html`: plots to evaluate the prediction results with metrics values (precision, recall, f1) and TP, FP and FN values

### Prediction

- Working directory

The working directory can be modified but by default is:

	$ cd /proj-dqry/config/

- Config and input data

Two configuration files are provided in `proj-dqry`:

	[config_yaml] = config-prd.yaml
	[logging_config] = logging.conf

The configuration _yaml_ has been set for the object detector workflow by reading the dedicated section. Verify and adapt, if required, the input and output paths.

-Run scripts

The prediction of objects requires the use of `object-detector` scripts. The workflow is processed in following way:

    $ python3 ../scripts/prepare_data.py [config_yaml]
    $ python3 ../../scripts/generate_tilesets.py [config_yaml]
    $ python3 ../../scripts/make_prediction.py [config_yaml]
    $ python3 ../../scripts/assess_predictions.py [config_yaml]

The first script to run is [`prepare_data.py`](/../scripts/README.md) in order to create tiles and labels files that will be then used by the object detector scripts. The `prepare_data.py` section of the _yaml_ configuration file is expected as follow:

    prepare_data.py:
        srs: "EPSG:2056"
        datasets:
            labels_shapefile: ../input/input-trne/[AOI_Shapefile]
      output_folder: ../output/output-prd
      zoom_level: [z]

Set the path to the desired label shapefile (AOI) (create a new folder: /proj-dqry/input/input-prd/ to the project). For prediction, the **labels_shapefile** corresponds to the AOI on which the object detection must be performed. It can be the whole Switzerland or part of it such as the footprint where SWISSIMAGE has been acquired for a given year.  

For the quarries example:

	[Label_Shapefile] = swissimage_footprint_[year].shp

Specify the zoom level _z_. The zoom level will act on the tiles size (and tiles number) and on the pixel resolution. We advise using zoom levels between 16 (1.6 m/px) and 17 (0.8 m/px). The zoom level should be the same as the used model has been trained.
The **srs** key provides the working geographical frame to ensure all the input data are compatible together.

Then, by running `generate_tilesets.py` the images will be downloaded from a _WMTS_ according to the tiles characteristics defined previously. A _XYZ_ connector is used to access _SWISSIMAGE_ for a given year. Be careful to set the desired year in the url:

      https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.swissimage-product/default/[YEAR]/3857/{z}/{x}/{y}.jpeg

A **debug mode** can be activated in order to run the script on a sample of images to perform some test for instance. The number of images sampled is hard-coded in the script. Inference predictions are performed (no Ground Truth data provided). One dataset will be defined (_oth_).

The object predictions are computed with a previously trained model. Copy the desired `logs_*` folder obtained during the 'Training and Evaluation' workflow into the folder proj-dqry/input/input-prd/.

  	model_weights: pth_file: '../../input/input-prd/logs/model_*.pth'

Choose the relevant `model_*.pth` file, _i.e._ the one minimizing the validation loss curve (see above 'Training and Evaluation'/Run scripts).

Predictions come with a confidence score [0 to 1]. Predictions with low score can be discarded by setting a threshold value for `make_predictions.py` script **score_thd**. Verify the influence of threshold changing on final prediction. For quarry project it is advised to not use large value. 
Finalize the process by running `assess_prediction.py` providing the final detection product.


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
- `oth_predictions_at_0dot*_threshold.pkl`: serialized pickle file of the prediction shapes filtered by prediction score value (from 0 to 1). The score value can be customized in the config _yaml_ file `score_thd` for `make_prediction.py` script. 

- Post-processing

The object detection output (`oth_predictions.geojson`) obtained via the `object-detector` scripts needs to be filtered to discard false detections and improve the aesthetic of the polygons (merge polygons belonging to a single quarry). The script [`prediction_filter.py`](/../script/README.md) allows to extract the prediction out of the detector _geojson_ based on a series of provided threshold values.

The `prediction_filter.py` is run as follow:

- Working directory

The working directory can be modified but is by default:

	$ cd /proj-dqry/config/
    
- Config and input data

	[config_yaml] = config-prd.yaml

The script expects a prediction _geojson_ (`oth_prediction.geojson` obtained with `assess_prediction.py`) file with all geometries containing a _score_ value normalized in _[0,1]_. The `prediction_filter.py` section of the _yaml_ configuration file is expected as follows. Paths and threshold values must be adapted:

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

-**distance**: two polygons that are close to each other can be considered to belong to the same quarry. Those polygons can be merged into a single one. By default the buffer value is set to 10 m.

-**area**: small area polygons can be discarded assuming a quarry has a minimal area. The default value is set to 2000 m2.

-**output**: provide the path of the filtered polygons shapefile with prediction score preserved. The output file name will be formated as: `oth_prediction_filter_year-{year}_score-{score}_elevation-{elevation}_distance-{distance}_area-{area}.geojson`.


The script `prediction_filter.py` is run as follow:

    $ python3 ../scripts/prediction-filter.py [config_yaml]


### Detection monitoring

The 'Prediction' workflow computes object prediction on images acquired at different years. In order to monitor the detected object over years, the script [`detection_monitoring.py`](/../scripts/README.md) has been developped.

The `detection_monitoring.py` is run as follow:

- Working directory

The working directory can be modified but is by default:

    $ cd /proj-dqry/config/
    
- Config and input data

    [config_yaml] = config-dm.yaml 

The `detection_monitoring.py` section of the _yaml_ configuration file is expected as follow:

    detection_monitoring.py:  
    years: [YEAR1, YEAR2, YEAR3,...]       
    datasets:
        detection: ../input/input-dm/'oth_prediction_filter_year-{year}_score-[SCORE]_elevation-[elevation]_distance-[distance]_area-[area].geojson'  
    output_folder: ../output/output-dm
  
Paths must be adapted if necessary (create a new folder: /proj-dqry/input/input-prd/ to the project to copy the input files in it). The script takes as input a _geojson_ file (**oth_prediction_filter_year-{year}_[filters_list].geojson**) obtained previously with the script `prediction_filter.py` for different years. The list of years required for the object monitoring must be specified in _years_.

-Run scripts

The prediction of objects requires the use of `object-detector` scripts. The workflow is processed in following way:

    $ python3 ../scripts/detection_monitoring.py [config_yaml]


The outputs are a _geojson_ and _csv_ (**quarry_time**) files saving predictions over years with their caracteristics (ID_object, ID_feature, year, score, area, geometry). The prediction files computed for previous years and _quarry_times_ files can be found on the STDL kDrive (https://kdrive.infomaniak.com/app/drive/548133/files) with the following access path: /STDL/Common Documents/Projets/En_cours/Quarries_TimeMachine/03_Results/Detection_monitoring/

### Plots

Script to draw basic plots is provided with [`plots.py`](/../scripts/README.md).

- Working directory

The working directory can be modified but is by default:

	$ cd /proj-dqry/config/

- Config and input data

	[config_yaml] = config-dm.yaml

The `plots.py` section of the _yaml_ configuration file is expected as follow:

	plots.py:  
	object_id: [ID_OBJECT1, ID_OBJECT2, ID_OBJECT3,...]
	plots: ['area-year']
	datasets:
    	detection: ../output/output-dm/quarry_times.geojson
	output_folder: ../output/output-dm/plots

Paths must be adapted if necessary. The script takes as input a `quarry_times.geojson` file produced with the script `detection_monitoring.py`. The list of object_id is required and the type of plot as well. So far only 'area-year' plot is available. Additional types of plots can be added in the future.

-Run scripts

	$ python3 ../scripts/prediction-filter.py [config_yaml]

## Global workflow
    
Following the end-to-end workflow can be run by issuing the following list of commands:

    $ cd proj-dqry/
    $ python3 -m venv <dir_path>/[name of the virtual environment]
    $ source <dir_path>/[name of the virtual environment]/bin/activate
    $ pip install -r requirements.txt

    $ mkdir input
    $ mkdir input-trne
    $ mkdir input-prd
    $ cd proj-dqry/config/

**Training and evaluation**: copy the required input files (labels shapefile) to **input-trne**

    $ python3 ../scripts/prepare_data.py config-trne.yaml
    $ python3 ../../scripts/generate_tilesets.py config-trne.yaml
    $ python3 ../../scripts/train_model.py config-trne.yaml
    $ python3 ../../scripts/make_prediction.py config-trne.yaml
    $ python3 ../../scripts/assess_predictions.py config-trne.yaml

**Predictions**: copy the required input files (AOI shapefile and trained model) to **input-prd**

    $ python3 ../scripts/prepare_data.py config-prd.yaml
    $ python3 ../../scripts/generate_tilesets.py config-prd.yaml
    $ python3 ../../scripts/make_prediction.py config-prd.yaml
    $ python3 ../../scripts/assess_predictions.py config-prd.yaml
    $ python3 ../scripts/prediction-filter.py config-prd.yaml 

**Object Monitoring**: copy the required input files (labels shapefile) to **input-dm**

    $ python3 ../scripts/detection_monitoring.py config-dm.yaml
    $ python3 ../scripts/plots.py config-dm.yaml
