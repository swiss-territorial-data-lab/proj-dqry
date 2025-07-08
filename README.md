# Automatic detection and observation of mineral extraction sites

The aim of the project is to automatically detect mineral extraction sites (MES, also referred as quarry in this project) on georeferenced raster images over several years using a deep learning approach. The workflow was initially developed to detect MES in airborne images from [swisstopo](https://www.swisstopo.admin.ch/en) over Switzerland. The trained model, achieves a **f1 score of about 80%**, enabling accurate detection of MES over time. A detailed documentation of the project and results can be found [here](https://tech.stdl.ch/PROJ-DQRY-TM/) on the STDL tech website. The latest developments allow users to use the framework with satellite images via [Open Data Cubes](https://www.opendatacube.org/) (ODC). Two have been tested: the [SwissDataCube](https://www.swissdatacube.org/) (SDC) and the [BrazilDataCube](https://data.inpe.br/bdc/web/en/home-page-2/) (BDC). The detailed documentation can be found [here](https://tech.stdl.ch/PROJ-DQRY-TM/) on the STDL tech website. Examples are provided for all use cases. <br>

**Table of content**

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
</p>

## Requirements

### Hardware

The project has been run on a 32 GiB RAM machine with a 16 GiB GPU (NVIDIA Tesla T4) compatible with [CUDA](https://detectron2.readthedocs.io/en/latest/tutorials/install.html). <br>
The main limitation is the number of tiles to be processed and the amount of detections, which can lead to RAM saturation. The provided requirements stand for a zoom level equal to or below 17 and an area of interest (AoI) corresponding to typical [SWISSIMAGE acquisition footprints](https://map.geo.admin.ch/?lang=fr&topic=ech&bgLayer=ch.swisstopo.pixelkarte-farbe&layers=ch.swisstopo.zeitreihen,ch.bfs.gebaeude_wohnungs_register,ch.bav.haltestellen-oev,ch.swisstopo.swisstlm3d-wanderwege,ch.astra.wanderland-sperrungen_umleitungen,ch.swisstopo.swissimage-product,ch.swisstopo.swissimage-product.metadata&layers_opacity=1,1,1,0.8,0.8,1,0.7&layers_visibility=false,false,false,false,false,true,true&layers_timestamp=18641231,,,,,2021,2021&time=2021) (no more than a third of Switzerland's surface area). 

### Software

- Ubuntu 20.04
- Python version 3.8 
- PyTorch version 1.10
- CUDA version 11.3
- GDAL version 3.0.4
- object-detector version [2.3.4](https://github.com/swiss-territorial-data-lab/object-detector/releases/tag/v.2.3.4)

### Installation

Install GDAL:

```bash
$ sudo apt-get install -y python3-gdal gdal-bin libgdal-dev gcc g++ python3.8-dev
```

Python dependencies can be installed with `pip` or `conda` using the `requirements.txt` file (compiled from `requirements.in`) provided. We advise using a [Python virtual environment](https://docs.python.org/3/library/venv.html).

- Create a Python virtual environment
```bash
$ python3.8 -m venv <dir_path>/<name of the virtual environment>
$ source <dir_path>/<name of the virtual environment>/bin/activate
```

- Install dependencies
```bash
$ pip install -r requirements.txt
```

- `requirements.txt` has been obtained by compiling `requirements.in`. Recompiling the file might lead to libraries version changes:
```bash
$ pip-compile requirements.in
```

## Getting started

### Files structure

The folders/files of the project `proj-dqry` (in combination with `object-detector`) is organised as follows. Path names can be customised by the user, and * indicates numbers which may vary:

<pre>.
├── config                                          # configurations files folder
│   ├── config_det.template.yaml                    # detection workflow template
│   ├── config_det.yaml                             # generic: detection workflow
│   ├── config_det_opendatacube.yaml                # example 2: detection workflow with ODC
│   ├── config_det_swissimage.yaml                  # example 1: detection workflow with swissimage
│   ├── config_track.yaml                           # detection tracking workflow
│   ├── config_trne.yaml                            # training and evaluation workflow
│   ├── config_trne_opendatacube.yaml               # example 2: training and evaluation workflow with ODC
│   ├── config_trne_swissimage.yaml                 # example 1: training and evaluation workflow with swissimage
│   ├── detectron2_config.yaml                      # generic: detectron 2
│   ├── detectron2_config_opendatacube.yaml         # example 2: detectron 2 with ODC
│   └── detectron2_config_swissimage.yaml           # example 1: detectron 2 with swissimage
├── data                                            # folder containing the input data
│   ├── AoI                                         # available on request
│   └── ground_truth                                                             
├── functions
│   ├── constants.py       
│   ├── metrics.py                         
│   └── misc.py                                
├── images                                          
├── models                                          # trained models
├── output                                          # outputs folders
│   ├── det                            
│   └── trne
├── scripts
│   ├── batch_process.sh                            # script to execute several commands
│   ├── filter_detections.py                        # script to filter detections
│   ├── get_dem.sh                                  # script downloading the swiss DEM and converting it to EPSG:2056
│   ├── get_slope.sh                                # script downloading the swiss slope raster and converting it to EPSG:2056
│   ├── merge_detections.py                         # script merging adjacent detections and attributing class
│   ├── merge_years.py                              # script merging all year detections layers
│   ├── plots.py                                    # script plotting detection tracking results
│   ├── prepare_data.py                             # script preparing data to be processed by the object-detector scripts
│   └── track_detections.py                         # script tracking overlaping detection trough years
├── .gitignore                                      
├── LICENSE
├── README.md                                      
├── requirements.in                                 # list of python libraries required for the project
└── requirements.txt                                # python dependencies compiled from requirements.in file
</pre>


## Data

Below is a description of the input data used for this project.

### Images
  - [_SWISSIMAGE Journey_](https://map.geo.admin.ch/#/map?lang=fr&center=2660000,1190000&z=1&bgLayer=ch.swisstopo.pixelkarte-farbe&topic=ech&layers=ch.swisstopo.swissimage-product@year=2024;ch.swisstopo.swissimage-product.metadata@year=2024) is an annual dataset of aerial images of Switzerland from 1946 to today. For this project, only RGB images from 1999 to the present are used. They include [_SWISSIMAGE 10 cm_](https://www.swisstopo.admin.ch/fr/geodata/images/ortho/swissimage10.html), _SWISSIMAGE 25 cm_ and _SWISSIMAGE 50 cm_. The images are downloaded from the geo.admin.ch server using the [XYZ](https://api3.geo.admin.ch/services/sdiservices.html#xyz) connector.
  - [_Landsat 8_](https://landsat.gsfc.nasa.gov/satellites/landsat-8/) products are used:
    - True colour images, collection 2, level 2 and a 30 m spatial resolution are used for Switzerland via the [SDC](https://explorer.swissdatacube.org/products/landsat_ot_c2_l2).
    - True and false colour image mosaics, with 30 m spatial resolution covering the Brazilian Amazon, are used for Brazil via the [BDC](https://data.inpe.br/bdc/web/en/home-page-2/).
  - [_Sentinel-2_](https://www.esa.int/Applications/Observing_the_Earth/Copernicus/Sentinel-2) (s2) image mosaics in false colour and 10 m spatial resolution are used for Brazil via the [BDC](https://data.inpe.br/bdc/web/en/home-page-2/).

### Ground truth
  - The MES labels of Switzerland come from the [_swissTLM3D_](https://www.swisstopo.admin.ch/fr/geodata/landscape/tlm3d.html) product. The file _mes_swisstlm3d_swissimage2020.shp_, used for training, has been reviewed and synchronised with the 2020 _SWISSIMAGE 10 cm_ mosaic. The file _mes_swisstlm3d_swissimage2020_landsat-fp-2020-08-11.shp_ has been adapted to the footprint of the Landsat image covering Switzerland on 11-08-2020.
  - A global dataset of mining areas in the world has been compiled by [Maus et al. (2020)](https://www.nature.com/articles/s41597-020-00624-w) and can be downloaded [here](https://doi.pangaea.de/10.1594/PANGAEA.910894). The dataset has been adapted to our needs by synchronising them with image data and AoI (_mes_Maus2020_landsat-brazil-6m_2017-07_epsg4326.shp_ and _mes_Maus2020_s2-amazon-biome-3m_epsg4326.shp_).
  **GT dataset from Tang, L., Werner, T.T. (https://doi.org/10.1038/s43247-023-00805-6), focusing on the principal MES of Brazil with few labels**
  - A dataset of artisanal gold mines detected in the Amazon, established by [Earth Genome](https://github.com/earthrise-media) since 2018, is available [here](https://github.com/earthrise-media/mining-detector). For the study we selected data from 2018 (_artisanal-mes_Earth-Genome_detections-2018.shp_) and 2022 (_artisanal-mes_Earth-Genome_detections-2022.shp_).

### AoI
  - The footprints of _SWISSIMAGE_ acquisition by year (_swissimage_footprint__*_.shp_) can be found [here](https://map.geo.admin.ch/?lang=fr&topic=ech&bgLayer=ch.swisstopo.pixelkarte-farbe&layers=ch.swisstopo.zeitreihen,ch.bfs.gebaeude_wohnungs_register,ch.bav.haltestellen-oev,ch.swisstopo.swisstlm3d-wanderwege,ch.astra.wanderland-sperrungen_umleitungen,ch.swisstopo.swissimage-product,ch.swisstopo.swissimage-product.metadata&layers_opacity=1,1,1,0.8,0.8,1,0.7&layers_visibility=false,false,false,false,false,true,true&layers_timestamp=18641231,,,,,2021,2021&time=2021). The shapefiles of _SWISSIMAGE_ acquisition footprint from 2015 to 2020 are provided in this repository.
  - The polygon for the study area in the Brazilian Amazon is provided in this repository.

### DEM and slope
  The DEM and slope of Switzerland used in this project have been processed by Lukas Martinelli and can be downloaded [here](https://github.com/lukasmartinelli/swissdem).

### Trained models
  - The trained model used to produce the results with _SWISSIMAGE_ presented in the [documentation](https://github.com/swiss-territorial-data-lab/stdl-tech-website/tree/master/docs/PROJ-DQRY) and achieving a f1 score of 82% is available on request.
  - The models trained on satellite images for the Swiss and Brazilian use cases presented in the [documentation](https://github.com/swiss-territorial-data-lab/stdl-tech-website/tree/master/docs/PROJ-DQRY) are available on request.


## Scripts

The `proj-dqry` repository contains scripts to prepare the data and post-process the results. Hereafter a short description of each script:

1. `prepare_data.py`: format labels and produce tiles to be processed in the OD.
2. `merge_detections.py`: merge adjacent detections cut by tiles into a single detection and assign a class more than one is defined (the class of the maximum area).
3. `filter_detections.py`: filter detections by overlap with other vector layers. The overlapping portion of the detection can be removed or a new attribute column is created to indicate the overlapping ratio with the layer of interest. Other information such as score, elevation, slope are also displayed.
4. `merge_years.py`: merge all the detection layers obtained during inference by year.
5. `track_detections.py`: identify and track an detection of an object over a multiple year datasets. 
5. `plots.py`: plot some parameters of the detections to help understand the results (optional).
7. `get_dem.sh`: download the DEM of Switzerland.
8. `get_slope.sh`: download the slope raster of Switzerland.
9. `batch_process.sh`: batch script to perform the inference workflow over several years.


Object detection is performed with tools present in the [`object-detector`](https://github.com/swiss-territorial-data-lab/object-detector) git repository. 


 ## Workflow instructions

The workflow can be executed by running the following list of actions and commands. A generic workflow is provided, along with two use cases: the first using SWISSIMAGE data to reproduce the results presented [here](https://tech.stdl.ch/PROJ-DQRY-TM/) ; the second using satellite images via ODC to reproduce the results presented [here](https://tech.stdl.ch/PROJ-DQRY-TM/).

Adjust the paths and input values/data of the configuration files accordingly. The contents of the configuration files in squared brackets must be assigned. Uncomment/comment the lines corresponding to the requirements accordingly.

<details>
  <summary>Generic</summary> 

  ### Training and evaluation: 
  
  - Prepare the data:
  ```bash
  $ python scripts/prepare_data.py config/config_trne.yaml
  $ stdl-objdet generate_tilesets config/config_trne.yaml
  ```

  - Train the model:
  ```bash
  $ stdl-objdet train_model config/config_trne.yaml
  $ tensorboard --logdir output/trne/logs
  ```

  Open the following link with a web browser: `http://localhost:6006` and identify the iteration minimising the validation loss and select the model accordingly (`model_*.pth`) in `config_trne`. 

  - Perform and assess detections:
  ```bash
  $ stdl-objdet make_detections config/config_trne.yaml
  $ stdl-objdet assess_detections config/config_trne.yaml
  ```

  - Finally, the detections obtained by tiles can be merged when adjacent and a new assessment is performed:
  ```bash
  $ python scripts/merge_detections.py config/config_trne.yaml
  ```
 
  ### Inference: 

  - Copy the selected trained model to the folder `models`:
  ```bash
  $ mkdir models
  $ cp output/trne/logs/<selected_model_pth> models
  ```

  - Process images:
  ```bash
  $ python scripts/prepare_data.py config/config_det.yaml
  $ stdl-objdet generate_tilesets config/config_det.yaml
  $ stdl-objdet make_detections config/config_det.yaml
  $ python scripts/merge_detections.py config/config_det.yaml
  $ scripts/get_dem.sh
  $ scripts/get_slope.sh
  $ python scripts/filter_detections.py config/config_det.yaml
  ```

  - The inference workflow has been automated and can be run for a batch of years (to be specified in the script) by executing these commands:
  ```bash
  $ scripts/get_dem.sh
  $ scripts/get_slope.sh
  $ scripts/batch_process.sh
  ```

  - Finally, all the detection layers obtained for each year are merged into a single geopackage.
  ```bash
  $ python scripts/merge_years.py config/config_det.yaml
  ```

### Detection tracking: 

```bash
$ python scripts/track_detections.py config/config_track.yaml
$ python scripts/plots.py config/config_track.yaml
```

</details>


<details>
  <summary>Example 1: SWISSIMAGE aerial images</summary> 

  ### Training and evaluation: 
  
  - Prepare the data:
  ```bash
  $ python scripts/prepare_data.py config/config_trne_swissimage.yaml
  $ stdl-objdet generate_tilesets config/config_trne_swissimage.yaml
  ```

  - Train the model:
  ```bash
  $ stdl-objdet train_model config/config_trne_swissimage.yaml
  $ tensorboard --logdir output/trne/swissimage/logs
  ```

  Open the following link with a web browser: `http://localhost:6006` and identify the iteration minimising the validation loss and select the model accordingly (`model_*.pth`) in `config_trne_swissimage`. For the provided parameters, `model_0002999.pth` is the default one.

  - Perform and assess detections:
  ```bash
  $ stdl-objdet make_detections config/config_trne_swissimage.yaml
  $ stdl-objdet assess_detections config/config_trne_swissimage.yaml
  ```

  - Finally, the detections obtained by tiles can be merged when adjacent and a new assessment is performed:
  ```bash
  $ python scripts/merge_detections.py config/config_trne_swissimage.yaml
  ```
 
  ### Inference: 

  - Copy the selected trained model to the folder `models`:
  ```bash
  $ mkdir -p models/swissimage
  $ cp output/trne/swissimage/logs/<selected_model_pth> models/swissimage
  ```

  - Process images:
  ```bash
  $ python scripts/prepare_data.py config/config_det_swissimage.yaml
  $ stdl-objdet generate_tilesets config/config_det_swissimage.yaml
  $ stdl-objdet make_detections config/config_det_swissimage.yaml
  $ python scripts/merge_detections.py config/config_det_swissimage.yaml
  $ scripts/get_dem.sh
  $ scripts/get_slope.sh
  $ python scripts/filter_detections.py config/config_det_swissimage.yaml
  ```

  - The inference workflow has been automated and can be run for a batch of years (to be specified in the script) by executing these commands:
  ```bash
  $ scripts/get_dem.sh
  $ scripts/get_slope.sh
  $ scripts/batch_process.sh
  ```

  - Finally, all the detection layers obtained for each year are merged into a single geopackage.

  ```bash
  $ python scripts/merge_years.py config/config_det_swissimage.yaml
  ```

### Detection tracking: 

```bash
$ python scripts/track_detections.py config/config_track_swissimage.yaml
$ python scripts/plots.py config/config_track_swissimage.yaml
```

</details>


<details>
  <summary>Example 2: satellite images via Open Data Cubes</summary> 

   The configuration files provide use cases that have been used to train detection models with satellite images (Landsat 8 and Sentinel-2) for sites of interest in Switzerland and Brazil. The default case is the Brazilian area of interest with the Sentinel-2 image mosaic and ground truth from [Maus et al. (2020)](https://www.nature.com/articles/s41597-020-00624-w). The other cases can be selected by uncommenting/commenting the lines corresponding to the requirements and specifying the path of the output directory accordingly.


  ### Training and evaluation: 
  
  - Prepare the data:
  ```bash
  $ python scripts/prepare_data.py config/config_trne_opendatacubes.yaml
  $ stdl-objdet generate_tilesets config/config_trne_opendatacubes.yaml
  ```

  - Train the model:
  ```bash
  $ stdl-objdet train_model config/config_trne_opendatacubes.yaml
  $ tensorboard --logdir output/trne/<image_name>/logs
  ```

  Open the following link with a web browser: `http://localhost:6006` and identify the iteration minimising the validation loss and select the model accordingly (`model_*.pth`) in `config_trne_opendatacubes`. For the provided parameters, `model_0002999.pth` is the default one.

  - Perform and assess detections:
  ```bash
  $ stdl-objdet make_detections config/config_trne_opendatacubes.yaml
  $ stdl-objdet assess_detections config/config_trne_opendatacubes.yaml
  ```

  - Finally, the detections obtained by tiles can be merged when adjacent and a new assessment is performed:
  ```bash
  $ python scripts/merge_detections.py config/config_trne_opendatacubes.yaml
  ```
 
  ### Inference: 

  - Copy the selected trained model to the folder `models`:
  ```bash
  $ mkdir -p models/<image_name>
  $ cp output/trne/<image_name>/logs/<selected_model_pth> models
  ```

  - Process images:
  ```bash
  $ python scripts/prepare_data.py config/config_det_opendatacubes.yaml
  $ stdl-objdet generate_tilesets config/config_det_opendatacubes.yaml
  $ stdl-objdet make_detections config/config_det_opendatacubes.yaml
  $ python scripts/merge_detections.py config/config_det_opendatacubes.yaml
  ```
  Optional:
  ```bash
  $ scripts/get_dem.sh
  $ scripts/get_slope.sh
  ```

 - Filter images:
  ```bash
  $ python scripts/filter_detections.py config/config_det_opendatacubes.yaml
  ```

</details>

## Contributors

`proj-dqry` was made possible with the help of several contributors (alphabetical):

Alessandro Cerioni, Nils Hamel, Clémence Herny, Shanci Li, Adrian Meyer, Roxane Pott, Huriel Reichel, Gwenaëlle Salamin, Pierre Sledz.

## Disclaimer

Depending on the end purpose, we strongly recommend users not take for granted the detections obtained through this code. Indeed, results can exhibit false positives and false negatives, as is the case in all approaches based on machine learning.

## License

This project is licensed under the terms of the GNU GPLv3. Documentation and illustrations are licensed under the terms of the CC BY 4.0.