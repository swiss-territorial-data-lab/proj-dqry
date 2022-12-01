## Overview

This set of scripts and configuration files are related to the _quarry/exploitation sites_ detection case. The detector is initially trained on _swissimage_ from _swisstopo_ using the _TLM_ data of _swisstopo_ for the labels.

The worflow is defined in two disctinct procedures:
* the Training and Evaluation procedure allowing to train the detection model on a given dataset and evaluated to ground truth dataset examined by domain experts.
* the Prediction procedure performing detection of quarries in a given dataset thanks to the previously trained model.

The quarry are detected with the tools developped in `object-detector`. 

_(to be improved)_


## Python virtual environment

Before starting to run scripts make sure to work with the required Python libraries that have been used during the code development. This can be ensured by working with a virtual environment that will preserve the package dependencies.

* if not done already, create a dedicated Python virtual environment:
	    
      python3 -m venv <path>/[name of the virtual environment]

* activate the virtual environment:

      source <path>/[name of the virtual environment]/bin/activate

* install the required Python packages into the virtual environment:

      pip install -r requirements.txt

The requirements.txt file used for the quarries detection can be found in the `proj-dqry` repository. 

* deactivate the virtual environment if not used anymore

      deactivate


## Required input data

The input data for the ‘Training and Evaluation’ and ‘Prediction’ workflow for the quarry detection project are stored on the STDL kDrive (https://kdrive.infomaniak.com/app/drive/548133/files) with the following access path: /STDL/Common Documents/Projets/En_cours/Quarries_TimeMachine/02_Data/

In this folder you can find different folders:
*	DEM
    -	swiss-srtm.tif: DEM of Switzerland produced from SRTM instrument (_add reference and source_). The raster is used to filter the detection according to an elevation threshold.
* Learning models
    - logs: folder containing trained detection model at several learning iteration. They have been obtained during the model training phase. The optimum model minimizing the validation loss curve. The learning characteristics of the algorithm can be visualized using tensorboard (see below in Processing/Run scripts). The optimum model obtained during the ‘Training and Evaluation’ phase is used to perform the ‘Prediction’ phase. The algorithm has been trained on SWISSIMAGE data with a 1 m/px resolution.
* Shapefiles
    -	quarry_label_tlm_revised: polygons shapefile of the quarries labels (TLM data) reviewed by the domain experts. This file has been used to train and assess the automatic detection algorithms = Ground Truth.
    - swissimage_footprints_shape_year_per_year: original SWISSIMAGE footprints and processed polygons border shapefiles for every SWISSIMAGE acquisition year.
    - switzerland_border: polygon shapefile of the Switzerland border. 

*	SWISSIMAGE
    -	Explanation.txt: file explaining the main characteristics of SWISSIMAGE and the references links (written by R. Pott).


## Workflow

### Training and Evaluation

- Working directory and paths

By default the working directory is: 

    $ cd proj-dqry/config/

- Config and input data

Two config files are provided in `proj-dqry`:

    [config_yaml] = config-trne.yaml 
    [logging_config] = logging.conf

The logging format file can be used as provided. The configuration _YAML_ has been set for the object detector workflow by reading dedicated section. It has to be adapted in terms of input and output location and files.

In the config file verify (and custom) the paths and set the paths to the input data to the tiles shapefile (tiling) and to the AoI shapefile (label).

In the config file verify (and custom) the paths of input and output. The `prepare_data.py` section of the _yaml_ configuration file is expected as follow:

    prepare_data.py:
        srs: "EPSG:2056"
        datasets:
            labels_shapefile: ../input/input-trne/[Label_Shapefile]
      output_folder: ../output/output-trne
      zoom_level: [z]

Set the path to the desired label shapefile (AOI) (create a new folder /proj-dqry/input/input-trne/). For the training, the labels correspond to polygons of quarries defined manually by experts. It constitute the ground truth. 

For the quarries example:

    [Label_Shapefile] = tlm-hr-trn-topo.shp

`prepare_data.py` set the tiles parameters for the tiling service request. XYZ connector is used to fetch images with wmts. wmts allows to request images for a given year and provides base tile of 256 px that can be combined according to the given zoom level z. x and y coordinates on a grid are defined for the given AOI and the zoom level. To avoid large computation time during the training phase, only tiles intersecting labels are kept. 

The _srs_ key provides the working geographical frame to ensure all the input data are compatible together.

- Run scripts

The training and detection of objects requires the use of `object-detector` scripts. The workflow is processed in following way:

    $ python3 prepare_data.py --config [config_yaml] --logger [logging_config]
    $ python3 [object-detector_path]/scripts/generate_tilesets.py [yaml_config]
    $ cd [output_directory]
    $ tar -cvf images-[image_size].tar COCO_{trn,val,tst}.json && \
      tar -rvf images-[image_size].tar {trn,val,tst}-images-[image_size] && \
      gzip < images-[image_size].tar > images-[image_size].tar.gz && \
      rm all-images-[image_size].tar
    $ cd -
    $ cd [process_directory]
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

    $ python3 prepare_data.py --config [yaml_config] --logger [logging_config]
    $ python3 [object-detector_path]/scripts/generate_tilesets.py [config_yaml]
    $ cd [output_directory]
    $ tar -cvf images-[image_size].tar COCO_{trn,val,tst}.json && \
      tar -rvf images-[image_size].tar {trn,val,tst}-images-[image_size] && \
      gzip < images-[image_size].tar > images-[image_size].tar.gz && \
      rm all-images-[image_size].tar
    $ cd -
    $ cd [process_directory]
    $ python3 [object-detector_path]/scripts/make_prediction.py [config_yaml]
    $ python3 [object-detector_path]/scripts/assess_predictions.py [config_yaml]


- Output:

Finally we obtained the following results stored in the folder /proj-dqry/output/output-prd/:

_(to be completed)_

- Post-processing

The quarry prediction output as a polygons shapefile needs a filtering procedure to discard false detections and improve the aesthetic of the polygons (merge polygons belonging to a single quarry). This is performed the script `prediction_filter.py`:

    $ python3 [object-detector_path]/post-processing/prediction-filter.py [config_yaml]

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

## Copyright and License

The pre-processing and post-processing scripts originate from the git repository `detector-interface`
  
**detector-interface** - Nils Hamel, Adrian Meyer, Huriel Reichel, Alessandro Cerioni <br >
Copyright (c) 2020-2022 Republic and Canton of Geneva

This program is licensed under the terms of the GNU GPLv3. Documentation and illustrations are licensed under the terms of the CC BY 4.0.