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
- [Workflow](#workflow)
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
├── config                                          # configurations files folder
│   ├── input-dm.yaml                               # detection monitoring workflow configuration file
│   ├── input-prd.template.yaml                     # prediction workflow for several years configuration file template
│   ├── input-prd.yaml                              # prediction workflow configuration file
│   ├── input-trne.yaml                             # training and evaluation workflow configuration file
│   ├── detectron2_config_dqry.yaml                 # detectron 2 configuration file 
│   ├── logging.conf                                # logging configuration
│   └── README.md                                   # detailled description to run workflows 
├── images                                          # storage of images used in README.md files 
│   ├── prediction_filter_after.png
│   ├── prediction_filter_before.png
│   ├── quarries_area-year.png
│   ├── quarry_monitoring_strategy.png
│   └── tiles_examples.png
├── input                                           # inputs folders. Have to be created by the end-user 
│   ├── input-dm                                    # detection monitoring input 
│   │   ├── oth_prediction_at_0dot*_threshold_year-*_score-0dot*_area-*_elevation-*_distance-*.geojson # final filtered predictions file for a given year. Copy output of `prediction_filter.py`  
│   ├── input-prd                                   # prediction inputs
│   |   ├── z*                                      # trained model for a given zoom level z, _i.e._ z16 
│   │   │   ├── logs                                # folder containing trained model 
│   │   │   │   ├── inference
│   │   │   │   │   ├── coco_instances_results.json
│   │   │   │   │   └── instances_predictions.pth
│   │   │   │   ├── events.out.tfevents.*.vm-gpu-02.*.0
│   │   │   │   ├── last_checkpoint
│   │   │   │   ├── metrics.json                    # computed metrics for the given interval and bin size
│   │   │   │   ├── model_*.pth                     # saved trained model at a given iteration * 
│   │   │   │   └── model_final.pth                 # last iteration saved model 
│   │   │   │
│   │   │   ├── lr.svg                              # learning rate plot (downloaded from tensorboard)
│   │   │   ├── metrics_ite-*                       # metrics value at threshold value for the optimum model iteration * (saved manually after run assess_prediction.py) 
│   │   │   ├── precision_vs_recall.html            # plot precision vs recall
│   │   │   ├── total_loss.svg                      # total loss plot (downloaded from tensorboard)
│   │   │   ├── trn_metrics_vs_threshold.html       # plot metrics of train DS (r, p, f1) vs threshold values
│   │   │   ├── trn_TP-FN-FP_vs_threshold.html      # plot train DS TP-FN-FP vs threshold values threshold values
│   │   │   ├── tst_metrics_vs_threshold.html       # plot metrics of test DS (r, p, f1) vs threshold values
│   │   │   ├── tst_TP-FN-FP_vs_threshold.html      # plot test DS TP-FN-FP vs threshold valuesthreshold values
│   │   │   ├── val_metrics_vs_threshold.html       # plot valiadation DS metrics (r, p, f1) vs threshold values
│   │   │   ├── val_TP-FN-FP_vs_threshold.html      # plot validation DS TP-FN-FP vs threshold values
│   │   │   └──validation_loss.svg                  # validation loss curve (downloaded from tensorboard)
│   │   ├── swissimage_footprint_*.prj              # shapefile projection of the AOI for a given year *
│   │   ├── swissimage_footprint_*.shp              # shapefile of the AOI for a given year *              
│   │   └── swissimage_footprint_*.shx              # shapefile indexes of the AOI for a given year *
│   └── input-trne                                  # training and evaluation inputs
│       ├── tlm-hr-trn-topo.prj                     # shapefile projection of the labels
│       ├── tlm-hr-trn-topo.shp                     # shapefile of the labels 
│       └── tlm-hr-trn-topo.shx                     # shapefile indexes of the labels
├── output                                          # outputs folders. Created automatically by running scripts
│   ├── output-dm                                   # detection monitoring outputs 
│   │   └── oth_prediction_at_0dot*_threshold_year-*_score-0dot*_area-*_elevation-*_distance-*   # final filtered predictions file for a given year
│   │       ├── plots                               # plots storage 
│   │       │   └── quarry_area.png                 # quarry area vs year plot  
│   │       ├── quarry_tiles.csv                    # table containing prediction (id, geometry, area, year...) for a list of given Year. Overlapping predictions between years display the same unique ID 
│   │       └── quarry_times.geojson                # geometry file containing prediction (id, geometry, area, year...) for a list of given Year. Overlapping predictions between years display the same unique ID 
│   ├── output-prd                                  # prediction outputs 
│   │   ├── all-images                              # images downloaded from wmts server (XYZ values)
│   │   │   ├── z_y_x.json
│   │   │   └── z_y_x.tif
│   │   ├── oth-images                              # tagged images other DataSet
│   │   │   └── z_y_x.tif
│   │   ├── sample_tagged_images                    # examples of annoted prediction on images (XYZ values)
│   │   │   └── oth_pred_z_y_x.png
│   │   ├── COCO_oth.json                           # COCO annotations on other DS  
│   │   ├── img_metadata.json                       # images info
│   │   ├── labels.json                             # AOI geometries 
│   │   ├── oth_prediction_at_0dot*_threshold_year-*_score-0dot*_area-*_elevation-*_distance-*.geojson
│   │   ├── oth_predictions_at_0dot*_threshold.gpkg # prediction results at a given score threshold * in geopackage format
│   │   ├── split_aoi_tiles.geojson                 # labels shape clipped to tiles shape 
│   │   └── tiles.geojson                           # tiles geometries 
│   └── output-trne                                 # training and evaluation outputs  
│       ├── all-images                              # images downloaded from wmts server (XYZ values)
│       │   ├── z_y_x.json
│       │   └── z_y_x.tif
│       ├── logs                                    # folder containing trained model 
│       │   ├── inference
│       │   │   ├── coco_instances_results.json
│       │   │   └── instances_predictions.pth
│       │   ├── events.out.tfevents.*.vm-gpu-02.*.0
│       │   ├── last_checkpoint
│       │   ├── metrics.json                        # computed metrics for the given interval and bin size
│       │   ├── model_*.pth                         # saved trained model at a given iteration *
│       │   └── model_final.pth                     # last iteration saved model
│       ├── sample_tagged_images                    # examples of annoted prediction on images (XYZ values)
│       │   └── pred_z_y_x.png
│       │   └── tagged_z_y_x.png
│       │   └── trn_pred_z_y_x.png
│       │   └── tst_pred_z_y_x.png
│       │   └── val_pred_z_y_x.png
│       ├── trn-images                              # tagged images train DataSet  
│       │   └── z_y_x.tif
│       ├── tst-images                              # tagged images test DataSet
│       │   └── z_y_x.tif
│       ├── val-images                              # tagged images validation DataSet
│       │   └── z_y_x.tif
│       ├── clipped_labels.geojson                  # labels shape clipped to tiles shape 
│       ├── COCO_trn.json                           # COCO annotations on train DS
│       ├── COCO_tst.json                           # COCO annotations on test DS
│       ├── COCO_val.json                           # COCO annotations on validation DS
│       ├── img_metadata.json                       # images info
│       ├── labels.json                             # labels geometries
│       ├── metrics_ite-*                           # metrics value at threshold value for the optimum model iteration * (saved manually after run assess_prediction.py)
│       ├── lr.svg                                  # learning rate plot (downloaded from tensorboard)
│       ├── precision_vs_recall.html                # plot precision vs recall
│       ├── split_aoi_tiles.geojson                 # tagged DS tiles 
│       ├── tagged_predictions.gpkg                 # tagged predictions (TP, FP, FN) 
│       ├── tiles.json                              # tiles geometries
│       ├── total_loss.svg                          # total loss plot (downloaded from tensorboard)
│       ├── trn_metrics_vs_threshold.html           # plot metrics of train DS (r, p, f1) vs threshold values
│       ├── trn_predictions_at_0dot*_threshold.gpkg # prediction results for train DS at a given score threshold * in geopackage
│       ├── trn_TP-FN-FP_vs_threshold.html          # plot train DS TP-FN-FP vs threshold values
│       ├── tst_metrics_vs_threshold.html           # plot metrics of test DS (r, p, f1) vs threshold values
│       ├── tst_predictions_at_0dot*_threshold.gpkg # prediction results for test DS at a given score threshold * in geopackage
│       ├── tst_TP-FN-FP_vs_threshold.html          # plot test DS TP-FN-FP vs threshold values
│       ├── val_metrics_vs_threshold.html           # plot metrics of validation DS (r, p, f1) vs threshold values
│       ├── val_predictions_at_0dot*_threshold.gpkg # prediction results for validation DS at a given score threshold * in geopackage
│       ├── val_TP-FN-FP_vs_threshold.html          # plot validation DS TP-FN-FP vs threshold values
│       └── validation_loss.svg                     # validation loss curve (downloaded from tensorboard)
├── scripts
│   ├── batch_process.sh                            # batch script automatising the prediction workflow (config/input-prd.template.yaml) 
│   ├── detection_monitoring.py                     # script tracking quarries in several years DS (config/input-dm.yaml) 
│   ├── plots.py                                    # script plotting figures (config/input-dm.yaml) 
│   ├── prediction_filter.py                        # script filtering predictions according to threshold values (config/input-prd.yaml) 
│   ├── prepare_data.py                             # script preparing files to run the object-detector scripts (config/input-tren.yaml and config/input-prd.yaml) 
│   └── README.md                                   # file explaining the role of each script 
├── .gitignore                                      # content added to this file is ignored by git 
├── LICENCE
├── README.md                                       # presentation of the project, requirements and execution of the project 
├── requirements.in                                 # python dependencies (modules and packages) required by the project
└── requirements.txt                                # compiled from requirements.in file. List of python dependencies for virtual environment creation
</pre>

 ## Workflow

<p align="center">
<img src="./images/dqry_workflow_graph.png?raw=true" width="100%">
<br />
<i>Workflow scheme.</i>
</p>


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
    $ python3 ../scripts/prediction_filter.py config-prd.yaml 

The workflow has been automatized and can be run for batch of years by running this command:

    $ ../scripts/batch_process.sh

**Object Monitoring**: copy the required input files (filtered prediction files (`oth_prediction_filter_year-{year}_[filters_list].geojson`)) to **input-dm** folder.

    $ python3 ../scripts/detection_monitoring.py config-dm.yaml
    $ python3 ../scripts/plots.py config-dm.yaml


## Disclaimer

The results provided by the `proj-dqry` framework are resulting from numerical implementation providing segmentation of **potential** quarry sites. False positive and false negative detection, inherent to deep learning automatic methods, are present in the final detection dataset. A **manual inspection** of the detection must be performed before data exploitation and interpretation.


## Copyright and License
 
**proj-dqry** - Nils Hamel, Adrian Meyer, Huriel Reichel, Clémence Herny, Shanci Li, Alessandro Cerioni, Roxane Pott <br >
Copyright (c) 2020-2022 Republic and Canton of Geneva

This program is licensed under the terms of the GNU GPLv3. Documentation and illustrations are licensed under the terms of the CC BY 4.0.