## Overview

This project provides a suite of scripts and configuration files to perform quarries automatic detections in georeferenced raster images with Deep Learning method. For object detection, tools developed in `object-detector` git repository are used.

The procedure is defined in three distinct workflows:
* **Training and Evaluation** workflow allows training the detection model on a given image dataset (year) and evaluated to ground truth dataset reviewed by domain experts. The detector is initially trained on _swissimage_ mosaic of 2020 (_swisstopo_) from using the _TLM_ data of _swisstopo_ as Ground Truth.
* **Prediction** workflow performing inference detection of quarries in a given image dataset (year) thanks to the previously trained model.
* **Detection monitoring** workflow tracking quarry evolution over years.


## Hardware and OS requirements

The workflows have been run with Ubuntu 20.04 OS on a GPU machine with 32 Gbits RAM. The main limitation is the number of tiles to proceed and the amount of prediction. The provided requirements stand for a zoom level equal to or below 17 and for an AOI corresponding to SWISSIMAGE acquisition footprints (about a third of Switzerland surface max). For higher zoom level and/or a larger AOI, the number of data to process might lead to memory saturation. In this case either a more powerful machine will be required, or the AOI will need to be subdivided in a smaller area.

## Python libraries

The scripts have been developed with Python 3.8 by importing libraries that are listed in `requirements.in` and `requirements.txt`. Before starting to run scripts make sure the required Python libraries that have been used during the code development are installed, otherwise incompatibilities and errors could occur. A clean method to install Python libraries is to work with a virtual environment preserving the package dependencies.

## Scripts and configuration files

The `proj-dqry` repository contains **scripts** to prepare and post-process the datasets:

	1. prepare_data.py
	2. prediction_filter.py
	3. detection_monitoring.py
	4. plots.py

The description of each script can be found [here](/scripts/README.md).  

In addition, the object detection itself is performed by tools developed in `object-detector` git repository. The description of the scripts used are presented here: https://github.com/swiss-territorial-data-lab/object-detector

Configurations files used to set the input parameters of the scripts and model are located in the **config** folder:

	1. config-trne.yaml
	2. config-prd.yaml
	3. config-dm.yaml
	4. detectron2_config_dqry.yaml

 The detailed instructions to run the workflows can be found [here](/config/README.md).

## Copyright and License
 
**proj-dqry** - Nils Hamel, Adrian Meyer, Huriel Reichel, Clémence Herny, Shanci Li, Alessandro Cerioni <br >
Copyright (c) 2020-2022 Republic and Canton of Geneva

This program is licensed under the terms of the GNU GPLv3. Documentation and illustrations are licensed under the terms of the CC BY 4.0.