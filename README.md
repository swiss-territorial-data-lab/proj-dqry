## Overview

This set of scripts and configuration files are related to the _quarry/exploitation sites_ detection case. The detector is initially trained on _swissimage_ from _swisstopo_ using the _TLM_ data of _swisstopo_ for the labels.

The worflow is defined in two disctinct procedures:
* the Training and Evaluation procedure allowing to train the detection model on a given dataset and evaluated to ground truth dataset examined by domain experts.
* the Prediction procedure performing detection of quarries in a given dataset thanks to the previously trained model.

The quarry are detected with the tools developped in `object-detector`. 

_(to be improved)_


## Hardware and OS requirements

The entire workflow has been run with Ubuntu 20.04 OS on a GPU machine with 32 Gbits RAM. The main limitation is the number of tiles to proceed. The provided requirements stand for a zoom level equal to or below 16 and for an AoI corresponding to SWISSIMAGE acquisition footprints (about a third of Switzerland surface max). For higher zoom level and/or a larger AoI, the number of tiles to process might lead to memory saturation. In this case either a more powerful machine will be required, or the AoI will need to be subdivided in a smaller area and the final predictions will be merged at the end.

## Python libraries

The scripts have been developed by importing Python3 libraries that are listed in `requirements.in` and `requirements.txt`. Before starting to run scripts make sure the required Python libraries that have been used during the code development are installed, otherwise incompatibilities and errors could occur. A clean method to install Python libraries is to work with a virtual environment preserving the package dependencies.

* if not already done, create a dedicated Python virtual environment:
	    
      python3 -m venv <dir_path>/[name of the virtual environment]

* activate the virtual environment:

      source <dir_path>/[name of the virtual environment]/bin/activate

* install the required Python packages into the virtual environment:

      pip install -r requirements.txt

The requirements.txt file used for the quarries detection can be found in the `proj-dqry` repository. 

* deactivate the virtual environment if not used anymore

      deactivate


## Required input data

The input data for the ‘Training and Evaluation’ and ‘Prediction’ workflow for the quarry detection project are stored on the STDL kDrive (https://kdrive.infomaniak.com/app/drive/548133/files) with the following access path: /STDL/Common Documents/Projets/En_cours/Quarries_TimeMachine/02_Data/

In this main folder you can find subfolders:
*	DEM
    -	`swiss-srtm.tif`: DEM (spatial resolution about 25 m/px) of Switzerland produced from SRTM instrument (https://doi.org/10.5066/F7PR7TFT). The raster is used to filter the quarry detection * Learning models
    - `logs`: folder containing trained detection models obtained during the model training phase using Ground Truth data. The learning characteristics of the algorithm can be visualized using tensorboard (see below in Processing/Run scripts). Models at several epochs have been saved. The optimum model minimize the validation loss curve across epochs. This model is used to perform the ‘Prediction’ phase. The algorithm has been trained on SWISSIMAGE data with zoom levels from 15 (3.2 m/px) to 18 (0.4 m/px). For each zoom level subfolder a file `metrics.txt` is provided summing-up the metrics values (precision, recall and f1-score) obtained for the optimized model epoch. The user can either used the already trained model or performed is own model training by running the ‘Training and Evaluation’ workflow and use the produced model to detect quarries.

* Shapefiles
    -	`quarry_label_tlm_revised`: polygons shapefile of the quarries labels (TLM data) reviewed by the domain experts. This file has been used to train and assess the automatic detection algorithms = Ground Truth.
    - `swissimage_footprints_shape_year_per_year`: original SWISSIMAGE footprints and processed polygons border shapefiles for every SWISSIMAGE acquisition year.
    - `switzerland_border`: polygon shapefile of the Switzerland border. 

*	SWISSIMAGE
    - `Explanation.txt`: file explaining the main characteristics of SWISSIMAGE and the references links (written by R. Pott).


## Workflow

This section detail the procedure and the command lines to execute in order to run the workflows.

### Training and Evaluation

- Working directory and paths

By default the working directory is: 

    $ cd proj-dqry/config/

- Config and input data

Configuration files are required:

    [logging_config] = logging.conf

The logging format file can be used as provided. The configuration _YAML_ has been set for the object detector workflow by reading dedicated section. It has to be adapted in terms of input and output location and files.

    [config_yaml] = config-trne.yaml 

In the config file verify (and custom) the paths and set the paths to the input data to the tiles shapefile (tiling) and to the AoI shapefile (label).

In the config file verify (and custom) the paths of input and output. The `prepare_data.py` section of the _yaml_ configuration file is expected as follow:

    prepare_data.py:
        srs: "EPSG:2056"
        datasets:
            labels_shapefile: ../input/input-trne/[Label_Shapefile]
      output_folder: ../output/output-trne
      zoom_level: [z]

Set the path to the desired label shapefile (AoI) (create a new folder /proj-dqry/input/input-trne/). For the training, the labels correspond to polygons of quarries defined manually by experts. It constitute the ground truth. 

For the quarries example:

    [Label_Shapefile] = tlm-hr-trn-topo.shp

`prepare_data.py` set the tiles parameters for the tiling service request. XYZ connector is used to fetch images with wmts. wmts allows to request images for a given year and provides base tile of 256 px that can be combined according to the given zoom level z. x and y coordinates on a grid are defined for the given AOI and the zoom level. To avoid large computation time during the training phase, only tiles intersecting labels are kept. 

The _srs_ key provides the working geographical frame to ensure all the input data are compatible together.

- Run scripts

The training and detection of objects requires the use of `object-detector` scripts. The workflow is processed in following way:

    $ python3 ../scripts/prepare_data.py [config_yaml]
    $ python3 [object-detector_path]/scripts/generate_tilesets.py [config_yaml]
    $ python3 [object-detector_path]/scripts/train_model.py [config_yaml]
    $ python3 [object-detector_path]/scripts/make_prediction.py [config_yaml]
    $ python3 [object-detector_path]/scripts/assess_predictions.py [config_yaml]

In between the `train_model.py` and `make_prediction.py` script execution, the output of the detection model training must be checked and the optimum model, i.e. the one minimizing the validation loss curve, must be chosen (obtained for a given iteration number) and set as input (model_weights: pth_file:./logs/[chosen model].pth) to make the prediction. For the quarry example the optimum is obtained for a learning iteration around 2000. The file model_final correspond to the last iteration recorded during the training procedure.

The validation loss curve can be visualized with `tensorboard` 

    tensorboard --logdir [logs folder]
And open the following link with a web browser: `http://localhost:6006`

- Output

Finally we obtained the following results in the folder /proj-dqry/output/output-trne/:

_(to be completed)_

### Prediction

- Config and input data

Two config files are provided in `proj-dqry`:

    [config_yaml] = config-prd.yaml 
    [logging_config] = logging.conf

In the config file verify (and custom) the paths of input and output. The `prepare_data.py` section of the _yaml_ configuration file is expected as follow:

    prepare_data.py:
        srs: "EPSG:3857"
        datasets:
            labels_shapefile: ../input/input-trne/[AOI_Shapefile]
      output_folder: ../output/output-prd
      zoom_level: [z]

Set the path to the desired label shapefile (AOI) (create a new folder /proj-dqry/input/input-prd/). For the prediction, the label correspond to the AOI on which the object detection must be performed. It can be the whole Switzerland or part of it such as the area where SWISSIMAGE has been acquired for a given year. 

For the quarries example:

    [Label_Shapefile] = swissimage_footprint_2020.shp

`prepare_data.py` set the tiles parameters for the tiling service request. XYZ connector is used to fetch images with wmts. wmts allows to request images for a given year and provides base tile of 256 px that can be combined according to the given zoom level z. x and y coordinates on a grid are defined for the given AOI and the zoom level. To avoid large computation time during the prediction phase, perform some tests on the zoom level (and therefore on the tile size and resolution).

The _srs_ key provides the working geographical frame to ensure all the input data are compatible together.

The object detection use a trained model. Copy the `logs` folder obtained during the Training and Evaluation procedure into the folder proj-dqry/input/input-prd/.

      model_weights: pth_file = logs

Choose the relevant log.pth file, i.e. the one minimizing the validation loss curve (see above Training and Evaluation/Run scripts). 

- Working directory and paths

By default the working directory is:

    $ cd /proj-dqry/config/

In the config file verify (and custom) the paths.

-Run scripts

The prediction of objects requires the use of `object-detector` scripts. The workflow is processed in following way:

    $ python3 ../scripts/prepare_data.py [yaml_config]
    $ python3 [object-detector_path]/scripts/generate_tilesets.py [config_yaml]
    $ python3 [object-detector_path]/scripts/make_prediction.py [config_yaml]
    $ python3 [object-detector_path]/scripts/assess_predictions.py [config_yaml]


- Output:

Finally we obtained the following results stored in the folder /proj-dqry/output/output-prd/:

_(to be completed)_

- Post-processing

The quarry prediction output as a polygons shapefile needs a filtering procedure to discard false detections and improve the aesthetic of the polygons (merge polygons belonging to a single quarry). This is performed the script `prediction_filter.py`:

    $ python3 ../post-processing/prediction-filter.py [config_yaml]

The `prediction_filter.py` section of the _yaml_ configuration file is expected as follow:

    prediction_filter.py:
        input: ../output/output-prd/oth_predictions.geojson 
        dem: ../input/DEM/swiss-srtm.tif 
        elevation: 1155.0   
        score: 0.96
        distance: 8 
        area: 1728.0  
        output: ../output/output-prd/oth_prediction_score-{score}_area-{area}_elevation-{elevation}_distance-{distance}.geojso

-input: indicate path to the input geojson file that needs to be filtered, i.e. oth_predictions.geojson

-dem: indicate the path to the DEM of Switzerland. A SRTM derived product is used and can be found in the STDL kDrive. A threshold elevation is used to discard detection above the given value. 

-elevation: altitude above which prediction are discard. Indeed 1st tests have shown numerous false detection due to snow cover area (reflectance value close to bedrock reflectance) or mountain bedrock exposure. By default the threshold elevation has been set to 1155.0 m.

-score: each polygon comes with a confidence score given by the prediction algorithm. Polygons with low scores can be discarded. By default the value is set to 0.96.

-distance: two polygons that are close to each other can be considered to belong to the same quarry. Those polygons can be merged into a single one. By default the buffer value is set to 8 m.

-area: small area polygons can be discarded assuming a quarry has a minimal area. The default value is set to 1728 m2.

-output: provide the path and name of the filtered polygons shapefile

### Prediction monitoring

- Config and input data

    [config_yaml] = config-dm.yaml 

- Working directory and paths

By default the working directory is:

    $ cd /proj-dqry/config/

In the config file verify (and custom) the paths.

-Run scripts

    $ python3 ../scripts/plots.py [config_yaml]

### Plots

- Config and input data

    [config_yaml] = config-dm.yaml 

- Working directory and paths

By default the working directory is:

    $ cd /proj-dqry/config/

In the config file verify (and custom) the paths.

-Run scripts

    $ python3 ../scripts/prediction-filter.py [config_yaml]

## Copyright and License

The pre-processing and post-processing scripts originate from the git repository `detector-interface`
  
**detector-interface** - Nils Hamel, Adrian Meyer, Huriel Reichel, Alessandro Cerioni <br >
Copyright (c) 2020-2022 Republic and Canton of Geneva

This program is licensed under the terms of the GNU GPLv3. Documentation and illustrations are licensed under the terms of the CC BY 4.0.