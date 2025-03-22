import sys
import geopandas as gpd
from loguru import logger
from shapely.validation import make_valid


def check_validity(poly_gdf, correct=False):
    '''
    Test if all the geometry of a dataset are valid. When it is not the case, correct the geometries with a buffer of 0 m
    if correct != False and stop with an error otherwise.

    - poly_gdf: dataframe of geometries to check
    - correct: boolean indicating if the invalid geometries should be corrected with a buffer of 0 m

    return: a dataframe with valid geometries.
    '''

    invalid_condition = ~poly_gdf.is_valid

    if poly_gdf[invalid_condition].shape[0]!=0:
        logger.warning(f"{poly_gdf[invalid_condition].shape[0]} geometries are invalid on {poly_gdf.shape[0]} detections.")
        
        if correct:
            logger.info("Correction of the invalid geometries with the shapely function 'make_valid'...")
            
            invalid_poly = poly_gdf.loc[invalid_condition, 'geometry']
            try:
                poly_gdf.loc[invalid_condition, 'geometry'] = [
                    make_valid(poly) for poly in invalid_poly
                    ]
     
            except ValueError:
                logger.info('Failed to fix geometries with "make_valid", try with a buffer of 0.')
                poly_gdf.loc[invalid_condition, 'geometry'] = [poly.buffer(0) for poly in invalid_poly] 
        else:
            sys.exit(1)

    return poly_gdf


def format_logger(logger):

    logger.remove()
    logger.add(sys.stdout, format="{time:YYYY-MM-DD HH:mm:ss} - {level} - {message}",
            level="INFO", filter=lambda record: record["level"].no < 25)
    logger.add(sys.stdout, format="{time:YYYY-MM-DD HH:mm:ss} - <green>{level}</green> - {message}",
            level="SUCCESS", filter=lambda record: record["level"].no < 30)
    logger.add(sys.stdout, format="{time:YYYY-MM-DD HH:mm:ss} - <yellow>{level}</yellow> - {message}",
            level="WARNING", filter=lambda record: record["level"].no < 40)
    logger.add(sys.stderr, format="{time:YYYY-MM-DD HH:mm:ss} - <red>{level}</red> - <level>{message}</level>",
            level="ERROR")
    
    return logger


def merge_polygons(gdf, id_name='id'):
    '''
    Merge overlapping polygons in a GeoDataFrame.

    - gdf: GeoDataFrame with polygon geometries
    - id_name (string): name of the index column

    return: a GeoDataFrame with polygons
    '''

    merge_gdf = gdf.copy()
    merge_gdf = gpd.GeoDataFrame(geometry=[merge_gdf.geometry.unary_union], crs=gdf.crs) 
    merge_gdf = merge_gdf.explode(ignore_index=True)
    merge_gdf[id_name] = merge_gdf.index 

    return merge_gdf