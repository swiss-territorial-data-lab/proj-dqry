## Overview

This set of scripts and configuration files are related to the _quarry/exploitation sites_ detection case. The detector is initially trained on _swissimage_ from _swisstopo_ using the _TLM_ data of _swisstopo_ for the labels.

For this case, the _thermal panel (TPNL)_ case script is used. See its documentation on the [following page](../interface_proj-tpnl)

## Required repositories
https://github.com/swiss-territorial-data-lab/proj-dqry.git
https://github.com/swiss-territorial-data-lab/object-detector.git

## Required input data
https://kdrive.infomaniak.com/app/drive/548133/files
access path : /STDL/Common Documents/Projets/En_cours/Quarries_TimeMachine/02_Data/

Training and Evaluation:
* Input tiles = tiles_500_0_0.shp
* Input labels = tlm-hr-trn-topo.shp

## Configuration files

Two files are provided along the prepare script :

* config.yaml
* logging.conf

The logging format file can be used as provided. 
The configuration _YAML_ has been set for the object detector workflow by reading dedicated section. It has to be adapted in terms of input and output location and files.

The section of the _yaml_ configuration file is expected as follows :

* for tiles defined through _CSV_ file:

    prepare_data.py:
      srs: "EPSG:2056"
      tiling:
        csv: [TILE_CSV_FILE]
        split: 1
      label:
        shapefile: [LABEL_SHAPEFILE]
       # redfact: 0.9
      output_folder: ../output

* for tiles defined through a shapefile:

    prepare_data.py:
      srs: "EPSG:2056"
      tiling:
        shapefile: [TILE_SHAPEFILE]
        split: 1
      label:
        shapefile: [LABEL_SHAPEFILE]
       # redfact: 0.9
      output_folder: ../output

The lables section can be missing, indicating that tiles are prepared for inference only.

The _redfact_ key allows to specify the reduction factor of the label that is performed before removing empty tiles (tiles with empty intersection with all labels). Reducing the labels before removing empty tiles allows to force tiles with small overlap with labels to be removed. This allows not to consider tiles with a small portion of label at its edges.

In both case, the _srs_ key provides the working geographical frame in order for all the input data to work together.

### CSV Specified Tiles

The _CSV_ file has to give the bounding box of each tile to consider. Each _CSV_ are expected to contain at least the following values :

    x_min, y_min, x_max, y_max

giving the tile bounding box coordinates. The _CSV_ file is specified using the _csv_ key in the _tiling_ section.

The _split_ key in the tiling section allows the script to divide the tiles into sub-tiles.

### Shapefile Specified Tiles

In case a _shapefile_ is used for tiles definition, it has to contain the tiles as simple _polygons_ providing the shape of each tile.

The _split_ key in the tiling section allows the script to divide the tiles into sub-tiles.

## Workflow

### Training and Validation

The scripts are used in the following way :

    $ cd [process_directory]
    $ python3 prepare_data.py --config [yaml_config] --logger [logging_config]
    $ python3 [object-detector_path]/scripts/generate_tilesets.py [yaml_config]
    $ cd [output_directory]
    $ tar -cvf images-[image_size].tar COCO_{trn,val,tst}.json && \
      tar -rvf images-[image_size].tar {trn,val,tst}-images-[image_size] && \
      gzip < images-[image_size].tar > images-[image_size].tar.gz && \
      rm images-[image_size].tar
    $ cd -
    $ cd [process_directory]
    $ python3 [object-detector_path]/scripts/train_model.py config.yaml
    $ python3 [object-detector_path]/scripts/make_prediction.py config.yaml
    $ python3 [object-detector_path]/scripts/assess_predictions.py config.yaml

### Prediction

From the Training and Validation procedure, copy from the output folder the log and detectron  