# Automatic detection and observation of mineral extraction sites in Switzerland

The project aims to perform automatic detection of mineral extraction sites (MES, also referred as quarry in this project) on georeferenced raster images of Switzerland over several years. A deep learning approach is used to train a model achieving a **f1 score of about 80%** (validation dataset), enabling accurate detection of MES over time. Detailed documentation of the project and results can be found on the [STDL technical website](https://tech.stdl.ch/PROJ-DQRY-TM/). <br>

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

The project `proj-dqry` provides scripts to prepare and post-process data and results dedicated to MES automatic detection. Object detection is performed with the `object-detector` framework developed by the STDL, based on deep learning method. Documentation of this project can be found [here](https://tech.stdl.ch/TASK-IDET/).

The procedure is defined in three distinct workflows:

1. **Training and evaluation**: enables the detection model to be trained and evaluated using a customised dataset reviewed by domain experts and constituting the ground truth. The detector is first trained on the [_SWISSIMAGE 10 cm_](https://www.swisstopo.admin.ch/fr/geodata/images/ortho/swissimage10.html) mosaic of 2020, using manually vectorised MES of the [swissTLM3D](https://www.swisstopo.admin.ch/fr/geodata/landscape/tlm3d.html) product.
2. **Detection**: enables detection by inference of MES in a given set of images ([_SWISSIMAGE Journey_](https://www.swisstopo.admin.ch/en/maps-data-online/maps-geodata-online/journey-through-time-images.html)) using the previously trained model.
3. **Detection tracking**: identifies and tracks MES evolution over time.

<p align="center">
<img src="./images/dqry_workflow_graph.png?raw=true" width="100%">
<br />
<i>Workflow scheme.</i>
</p>

## Requirements

### Hardware

The project has been run on a 32 GiB RAM machine with a 16 GiB GPU (NVIDIA Tesla T4) compatible with [CUDA](https://detectron2.readthedocs.io/en/latest/tutorials/install.html). The library [detectron2](https://github.com/facebookresearch/detectron2), dedicated to object detection with deep learning algorithm, was used. <br>
The main limitation is the number of tiles to be processed and the amount of detections, which can lead to RAM saturation. The provided requirements stand for a zoom level equal to or below 17 and an area of interest (AoI) corresponding to typical [SWISSIMAGE acquisition footprints](https://map.geo.admin.ch/?lang=fr&topic=ech&bgLayer=ch.swisstopo.pixelkarte-farbe&layers=ch.swisstopo.zeitreihen,ch.bfs.gebaeude_wohnungs_register,ch.bav.haltestellen-oev,ch.swisstopo.swisstlm3d-wanderwege,ch.astra.wanderland-sperrungen_umleitungen,ch.swisstopo.swissimage-product,ch.swisstopo.swissimage-product.metadata&layers_opacity=1,1,1,0.8,0.8,1,0.7&layers_visibility=false,false,false,false,false,true,true&layers_timestamp=18641231,,,,,2021,2021&time=2021) (no more than a third of Switzerland's surface area). 

### Software

- Ubuntu 20.04
- Python version 3.8 
- PyTorch version 1.10
- CUDA version 11.3
- `object-detector` version [1.0.0](https://github.com/swiss-territorial-data-lab/object-detector/releases/tag/v1.0.0) 

### Installation

Install GDAL:

```bash
sudo apt-get install -y python3-gdal gdal-bin libgdal-dev gcc g++ python3.8-dev
```

Python dependencies can be installed with `pip` or `conda` using the `requirements.txt` file (compiled from `requirements.in`) provided. We advise using a [Python virtual environment](https://docs.python.org/3/library/venv.html).

- Create a Python virtual environment
```bash
$ python3 -m venv <dir_path>/<name of the virtual environment>
$ source <dir_path>/<name of the virtual environment>/bin/activate
```

- Install dependencies

```bash
$ pip install -r requirements.txt
```

- If needed (update dependencies or addition a new Python library), _requirements.in_ can be compiled to generate a new _requirements.txt_:

```bash
$ pip-compile requirements.in
```

## Getting started

### Files structure

The folders/files of the project `proj-dqry` (in combination with `object-detector`) is organised as follows. Path names can be customised by the user, and * indicates numbers which may vary:

<pre>.
├── config                                          # configurations files folder
│   ├── config_det.template.yaml                    # template file for detection workflow over several years
│   ├── config_track.yaml                           # detection tracking workflow
│   ├── config_det.yaml                             # detection workflow
│   ├── config_trne.yaml                            # training and evaluation workflow
│   ├── detectron2_config_dqry.yaml                 # detectron 2
│   └── logging.conf                                # logging configuration
├── images                                          # folder containing the images displayed in the README 
├── input                                           # inputs folders
│   ├── input_track                                 # detection tracking input 
│   │   ├── oth_detections_at_0dot*_threshold_year-*_score-0dot*_area-*_elevation-*_distance-*.geojson # final filtered detections file for a given year
│   ├── input_det                                   # detection inputs
│   │   ├── logs                                    # folder containing trained model 
│   │   │   └── model_*.pth                         # selected model at iteration
│   │   ├── AoI
│   │   │   ├── swissimage_footprint_*.prj          # AoI shapefile projection for a given year
│   │   │   ├── swissimage_footprint_*.shp          # AoI shapefile for a given year          
│   │   │   └── swissimage_footprint_*.shx          # AoI shapefile indexes for a given year
│   └── input_trne                                  # training and evaluation inputs
│       ├── tlm-hr-trn-topo.prj                     # shapefile projection of the labels
│       ├── tlm-hr-trn-topo.shp                     # shapefile of the labels 
│       └── tlm-hr-trn-topo.shx                     # shapefile indexes of the labels
├── output                                          # outputs folders
│   ├── output_track                                # detection tracking outputs 
│   │   └── oth_detections_at_0dot*_threshold_year-*_score-0dot*_area-*_elevation-*_distance-*   # final filtered detections file for a given year
│   │       ├── plots                               # plot saving folder
│   │       ├── detections_years.csv                # table containing detections (id, geometry, area, year...) for a list of given year
│   │       └── detections_years.geojson            # geometry file containing detections (id, geometry, area, year...) for a list of given year
│   ├── output_det                                  # detection outputs 
│   │   ├── all-images                              # images downloaded from wmts server (XYZ values)
│   │   │   ├── z_y_x.json
│   │   │   └── z_y_x.tif
│   │   ├── oth-images                              # tagged images other dataset
│   │   │   └── z_y_x.tif
│   │   ├── sample_tagged_images                    # examples of annotated detections on images (XYZ values)
│   │   │   └── oth_pred_z_y_x.png
│   │   ├── COCO_oth.json                           # COCO annotations on other dataset  
│   │   ├── img_metadata.json                       # images info
│   │   ├── labels.json                             # AoI contour 
│   │   ├── oth_detections_at_0dot*_threshold_year-*_score-0dot*_area-*_elevation-*_distance-*.geojson
│   │   ├── oth_detections_at_0dot*_threshold.gpkg  # detections obtained with a given score threshold
│   │   ├── split_AoI_tiles.geojson                 # labels' shapes clipped to tiles' shapes 
│   │   └── tiles.geojson                           # tiles geometries 
│   └── output_trne                                 # training and evaluation outputs  
│       ├── all-images                              # images downloaded from WMTS server (XYZ values)
│       │   ├── z_y_x.json
│       │   └── z_y_x.tif
│       ├── logs                                    # folder containing trained model 
│       │   ├── inference
│       │   │   ├── coco_instances_results.json
│       │   │   └── instances_detections.pth
│       │   ├── metrics.json                        # computed metrics for the given interval and bin size
│       │   ├── model_*.pth                         # saved trained model at a given iteration
│       │   └── model_final.pth                     # last iteration saved model
│       ├── sample_tagged_images                    # examples of annotated detections on images (XYZ values)
│       │   └── pred_z_y_x.png
│       │   └── tagged_z_y_x.png
│       │   └── trn_pred_z_y_x.png
│       │   └── tst_pred_z_y_x.png
│       │   └── val_pred_z_y_x.png
│       ├── trn-images                              # tagged images train dataset  
│       │   └── z_y_x.tif
│       ├── tst-images                              # tagged images test dataset
│       │   └── z_y_x.tif
│       ├── val-images                              # tagged images validation dataset
│       │   └── z_y_x.tif
│       ├── clipped_labels.geojson                  # labels shape clipped to tiles shape 
│       ├── COCO_trn.json                           # COCO annotations on train dataset
│       ├── COCO_tst.json                           # COCO annotations on test dataset
│       ├── COCO_val.json                           # COCO annotations on validation dataset
│       ├── img_metadata.json                       # images info
│       ├── labels.json                             # labels geometries
│       ├── precision_vs_recall.html                # plot precision vs recall
│       ├── split_AoI_tiles.geojson                 # tagged dataset tiles 
│       ├── tagged_detections.gpkg                  # tagged detections (TP, FP, FN) 
│       ├── tiles.json                              # tiles geometries
│       ├── trn_metrics_vs_threshold.html           # plot metrics of train dataset vs threshold values
│       ├── trn_detections_at_0dot*_threshold.gpkg  # detections obtained for the train dataset with a given score threshold 
│       ├── trn_TP-FN-FP_vs_threshold.html          # plot train DS TP-FN-FP vs threshold values
│       ├── tst_metrics_vs_threshold.html           # plot metrics of test dataset vs threshold values
│       ├── tst_detections_at_0dot*_threshold.gpkg  # detections obtained for the test dataset with a given score threshold
│       ├── tst_TP-FN-FP_vs_threshold.html          # plot test dataset TP-FN-FP vs threshold values
│       ├── val_metrics_vs_threshold.html           # plot metrics of validation dataset vs threshold values
│       ├── val_detections_at_0dot*_threshold.gpkg  # detections obtained for the validation dataset with a given score threshold
│       └── val_TP-FN-FP_vs_threshold.html          # plot validation dataset TP-FN-FP vs threshold values
├── scripts
│   ├── batch_process.sh                            # batch script automatising the detection workflow
│   ├── track_detections.py                         # script tracking the detections in multiple years dataset 
│   ├── filter_detections.py                        # script filtering the detections according to threshold values
│   ├── get_dem.sh                                  # batch script downloading the DEM of Switzerland
│   ├── plots.py                                    # script plotting figures
│   ├── prepare_data.py                             # script preparing data to be processed by the object-detector scripts
│   └── README.md                                   # detail description of each script 
├── .gitignore                                      
├── LICENSE
├── README.md                                      
├── requirements.in                                 # list of python libraries required for the project
└── requirements.txt                                # python dependencies compiled from requirements.in file
</pre>


## Data

Below, the description of input data used for this project. 

- images: [_SWISSIMAGE Journey_](https://www.swisstopo.admin.ch/en/maps-data-online/maps-geodata-online/journey-through-time-images.html) is an annual dataset of aerial images of Switzerland. Only RGB images are used, from 1999 to current. It includes [_SWISSIMAGE 10 cm_](https://www.swisstopo.admin.ch/fr/geodata/images/ortho/swissimage10.html), _SWISSIMAGE 25 cm_ and _SWISSIMAGE 50 cm_. The images are downloaded from the [geo.admin.ch](https://www.geo.admin.ch/fr) server using [XYZ](https://developers.planet.com/docs/planetschool/xyz-tiles-and-slippy-maps/) connector. 
- ground truth: MES labels come from the [swissTLM3D](https://www.swisstopo.admin.ch/fr/geodata/landscape/tlm3d.html) product. The file _tlm-hr-trn-topo.shp_, used for training, has been reviewed and synchronised with the 2020 _SWISSIMAGE 10 cm_ mosaic.
- AoI: image acquisition footprints by year (swissimage_footprint_<YEAR>.shp) can be found [here](https://map.geo.admin.ch/?lang=fr&topic=ech&bgLayer=ch.swisstopo.pixelkarte-farbe&layers=ch.swisstopo.zeitreihen,ch.bfs.gebaeude_wohnungs_register,ch.bav.haltestellen-oev,ch.swisstopo.swisstlm3d-wanderwege,ch.astra.wanderland-sperrungen_umleitungen,ch.swisstopo.swissimage-product,ch.swisstopo.swissimage-product.metadata&layers_opacity=1,1,1,0.8,0.8,1,0.7&layers_visibility=false,false,false,false,false,true,true&layers_timestamp=18641231,,,,,2021,2021&time=2021). The shapefiles of _SWISSIMAGE_ acquisition footprint from 2015 to 2020 are provided in this repository.
- DEM: the DEM of Switzerland has been processed by Lukas Martinelli and can be downloaded [here](https://github.com/lukasmartinelli/swissdem).
- trained model: the trained model used to produce the results presented in the [documentation](https://github.com/swiss-territorial-data-lab/stdl-tech-website/tree/master/docs/PROJ-DQRY) and achieving a f1 score of 82% is available on request.


## Scripts

The `proj-dqry` repository contains scripts to prepare and post-process the data and results:

1. `prepare_data.py` 
2. `filter_detections.py` 
3. `track_detections.py` 
4. `plots.py` 
5. `get_DEM.sh` 
6. `batch_process.sh` 

The description of each script can be found [here](./scripts/README.md). 

Object detection is performed with tools present in the [`object-detector`](https://github.com/swiss-territorial-data-lab/object-detector) git repository. 


 ## Workflow instructions

The workflow can be executed by running the following list of actions and commands. Adjust the paths and input values of the configuration files accordingly. The contents of the configuration files in angle brackets must be assigned. 

**Training and evaluation**: 

```bash
$ python scripts/prepare_data.py config/config_trne.yaml
$ stdl-objdet generate_tilesets config/config_trne.yaml
$ stdl-objdet train_model config/config_trne.yaml
$ tensorboard --logdir output/output_trne/logs
```

Open the following link with a web browser: `http://localhost:6006` and identify the iteration minimising the validation loss and select the model accordingly (`model_*.pth`) in `config_trne`. For the provided parameters, `model_0002999.pth` is the default one.

```bash
$ stdl-objdet make_detections config/config_trne.yaml
$ stdl-objdet assess_detections config/config_trne.yaml
```

**Detection**: 

```bash
$ mkdir -p input/input_det/logs
$ cp output/output_trne/logs/<selected_model_pth> input/input_det/logs
$ python scripts/prepare_data.py config/config_det.yaml
```

Don't forget to assign the desired year to the url in `config_det.yaml` when you download tiles from the server with `generate_tilesets.py`.

url: https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.swissimage-product/default/[YEAR]/3857/{z}/{x}/{y}.jpeg


```bash
$ stdl-objdet generate_tilesets config/config_det.yaml
$ stdl-objdet make_detections config/config_det.yaml
$ scripts/get_dem.sh
$ python scripts/filter_detections.py config/config_det.yaml
```

The **Detection** workflow has been automated and can be run for a batch of years by executing these commands:

```bash
$ scripts/get_dem.sh
$ scripts/batch_process.sh
```

**Detection tracking**: 

Copy the detections files `oth_detections_at_0dot3_threshold_year-{year}_{filters_list}.geojson` produced for different years with the **Detection** workflow to the **input_track** folder.


```bash
$ mkdir input/input_track
$ cp output/output_det/<oth_filtered_detections_path> input/input_track
$ python scripts/track_detections.py config/config_track.yaml
$ python scripts/plots.py config/config_track.yaml
```

## Contributors

`proj-dqry` was made possible with the help of several contributors (alphabetical):

Alessandro Cerioni, Nils Hamel, Clémence Herny, Shanci Li, Adrian Meyer, Huriel Reichel

## Disclaimer

Depending on the end purpose, we strongly recommend users not take for granted the detections obtained through this code. Indeed, results can exhibit false positives and false negatives, as is the case in all approaches based on machine learning.

## License

This project is licensed under the terms of the GNU GPLv3. Documentation and illustrations are licensed under the terms of the CC BY 4.0.