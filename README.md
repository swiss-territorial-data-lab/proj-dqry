# Automatic detection of mineral extraction sites in Switzerland

## Overview

This set of scripts and configuration files are related to the _quarry/exploitation sites_ detection case. The detector is initially trained on _swissimage_ from _swisstopo_ using the _TLM_ data of _swisstopo_ for the labels.

The workflow is defined in two distinct procedures:
* the Training and Evaluation procedure allows for the training of the detection model on a given dataset and its evaluation with the ground truth dataset examined by domain experts.
* the detections procedure performing detection of quarries in a given dataset thanks to the previously trained model.

The quarry are detected with the tools developped in the `object-detector` developped by the STDL and located [here](https://github.com/swiss-territorial-data-lab/object-detector). Version 1.0.0 of `proj-dqry` works along with version 1.0.0 of `object-detector`. 

Full documentation of the project can be found [here](https://tech.stdl.ch/PROJ-DQRY/).

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

The input data for the **Training and Evaluation** and **Detection** workflows for the quarry detection project can either be found in input folders and/or are stored on the STDL kDrive (https://kdrive.infomaniak.com/app/drive/548133/files) with the following access path: /STDL/Common Documents/Projets/En_cours/Quarries_TimeMachine/02_Data/, available on request.

* DEM
    - swiss-srtm.tif: DEM of Switzerland produced from SRTM instrument. The raster is used to filter the detection according to an elevation threshold. It is available on request.
* Learning models
    - logs: folder containing trained detection model at several learning iteration. They have been obtained during the model training phase. The optimum model minimizing the validation loss curve. The learning characteristics of the algorithm can be visualized using tensorboard (see below in Processing/Run scripts). The optimum model obtained during the **Training and Evaluation** phase is used to perform the **Detections** phase. The algorithm has been trained on [SWISSIMAGE 10 cm](https://www.swisstopo.admin.ch/fr/geodata/images/ortho/swissimage10.html) data with a 1 m/px resolution.
* Shapefiles
    - quarry_label_tlm_revised: `tlm-hr-trn-topo.shp` is a polygons shapefile of the quarries labels (TLM data) reviewed by the domain experts. This file has been used to train and assess the automatic detection algorithms = Ground Truth.
    - swissimage_footprints_shape_year_per_year: original SWISSIMAGE footprints and processed polygons border shapefiles for every SWISSIMAGE acquisition year.
    - switzerland_border: polygon shapefile of the Switzerland border. 
    - tiles_prd: tiles shapefile (tiles_500_0_0_[number].shp) of the defined AoI. This file can be created with the pre-processing script `tile-generator.py` with `tiles_prediction0x.geojson` as input.   
    - tiles_trne: tiles shapefile (tiles_500_0_0.shp) intersecting labeled quarries in `tlm-hr-trn-topo.shp` file. This file can be created with the pre-processing script `tile-generator.py`. It contains the tiles as simple _polygons_ providing the shape of each tile.
*	SWISSIMAGE
    - Explanation.txt: file explaining the main characteristics of SWISSIMAGE and the references links (written by R. Pott).


## Workflow

### Training and Evaluation

- Pre-processing

The pre-processing, performed with the script `tile-generator.py`, generates a shapefile with tiles of a given size for an AoI defined by an input shapefile.

```bash
$ python3 pre-processing/tile-generator.py 
                                    --labels [polygon_shapefile] 
                                    --size [tile_size]
                                    --output [output_directory]
                                    [--x-shift/--y-shift [grid origin shift]]
```

For the quarries example:

    [polygon_shapefile] = input/input-trne/tlm-hr-trn-topo.shp
    [tile_size] = 500 (m)
    [output_directory]: input/input-trne/

- Processing

-Working directory and paths

By default the working directory is: 

    $ cd proj-dqry/config/

-Config and input data

Two config files are provided in `proj-dqry`:

    [yaml_config] = config-trne.yaml 
    [logging_config] = logging.conf

The logging format file can be used as provided. The configuration _YAML_ has been set for the object detector workflow by reading dedicated section. It has to be adapted in terms of input and output location and files.

The `prepare_data.py` section of the _yaml_ configuration file is expected as follows :

```bash
prepare_data.py:
    srs: "EPSG:2056"
    tiling:
        shapefile: ../input/input-trne/[Tile_Shapefile]
    label:
        shapefile: ../input/input-trne/[Label_Shapefile]
    output_folder: ../output/output-trne
```

Set the path to the desired tiles shapefile (tiling) and to the AoI shapefile (label).

For the quarries example:

    [Tile_Shapefile] = tiles_500_0_0.shp   # Output of the script `tile-generator.py`  
    [Label_Shapefile] = tlm-hr-trn-topo.shp

In both case, the _srs_ key provides the working geographical frame in order for all the input data to work together.

-Run scripts

The scripts can be executed as follow:

```bash
$ python3 ../scripts/prepare_data.py --config config-trne.yaml --logger logging.conf
$ python3 [object-detector_path]/scripts/generate_tilesets.py config-trne.yaml
$ cd [output_directory]
$ tar -cvf images-[image_size].tar COCO_{trn,val,tst}.json && \
    tar -rvf images-[image_size].tar {trn,val,tst}-images-[image_size] && \
    gzip < images-[image_size].tar > images-[image_size].tar.gz && \
    rm all-images-[image_size].tar
$ cd -
$ cd [process_directory]
$ python3 [object-detector_path]/scripts/train_model.py config-trne.yaml
$ python3 [object-detector_path]/scripts/make_detections.py config-trne.yaml
$ python3 [object-detector_path]/scripts/assess_detections.py config-trne.yaml
```

In between the `train_model.py` and `make_detections.py` script execution, the output of the detection model training must be checked and the optimum model , i.e. the one minimizing the validation loss curve, must be chosen (obtained for a given iteration number) and set as input (model_weights: pth_file:./logs/[chosen model].pth) to make the detections. For the quarry example the optimum is obtained for a learning iteration around 2000-3000. The file model_final correspond to the last iteration recorded during the training procedure.

The validation loss curve can be visualized with `tensorboard` 

    tensorboard --logdir [logs folder]

And open the following link with a web browser: `http://localhost:6006`


### Detection

- Pre-processing

The pre-processing, performed with the script `tile-generator.py`, generates a shapefile with tiles of a given size for an AoI defined by an input shapefile.

```bash
$ python3 pre-processing/tile-generator.py --labels [polygon_shapefile] 
                                    --size [tile_size]
                                    --output [output_directory]
                                    [--x-shift/--y-shift [grid origin shift]]
```

For the quarries example:

    [polygon_shapefile] = input/input-prd/tiles_detections0x.geojson
    [tile_size] = 500 (in px)
    [output_directory]: input/input-prd/

- Processing

-Working directory and paths

By default the working directory is:

    $ cd /proj-dqry/config/

-Config and input data

Two config files are provided in `proj-dqry`:

    [yaml_config] = config-prd.yaml 
    [logging_config] = logging.conf

Choose the relevant `model_*.pth` file, i.e. the one minimizing the validation loss curve (see above Training and Evaluation/Processing/Run scripts) and copy it to input/input-prd/logs/. 

The `prepare_data.py` section of the _yaml_ configuration file is expected as follows :

```bash
prepare_data.py:
    srs: "EPSG:2056"
    tiling:
        shapefile: ../input/input-trne/[Tile_Shapefile]
    label:
        shapefile: ../input/input-trne/[Label_Shapefile]
    output_folder: ../output/output-trne
```

Set the path to the desired tiles shapefile (tiling) and to the AoI shapefile (label).

For the quarries example:

    [Tile_Shapefile] = tiles_500_0_0.shp
    [Label_Shapefile] = tiles_500_0_0.shp

In both case, the _srs_ key provides the working geographical frame in order for all the input data to work together.

-Run scripts

The scripts can be executed as follow:

```bash
$ python3 ../scripts/prepare_data.py --config config-prd.yaml --logger logging.conf
$ python3 [object-detector_path]/scripts/generate_tilesets.py config-prd.yaml
$ cd [output_directory]
$ tar -cvf images-[image_size].tar COCO_{trn,val,tst}.json && \
    tar -rvf images-[image_size].tar {trn,val,tst}-images-[image_size] && \
    gzip < images-[image_size].tar > images-[image_size].tar.gz && \
    rm all-images-[image_size].tar
$ cd -
$ cd [process_directory]
$ python3 [object-detector_path]/scripts/make_detections.py config-prd.yaml
```

- Post-processing

The quarry detections output as a polygons shapefile needs a filtering procedure to discard false detections and improve the aesthetic of the polygons (merge polygons belonging to a single quarry). This is performed the script `prediction-filter.py`:

```bash
$ python post-processing/prediction-filter.py --input [detections shapefile GeoJSON]
				     	                --dem [digital elevation model GeoTiff]
                          	            --score [threshold value]
                                        --area [threshold value]
                                        --distance [threshold value]
                                        --output [Output GeoJSON]
```

-input: indicate path to the input geojson file that needs to be filtered, i.e. oth_detections.geojson

-dem: indicate the path to the DEM of Switzerland. A SRTM derived product is used and can be found in the STDL kDrive. A threshold elevation is used to discard detection above the given value. Indeed 1st tests have shown numerous false detection were due to snow cover area (reflectance value close to bedrock reflectance) or mountain bedrock exposure. By default the threshold elevation has been set to 1155 m.

-score: each polygon comes with a confidence score given by the detections algorithm. Polygons with low scores can be discarded. By default the value is set to 0.96.

-area: small area polygons can be discarded assuming a quarry has a minimal area. The default value is set to 1728 m2.

-distance: two polygons that are close to each other can be considered to belong to the same quarry. Those polygons can be merged into a single one. By default the value is set to 8 m.

-output: provide the path and name of the filtered polygons shapefile

## Copyright and License

The pre-processing and post-processing scripts originate from the git repository `detector-interface`
  
**detector-interface** - Nils Hamel, Adrian Meyer, Huriel Reichel, Alessandro Cerioni <br >
Copyright (c) 2020-2022 Republic and Canton of Geneva

This program is licensed under the terms of the GNU GPLv3. Documentation and illustrations are licensed under the terms of the CC BY 4.0.