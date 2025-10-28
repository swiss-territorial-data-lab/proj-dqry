################################################################
#  Script used to run automatically Detections workflow for MES detection
#  Inputs are defined in config_det_swissimage.template.yaml


echo 'Run batch processes to perfomr Mineral Extraction Site detections over several years'

for year in YEAR1 YEAR2 YEAR3     # list of years to process (no comma: YEAR1 YEAR2 YEAR3 ...) 
do
    echo ' '
    echo '-----------'
    echo Year = $year
    sed 's/#YEAR#/$year/g' config/config_det_swissimage.template.yaml > config/config_det_swissimage_$year.yaml
    sed -i "s/SWISSIMAGE_YEAR/$year/g" config/config_det_swissimage_$year.yaml
    echo ' '
    echo 'prepare_data.py'
    python ./scripts/prepare_data.py config/config_det_swissimage_$year.yaml
    echo ' '
    echo 'generate_tilesets.py'
    stdl-objdet generate_tilesets config/config_det_swissimage_$year.yaml
    echo ' '
    echo 'make_detections.py'
    stdl-objdet make_detections config/config_det_swissimage_$year.yaml
    echo ' '
    echo 'merge_detections.py'
    python ./scripts/merge_detections.py config/config_det_swissimage_$year.yaml
    echo ' '
    echo 'filter_detections.py'
    python ./scripts/filter_detections.py config/config_det_swissimage_$year.yaml
done