## Overview

The project `proj-dqry` provides the procedure to perform automatic detection of Quarries and Mineral Extraction Sites (MES) on georefrenced raster image in Switzerland over several years. The project `proj-dqry` provides the preparation and post-processing scripts. Object detection is performed with the `object-detector` framework developed by the STDL, based on Deep Learning method. Documentation and scripts can be found here: https://github.com/swiss-territorial-data-lab/object-detector

The procedure is defined in three distinct workflows:

1. **Training and Evaluation** enables the detection model to be trained and evaluated using a customised dataset reviewed by domain experts and constituting the ground truth. The detector is first trained on the [_SWISSIMAGE 10 cm_](https://www.swisstopo.admin.ch/fr/geodata/images/ortho/swissimage10.html) mosaic of 2020, using the [swissTLM3D](https://www.swisstopo.admin.ch/fr/geodata/landscape/tlm3d.html) data of manually vectorized quarries as ground truth.
2. **Detection** detects careers in a given set of images by inference ([_SWISSIMAGE Journey_](https://www.swisstopo.admin.ch/en/maps-data-online/maps-geodata-online/journey-through-time-images.html) release year) using the previously trained model.
3. **Detection monitoring** tracks quarry evolution over the years.

<p align="center">
<img src="./images/dqry_workflow_graph.png?raw=true" width="100%">
<br />
<i>Workflow scheme.</i>
</p>

**TOC**
- [Requirements](#requirements)
    - [Hardware](#hardware)
    - [Installation](#installation)
- [Python libraries](#python-libraries)
- [Files structure](#files-structure)
- [Workflow instructions](#workflow-instructions)
- [Copyright and License](#copyright-and-license)

## Requirements

### Hardware

The scripts have been run with Ubuntu 20.04 OS on a 32 GiB RAM machine with 16 GiB GPU (NVIDIA Tesla T4) compatible with [CUDA](https://detectron2.readthedocs.io/en/latest/tutorials/install.html) to use the library [detectron2](https://github.com/facebookresearch/detectron2), dedicated to object detection with Deep Learning algorithms. <br>
The main limitation of this project is the number of tiles to proceed with and the amount of detection. The provided requirements stand for a zoom level equal to or below 17 and an AOI corresponding to SWISSIMAGE acquisition footprints (about a third of Switzerland's surface at maximum). For a higher zoom level and/or a larger AOI, the number of data to process might lead to RAM saturation. In this case, either a machine with larger RAM is required, or the AOI needs to be subdivided into a smaller area.

### Installation

The scripts have been developed with Python 3.8 using PyTorch version 1.10 and CUDA version 11.3. 
If not already done install GDAL:

    sudo apt-get install -y python3-gdal gdal-bin libgdal-dev gcc g++ python3.8-dev

All the dependencies required for the project are listed in `requirements.in` and `requirements.txt`. To install them:

- Create a Python virtual environment

        $ python3 -m venv <dir_path>/[name of the virtual environment]
        $ source <dir_path>/[name of the virtual environment]/bin/activate

- Install dependencies

        $ pip install -r requirements.txt

-_requirements.txt_ has been obtained by compiling _requirements.in_. Recompiling the file might lead to libraries version changes:

        $ pip-compile requirements.in

Pandas 1.5.3 is recommended to avoid dependencies depreciation.

## Files structure

The `proj-dqry` repository (https://github.com/swiss-territorial-data-lab/proj-dqry) contains scripts to prepare and post-process the datasets:

1. `prepare_data.py` 
2. `filter_detection.py` 
3. `detection_monitoring.py` 
4. `plots.py` 
5. `batch_process.sh` 

The description of each script can be found [here](/scripts/README.md).  

In addition, object detection is performed by tools developed in `object-detector` git repository. A description of the scripts used is presented [here](https://github.com/swiss-territorial-data-lab/object-detector)

The general folders/files structure of the project `proj-dqry` is organized as follows. The path names can be customized by the end-user, and * indicates numbers that can vary:

<pre>.
├── config                                          # configurations files folder
│   ├── input_dm.yaml                               # detection monitoring workflow configuration file
│   ├── input_det.template.yaml                     # prediction workflow for several years configuration file template
│   ├── input_det_.yaml                              # prediction workflow configuration file
│   ├── input_trne.yaml                             # training and evaluation workflow configuration file
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
│   │   ├── oth_prediction_at_0dot*_threshold_year-*_score-0dot*_area-*_elevation-*_distance-*.geojson # final filtered detections file for a given year. Copy output of `prediction_filter.py`  
│   ├── input-prd                                   # prediction inputs
│   |   ├── z*                                      # trained model for a given zoom level z, _i.e._ z16 
│   │   │   ├── logs                                # folder containing trained model 
│   │   │   │   ├── inference
│   │   │   │   │   ├── coco_instances_results.json
│   │   │   │   │   └── instances_detections.pth
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
│   │   └── oth_prediction_at_0dot*_threshold_year-*_score-0dot*_area-*_elevation-*_distance-*   # final filtered detections file for a given year
│   │       ├── plots                               # plots storage 
│   │       │   └── quarry_area.png                 # quarry area vs year plot  
│   │       ├── quarry_tiles.csv                    # table containing prediction (id, geometry, area, year...) for a list of given Year. Overlapping detections between years display the same unique ID 
│   │       └── quarry_times.geojson                # geometry file containing prediction (id, geometry, area, year...) for a list of given Year. Overlapping detections between years display the same unique ID 
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
│   │   ├── oth_detections_at_0dot*_threshold.gpkg # prediction results at a given score threshold * in geopackage format
│   │   ├── split_aoi_tiles.geojson                 # labels shape clipped to tiles shape 
│   │   └── tiles.geojson                           # tiles geometries 
│   └── output-trne                                 # training and evaluation outputs  
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
│       ├── tagged_detections.gpkg                 # tagged detections (TP, FP, FN) 
│       ├── tiles.json                              # tiles geometries
│       ├── total_loss.svg                          # total loss plot (downloaded from tensorboard)
│       ├── trn_metrics_vs_threshold.html           # plot metrics of train DS (r, p, f1) vs threshold values
│       ├── trn_detections_at_0dot*_threshold.gpkg # prediction results for train DS at a given score threshold * in geopackage
│       ├── trn_TP-FN-FP_vs_threshold.html          # plot train DS TP-FN-FP vs threshold values
│       ├── tst_metrics_vs_threshold.html           # plot metrics of test DS (r, p, f1) vs threshold values
│       ├── tst_detections_at_0dot*_threshold.gpkg # prediction results for test DS at a given score threshold * in geopackage
│       ├── tst_TP-FN-FP_vs_threshold.html          # plot test DS TP-FN-FP vs threshold values
│       ├── val_metrics_vs_threshold.html           # plot metrics of validation DS (r, p, f1) vs threshold values
│       ├── val_detections_at_0dot*_threshold.gpkg # prediction results for validation DS at a given score threshold * in geopackage
│       ├── val_TP-FN-FP_vs_threshold.html          # plot validation DS TP-FN-FP vs threshold values
│       └── validation_loss.svg                     # validation loss curve (downloaded from tensorboard)
├── scripts
│   ├── batch_process.sh                            # batch script automatising the prediction workflow (config/input-prd.template.yaml) 
│   ├── detection_monitoring.py                     # script tracking quarries in several years DS (config/input-dm.yaml) 
│   ├── plots.py                                    # script plotting figures (config/input-dm.yaml) 
│   ├── prediction_filter.py                        # script filtering detections according to threshold values (config/input-prd.yaml) 
│   ├── prepare_data.py                             # script preparing files to run the object-detector scripts (config/input-tren.yaml and config/input-prd.yaml) 
│   └── README.md                                   # file explaining the role of each script 
├── .gitignore                                      # content added to this file is ignored by git 
├── LICENCE
├── README.md                                       # presentation of the project, requirements and execution of the project 
├── requirements.in                                 # python dependencies (modules and packages) required by the project
└── requirements.txt                                # compiled from requirements.in file. List of python dependencies for virtual environment creation
</pre>


 ## Workflow instructions

The workflow can be run by issuing the following list of actions and commands:

    $ cd proj-dqry/
    $ python3 -m venv <dir_path>/[name of the virtual environment]
    $ source <dir_path>/[name of the virtual environment]/bin/activate
    $ pip install -r requirements.txt

    $ mkdir input
    $ mkdir input_trne
    $ mkdir input_det
    $ mkdir input_dm

Adapt the paths and input values of the configuration files accordingly.

**Training and evaluation**: copy the required input files (labels shapefile (_tlm-hr-trn-topo.shp_) and trained model is necessary (`z*/logs`)) to **input-trne** folder.

    $ python3 scripts/prepare_data.py config/config_trne.yaml
    $ stdl-objdet generate_tilesets config_trne.yaml config/config_trne.yaml
    $ python3 stdl-objdet train_model config_trne.yaml config/config_trne.yaml
    $ tensorboard --logdir output/output_trne/logs

Open the following link with a web browser: `http://localhost:6006` and identified the iteration minimizing the validation loss curve and the selected model name (**pth_file**) in `config_trne` to run `make_detections.py`. 

    $ stdl-objdet make_detections config_trne.yaml config/config_trne.yaml
    $ stdl-objdet assess_detections config/config_trne.yaml

**Detection**: copy the required input files (AOI shapefile (`swissimage_footprint_[YEAR].shp`) and trained model (`/z*/logs`)) to **input-prd** folder.

    $ python3 scripts/prepare_data.py config/config_det.yaml
    $ python3 stdl-objdet generate_tilesets config/config_det.yaml
    $ python3 stdl-objdet make_detections config/config_det.yaml
    $ script/get_dem.sh
    $ python3 scripts/filter_detections.py config/config_det.yaml

The **Detection** workflow has been automated and can be run for a batch of years by executing this command:

    $ scripts/batch_process.sh

**Object Monitoring**: copy the required input files (filtered detection files (`oth_detections_filter_year-{year}_[filters_list].geojson`)) to **input_dm** folder.

    $ python3 scripts/detection_monitoring.py config/config_dm.yaml
    $ python3 scripts/plots.py config/config_dm.yaml


## Disclaimer

Depending on the end purpose, we strongly recommend users not take for granted the detection obtained through this code. Indeed, results can exhibit false positives and false negatives, as is the case in all Machine Learning-based approaches.