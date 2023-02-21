## Overview

This project provides a suite of scripts and configuration files to perform quarries automatic detections with georeferenced raster images with Deep Learning method. For object detection, tools developed in `object-detector` git repository are used.

The procedure is defined in three distinct workflows:
1. **Training and Evaluation** workflow allowing to train and evaluate the detection model with a customed dataset reviewed by domain experts and constituing the ground truth. The detector is initially trained on _SWISSIMAGE 10 cm_ mosaic of 2020 ([swisstopo](https://www.swisstopo.admin.ch/fr/geodata/images/ortho/swissimage10.html)), using the _TLM_ data of _swisstopo_ as Ground Truth.
2. **Prediction** workflow performing inference detection of quarries in a given image dataset (_SWISSIMAGE_ acquisition year) thanks to the previously trained model.
3. **Detection monitoring** workflow tracking quarry evolution over years.

A global documentation of the project can be found [here](https://github.com/swiss-territorial-data-lab/stdl-tech-website/tree/master/docs/PROJ-DQRY). 

**TOC**
- [Requirements](#requirements)
- [Python libraries](#python-libraries)
- [Files structure](#files-structure)
- [Global workflow](#global-workflow)
- [Copyright and License](#copyright-and-license)

## Requirements

Workflows have been run with Ubuntu 20.04 OS on a 32 GiB RAM machine with 15GiB GPU. The main limitation is the number of tiles to proceed and the amount of prediction. The provided requirements stand for a zoom level equal to or below 17 and for an AOI corresponding to SWISSIMAGE acquisition footprints (about a third of Switzerland surface max). For higher zoom level and/or a larger AOI, the number of data to process might lead to memory saturation. In this case either a more powerful machine is be required, or the AOI needs to be subdivided in a smaller area.

## Python libraries

The scripts have been developed with Python 3.8 by importing libraries that are listed in `requirements.in` and `requirements.txt`. Before starting to run scripts make sure the required Python libraries that have been used during the code development are installed, otherwise incompatibilities and errors might occur. A clean method to install Python libraries is to work with a virtual environment preserving the package dependencies.

## Files structure

The `proj-dqry` repository (https://github.com/swiss-territorial-data-lab/proj-dqry) contains **scripts** to prepare and post-process the datasets:

1. `prepare_data.py` 
2. `prediction_filter.py` 
3. `detection_monitoring.py` 
4. `plots.py` 
5. `batch_process.sh` 

The description of each script can be found [here](/scripts/README.md).  

In addition, the object detection itself is performed by tools developed in `object-detector` git repository. The description of the scripts used are presented [here](https://github.com/swiss-territorial-data-lab/object-detector)

The folders/files structure of the project is orgranised as follow. The path names can be customed by the end-user and * indicates number value that can vary:

<pre>.
├── config
│   ├── input-dm.yaml
│   ├── input-prd.template.yaml
│   ├── input-prd.yaml
│   ├── input-trne.yaml
│   ├── detectron2_config_dqry.yaml
│   ├── logging.conf
│   └── README.md
├── images
│   ├── prediction_filter_after.png
│   ├── prediction_filter_before.png
│   ├── quarries_area-year.png
│   ├── quarry_monitoring_strategy.png
│   └── tiles_examples.png
├── input
│   ├── input-dm
│   │   ├── oth_prediction_at_0dot*_threshold_year-*_score-0dot*_area-*_elevation-*_distance-*.geojson # Final filtered predictions file for a given year.
│   ├── input-prd
│   |   ├── z*
│   │   │   ├── logs
│   │   │   │   ├── inference
│   │   │   │   ├── events.out.tfevents.*.vm-gpu-02.*.0
│   │   │   │   ├── last_checkpoint
│   │   │   │   ├── metrics.json
│   │   │   │   ├── model_*.pth
│   │   │   │   └── model_final.pth
│   │   │   │       ├── coco_instances_results.json
│   │   │   │       └── instances_predictions.pth
│   │   │   ├── lr.svg
│   │   │   ├── metrics_ite-*
│   │   │   ├── precision_vs_recall.html
│   │   │   ├── total_loss.svg
│   │   │   ├── trn_metrics_vs_threshold.html
│   │   │   ├── trn_TP-FN-FP_vs_threshold.html
│   │   │   ├── tst_metrics_vs_threshold.html
│   │   │   ├── tst_TP-FN-FP_vs_threshold.html
│   │   │   ├── val_metrics_vs_threshold.html
│   │   │   ├── val_TP-FN-FP_vs_threshold.html
│   │   │   └──validation_loss.svg
│   │   ├── swissimage_footprint_*.prj
│   │   ├── swissimage_footprint_*.shp
│   │   └── swissimage_footprint_*.shx
│   └── input-trne
│       ├── tlm-hr-trn-topo.prj
│       ├── tlm-hr-trn-topo.shp
│       └── tlm-hr-trn-topo.shx
├── output
│   ├── output-dm
│   │   └── oth_prediction_at_0dot*_threshold_year-*_score-0dot*_area-*_elevation-*_distance-*
│   │   │   ├── plots
│   │   │   │   └── quarry_area.png
│   │   │   ├── quarry_tiles.csv
│   │   │   └── quarry_times.geojson
│   ├── output-prd
│   │   ├── all-images
│   │   │   ├── z_y_x.json
│   │   │   └── z_y_x.tif
│   │   ├── oth-images
│   │   │   └── z_y_x.tif
│   │   ├── sample_tagged_images
│   │   │   └── oth_pred_z_y_x.png
│   │   ├── COCO_oth.json
│   │   ├── img_metadata.json
│   │   ├── labels.json
│   │   ├── oth_prediction_at_0dot*_threshold_year-*_score-0dot*_area-*_elevation-*_distance-*.geojson
│   │   ├── oth_predictions_at_0dot*_threshold.gpkg
│   │   ├── split_aoi_tiles.geojson
│   │   └── tiles.geojson
│   └── output-trne
│   │   ├── all-images
│   │   │   ├── z_y_x.json
│   │   │   └── z_y_x.tif
│   │   ├── logs
│   │   │   ├── inference
│   │   │   │   ├── coco_instances_results.json
│   │   │   │   └── instances_predictions.pth
│   │   │   ├── events.out.tfevents.*.vm-gpu-02.*.0
│   │   │   ├── last_checkpoint
│   │   │   ├── metrics.json
│   │   │   ├── model_*.pth
│   │   │   └── model_final.pth
│   │   ├── sample_tagged_images
│   │   │   └── pred_z_y_x.png
│   │   │   └── tagged_z_y_x.png
│   │   │   └── trn_pred_z_y_x.png
│   │   │   └── tst_pred_z_y_x.png
│   │   │   └── val_pred_z_y_x.png
│   │   ├── trn-images
│   │   │   └── z_y_x.tif
│   │   ├── tst-images
│   │   │   └── z_y_x.tif
│   │   ├── val-images
│   │   │   └── z_y_x.tif
│   │   ├── clipped_labels.geojson
│   │   ├── COCO_trn.json
│   │   ├── COCO_tst.json
│   │   ├── COCO_val.json
│   │   ├── img_metadata.json
│   │   ├── labels.json
│   │   ├── metrics_ite-*
│   │   ├── lr.svg
│   │   ├── precision_vs_recall.html
│   │   ├── split_aoi_tiles.geojson
│   │   ├── tagged_predictions.gpkg
│   │   ├── tiles.json
│   │   ├── total_loss.svg
│   │   ├── trn_metrics_vs_threshold.html
│   │   ├── trn_predictions_at_0dot*_threshold.gpkg
│   │   ├── trn_TP-FN-FP_vs_threshold.html
│   │   ├── tst_metrics_vs_threshold.html
│   │   ├── tst_predictions_at_0dot*_threshold.gpkg
│   │   ├── tst_TP-FN-FP_vs_threshold.html
│   │   ├── val_metrics_vs_threshold.html
│   │   ├── val_predictions_at_0dot*_threshold.gpkg
│   │   ├── val_TP-FN-FP_vs_threshold.html
│   │   └── validation_loss.svg
├── scripts
│   └── batch_process.sh
│   └── detection_monitoring.py
│   └── plots.py
│   └── prediction_filter.py
│   └── prepare_data.py
│   └── README.md
├── .gitignore
├── LICENCE
├── README.md
├── requirements.in
└── requirements.txt
</pre>

 ## Global workflow
    
Following the end to end workflow can be run by issuing the following list of actions and commands:

Copy `proj-dqry` and `object-detector` repository in a same folder.  

    $ cd proj-dqry/
    $ python3 -m venv <dir_path>/[name of the virtual environment]
    $ source <dir_path>/[name of the virtual environment]/bin/activate
    $ pip install -r requirements.txt

    $ mkdir input
    $ mkdir input-trne
    $ mkdir input-prd
    $ mkdir input-dm
    $ cd proj-dqry/config/

Adapt the paths and input value of the configuration files accordingly.

**Training and evaluation**: copy the required input files (labels shapefile (tlm-hr-trn-topo.shp) and trained model is necessary (`z*/logs`)) to **input-trne** folder.

    $ python3 ../scripts/prepare_data.py config-trne.yaml
    $ python3 ../../object-detector/scripts/generate_tilesets.py config-trne.yaml
    $ python3 ../../object-detector/scripts/train_model.py config-trne.yaml
    $ tensorboard --logdir ../output/output-trne/logs

Open the following link with a web browser: `http://localhost:6006` and identified the iteration minimizing the validation loss curve and the selected model name (**pth_file**) in `config-trne` to run `make_predictions.py`. 

    $ python3 ../../object-detector/scripts/make_predictions.py config-trne.yaml
    $ python3 ../../object-detector/scripts/assess_predictions.py config-trne.yaml

**Predictions**: copy the required input files (AOI shapefile (`swissimage_footprint_[YEAR].shp`), trained model (`/z*/logs`) and DEM (`switzerland_dem_EPSG:2056.tif`)) to **input-prd** folder.

    $ python3 ../scripts/prepare_data.py config-prd.yaml
    $ python3 ../../object-detector/scripts/generate_tilesets.py config-prd.yaml
    $ python3 ../../object-detector/scripts/make_predictions.py config-prd.yaml
    $ python3 ../scripts/prediction-filter.py config-prd.yaml 

The workflow has been automatized and can be run for batch of years by running this command:

    $ ../scripts/batch_process.sh

**Object Monitoring**: copy the required input files (filtered prediction files (`oth_prediction_filter_year-{year}_[filters_list].geojson`)) to **input-dm** folder.

    $ python3 ../scripts/detection_monitoring.py config-dm.yaml
    $ python3 ../scripts/plots.py config-dm.yaml


## Copyright and License
 
**proj-dqry** - Nils Hamel, Adrian Meyer, Huriel Reichel, Clémence Herny, Shanci Li, Alessandro Cerioni, Roxane Pott <br >
Copyright (c) 2020-2022 Republic and Canton of Geneva

This program is licensed under the terms of the GNU GPLv3. Documentation and illustrations are licensed under the terms of the CC BY 4.0.