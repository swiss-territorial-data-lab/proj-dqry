# Automatic detection and monitoring of mineral extraction sites in Switzerland

The project aims to perform automatic detection of Mineral Extraction Sites (MES, also refered as quarry in this project) on georefrenced raster images of Switzerland over several years. A Deep Learning approach is used to train a model achiving a **f1 score of about 80%** (validation dataset), enabling accurate detection of MES. Detailed documentation of the project and results can be found on the [STDL technical website](https://github.com/swiss-territorial-data-lab/stdl-tech-website/tree/master/docs/PROJ-DQRY). <br>

**TOC**
- [Overview](#overview)
- [Requirements](#requirements)
    - [Hardware](#hardware)
    - [Software](#software)
    - [Installation](#installation)
- [Getting started](#getting-started)
    - [Files structure](#files-structure)
    - [Data](#data)
    - [Scripts](#scripts)
    - [Workflow instructions](#workflow-instructions)
- [Contributors](#contributors)
- [Disclaimer](#disclaimer)
- [Copyright and License](#copyright-and-license)


## Overview

The project `proj-dqry` provides preparation and post-processing scripts. Object detection is performed with the `object-detector` framework developed by the STDL, based on Deep Learning method. Documentation can be found [here](https://tech.stdl.ch/TASK-IDET/).

The procedure is defined in three distinct workflows:

1. **Training and Evaluation** enables the detection model to be trained and evaluated using a customised dataset reviewed by domain experts and constituting the ground truth. The detector is first trained on the [_SWISSIMAGE 10 cm_](https://www.swisstopo.admin.ch/fr/geodata/images/ortho/swissimage10.html) mosaic of 2020, using the [swissTLM3D](https://www.swisstopo.admin.ch/fr/geodata/landscape/tlm3d.html) data of manually vectorized MES.
2. **Detection** detects MES in a given set of images by inference ([_SWISSIMAGE Journey_](https://www.swisstopo.admin.ch/en/maps-data-online/maps-geodata-online/journey-through-time-images.html) release year) using the previously trained model.
3. **Detection monitoring** tracks MES evolution over the years.

<p align="center">
<img src="./images/dqry_workflow_graph.png?raw=true" width="100%">
<br />
<i>Workflow scheme.</i>
</p>

## Requirements

### Hardware

A CUDA-enabled GPU is required. <br>
The project has been run on a 32 GiB RAM machine with 16 GiB GPU (NVIDIA Tesla T4) compatible with [CUDA](https://detectron2.readthedocs.io/en/latest/tutorials/install.html) to use the library [detectron2](https://github.com/facebookresearch/detectron2), dedicated to object detection with Deep Learning algorithm. <br>
The main potential limitation is the number of tiles to proceed with and the amount of detection that might lead to RAM saturation. The provided requirements stand for a zoom level equal to or below 17 and an AoI corresponding to typical [SWISSIMAGE acquisition footprints](https://map.geo.admin.ch/?lang=fr&topic=ech&bgLayer=ch.swisstopo.pixelkarte-farbe&layers=ch.swisstopo.zeitreihen,ch.bfs.gebaeude_wohnungs_register,ch.bav.haltestellen-oev,ch.swisstopo.swisstlm3d-wanderwege,ch.astra.wanderland-sperrungen_umleitungen,ch.swisstopo.swissimage-product,ch.swisstopo.swissimage-product.metadata&layers_opacity=1,1,1,0.8,0.8,1,0.7&layers_visibility=false,false,false,false,false,true,true&layers_timestamp=18641231,,,,,2021,2021&time=2021) (about a third of Switzerland's surface at maximum). 

### Software

- OS: Ubuntu 20.04
- The scripts have been developed with Python 3.8 using PyTorch version 1.10 and CUDA version 11.3. 
- Compatible [`object-detector`](https://github.com/swiss-territorial-data-lab/object-detector) version [1.0.0](https://github.com/swiss-territorial-data-lab/object-detector/releases/tag/v1.0.0) 
- Python dependencies may be installed with either `pip` or `conda`, using the provided `requirements.txt` file. We advise using a [Python virtual environment](https://docs.python.org/3/library/venv.html).

### Installation

If not already done install GDAL:

```bash
sudo apt-get install -y python3-gdal gdal-bin libgdal-dev gcc g++ python3.8-dev
```

All the dependencies required for the project are listed in `requirements.txt` compiled from `requirements.in`. To install them:

- Create a Python virtual environment
```bash
$ python3 -m venv <dir_path>/[name of the virtual environment]
$ source <dir_path>/[name of the virtual environment]/bin/activate
```

- Install dependencies

```bash
$ pip install -r requirements.txt
```

- If needed (update dependencies or add a new Python library), _requirements.in_ can be compiled to generate a new _requirements.txt_. This operation might lead to libraries version changes:

```bash
$ pip-compile requirements.in
```

## Getting started

### Files structure

The general folders/files structure of the project `proj-dqry` is organized as follows. The path names can be customized by the end-user, and * indicates numbers that can vary:

<pre>.
├── config                                          # configurations files folder
│   ├── config_det.template.yaml                     # detection workflow for several years configuration file template
│   ├── config_dm.yaml                               # detection monitoring workflow configuration file
│   ├── config_det.yaml                              # detection workflow configuration file
│   ├── config_trne.yaml                             # training and evaluation workflow configuration file
│   ├── detectron2_config_dqry.yaml                  # detectron 2 configuration file 
│   └── logging.conf                                 # logging configuration
├── images
│   ├── dqry_workflow_graph.png
│   ├── detection_filter_after.png
│   ├── detection_filter_before.png
│   ├── quarries_area-year.png
│   ├── quarry_tracking_strategy.png
│   └── tiles_examples.png
├── input                                           # inputs folders. Have to be created by the end-user 
│   ├── input_dm                                    # detections monitoring input 
│   │   ├── oth_detections_at_0dot*_threshold_year-*_score-0dot*_area-*_elevation-*_distance-*.geojson # final filtered detections file for a given year. Copy output of `filter_detections.py`  
│   ├── input_det                                   # detection inputs
│   │   ├── logs                                    # folder containing trained model 
│   │   │   └── model_*.pth                         # selected model at iteration *
│   │   ├── AoI
│   │   │   ├── AoI_*.prj                           # AoI shapefile projection for a given year *
│   │   │   ├── AoI_*.shp                           # AoI shapefile for a given year *              
│   │   │   └── AoI_*.shx                           # AoI shapefile indexes for a given year *
│   └── input_trne                                  # training and evaluation inputs
│       ├── tlm-hr-trn-topo.prj                     # shapefile projection of the labels
│       ├── tlm-hr-trn-topo.shp                     # shapefile of the labels 
│       └── tlm-hr-trn-topo.shx                     # shapefile indexes of the labels
├── output                                          # outputs folders. Created automatically by running scripts
│   ├── output_dm                                   # detection monitoring outputs 
│   │   └── oth_detections_at_0dot*_threshold_year-*_score-0dot*_area-*_elevation-*_distance-*   # final filtered detections file for a given year
│   │       ├── plots                               # plots storage 
│   │       │   └── quarry_area.png                 # quarry area vs year plot  
│   │       ├── quarry_tiles.csv                    # table containing detections (id, geometry, area, year...) for a list of given Year. Overlapping detections between years display the same unique ID 
│   │       └── quarry_times.geojson                # geometry file containing detections (id, geometry, area, year...) for a list of given Year. Overlapping detections between years display the same unique ID 
│   ├── output_det                                  # detection outputs 
│   │   ├── all-images                              # images downloaded from wmts server (XYZ values)
│   │   │   ├── z_y_x.json
│   │   │   └── z_y_x.tif
│   │   ├── oth-images                              # tagged images other DataSet
│   │   │   └── z_y_x.tif
│   │   ├── sample_tagged_images                    # examples of annoted detection on images (XYZ values)
│   │   │   └── oth_pred_z_y_x.png
│   │   ├── COCO_oth.json                           # COCO annotations on other DS  
│   │   ├── img_metadata.json                       # images info
│   │   ├── labels.json                             # AoI contour 
│   │   ├── oth_detections_at_0dot*_threshold_year-*_score-0dot*_area-*_elevation-*_distance-*.geojson
│   │   ├── oth_detections_at_0dot*_threshold.gpkg  # detection results at a given score threshold * in geopackage format
│   │   ├── split_AoI_tiles.geojson                 # labels shape clipped to tiles shape 
│   │   └── tiles.geojson                           # tiles geometries 
│   └── output_trne                                 # training and evaluation outputs  
│       ├── all-images                              # images downloaded from wmts server (XYZ values)
│       │   ├── z_y_x.json
│       │   └── z_y_x.tif
│       ├── logs                                    # folder containing trained model 
│       │   ├── inference
│       │   │   ├── coco_instances_results.json
│       │   │   └── instances_detections.pth
│       │   ├── events.out.tfevents.*.vm-gpu-02.*.0
│       │   ├── last_checkpoint
│       │   ├── metrics.json                        # computed metrics for the given interval and bin size
│       │   ├── model_*.pth                         # saved trained model at a given iteration *
│       │   └── model_final.pth                     # last iteration saved model
│       ├── sample_tagged_images                    # examples of annoted detection on images (XYZ values)
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
│       ├── precision_vs_recall.html                # plot precision vs recall
│       ├── split_AoI_tiles.geojson                 # tagged DS tiles 
│       ├── tagged_detections.gpkg                  # tagged detections (TP, FP, FN) 
│       ├── tiles.json                              # tiles geometries
│       ├── trn_metrics_vs_threshold.html           # plot metrics of train DS (r, p, f1) vs threshold values
│       ├── trn_detections_at_0dot*_threshold.gpkg  # detection results for train DS at a given score threshold * in geopackage
│       ├── trn_TP-FN-FP_vs_threshold.html          # plot train DS TP-FN-FP vs threshold values
│       ├── tst_metrics_vs_threshold.html           # plot metrics of test DS (r, p, f1) vs threshold values
│       ├── tst_detections_at_0dot*_threshold.gpkg  # detection results for test DS at a given score threshold * in geopackage
│       ├── tst_TP-FN-FP_vs_threshold.html          # plot test DS TP-FN-FP vs threshold values
│       ├── val_metrics_vs_threshold.html           # plot metrics of validation DS (r, p, f1) vs threshold values
│       ├── val_detections_at_0dot*_threshold.gpkg # detection results for validation DS at a given score threshold * in geopackage
│       └── val_TP-FN-FP_vs_threshold.html          # plot validation DS TP-FN-FP vs threshold values
├── scripts
│   ├── batch_process.sh                            # batch script automatising the detection workflow
│   ├── detection_monitoring.py                     # script tracking detections in several years DS 
│   ├── filter_detection.py                         # script filtering detections according to threshold values
│   ├── get_dem.sh                                  # batch script downloading DEM of Switzerland
│   ├── plots.py                                    # script plotting figures
│   ├── prepare_data.py                             # script preparing files to run the object-detector scripts
│   └── README.md                                   # detail description of each script 
├── .gitignore                                      # content added to this file is ignored by git 
├── LICENCE
├── README.md                                       # presentation of the project, requirements and execution of the project 
├── requirements.in                                 # python dependencies (modules and packages) required by the project
└── requirements.txt                                # compiled from requirements.in file. List of python dependencies for virtual environment creation
</pre>

## Data

Below the source of input data used for this project. The input data can be adapted as required.

- images: annual dataset of aerial images of Switzerland from ([_SWISSIMAGE Journey_](https://www.swisstopo.admin.ch/en/maps-data-online/maps-geodata-online/journey-through-time-images.html) release year). Only RGB images are used, from 1999 to current. It includes [_SWISSIMAGE 10 cm_](https://www.swisstopo.admin.ch/fr/geodata/images/ortho/swissimage10.html), _SWISSIMAGE 25 cm_ and _SWISSIMAGE 50 cm_. The images are downloaded from [geo.admin.ch](https://www.geo.admin.ch/fr) servor using XYZ connector with this url format: https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.swissimage-product/default/[YEAR]/3857/{z}/{x}/{y}.jpeg
- labels: MES labels come from [swissTLM3D](https://www.swisstopo.admin.ch/fr/geodata/landscape/tlm3d.html) product. The file _tlm-hr-trn-topo.shp_, used for training, has been reviewed and synchronised with the 2020 _SWISSIMAGE 10 cm_ mosaic.
- AoI: image acquisition footprint by year (AoI_[YEAR].shp) are visible [here](https://map.geo.admin.ch/?lang=fr&topic=ech&bgLayer=ch.swisstopo.pixelkarte-farbe&layers=ch.swisstopo.zeitreihen,ch.bfs.gebaeude_wohnungs_register,ch.bav.haltestellen-oev,ch.swisstopo.swisstlm3d-wanderwege,ch.astra.wanderland-sperrungen_umleitungen,ch.swisstopo.swissimage-product,ch.swisstopo.swissimage-product.metadata&layers_opacity=1,1,1,0.8,0.8,1,0.7&layers_visibility=false,false,false,false,false,true,true&layers_timestamp=18641231,,,,,2021,2021&time=2021).
- Switzerland DEM: the DEM model of Switzerland has been processed by Lukas Martinelli and can be downloaded [here](https://github.com/lukasmartinelli/swissdem).
- trained model: the trained model used to produce the results presented in the [documentation](https://github.com/swiss-territorial-data-lab/stdl-tech-website/tree/master/docs/PROJ-DQRY) and achieving a f1 score of 82% is available on request.


## Scripts

The `proj-dqry` repository contains scripts to prepare and post-process the datasets:

1. `prepare_data.py` 
2. `filter_detection.py` 
3. `detection_monitoring.py` 
4. `plots.py` 
5. `get_DEM.sh` 
6. `batch_process.sh` 

The description of each script can be found [here](/scripts/README.md). 

In addition, object detection is performed by tools developed in the `object-detector` git repository. A description of the scripts used is presented [here](https://github.com/swiss-territorial-data-lab/object-detector).


 ## Workflow instructions

The workflow can be executed by running the following list of actions and commands. Adjust the paths and input values of the configuration files accordingly. Content of config files in [] must be assigned.  

**Training and evaluation**: 

```bash
$ python3 scripts/prepare_data.py config/config_trne.yaml
$ stdl-objdet generate_tilesets config/config_trne.yaml
$ stdl-objdet train_model config/config_trne.yaml
$ tensorboard --logdir output/output_trne/logs
```

Open the following link with a web browser: `http://localhost:6006` and identify the iteration minimizing the validation loss curve and select the model accordingly (**pth_file**) in `config_trne`. 

```bash
$ stdl-objdet make_detections config/config_trne.yaml
$ stdl-objdet assess_detections config/config_trne.yaml
```

**Detection**: copy the selected trained model to `input/input_det/logs` folder (create it if it does not exist).

```bash
$ python3 scripts/prepare_data.py config/config_det.yaml
$ stdl-objdet generate_tilesets config/config_det.yaml
$ stdl-objdet make_detections config/config_det.yaml
$ scripts/get_dem.sh
$ python3 scripts/filter_detections.py config/config_det.yaml
```

The **Detection** workflow has been automated and can be run for a batch of years by executing this command:

```bash
$ scripts/get_dem.sh
$ scripts/batch_process.sh
```

**Object Monitoring**: copy the required input files (filtered detection files (`oth_detections_filter_year-{year}_[filters_list].geojson`)) to **input_dm** folder.

```bash
$ mkdir input_dm
$ python3 scripts/detections_monitoring.py config/config_dm.yaml
$ python3 scripts/plots.py config/config_dm.yaml
```

## Contributors

`proj-dqry` was made possible with the help of several contributors (alphabetical):

Alessandro Cerioni, Nils Hamel, Clémence Herny, Shanci Li, Adrian Meyer, Huriel Reichel

## Disclaimer

Depending on the end purpose, we strongly recommend users not take for granted the detection obtained through this code. Indeed, results can exhibit false positives and false negatives, as is the case in all Machine Learning-based approaches.

## Copyright and license

This project is licensed under the terms of the GNU GPLv3. Documentation and illustrations are licensed under the terms of the CC BY 4.0.

Copyright (c) 2020-2022 Republic and Canton of Geneva