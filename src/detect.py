import os
import argparse
import numpy as np

from osgeo import gdal
import rasterio as rio
from rasterio.warp import reproject, calculate_default_transform
    

def __write(fn, arr, trans, crs='EPSG:4326', nodata=-1):
    """Write ndarray to GeoTiff.

    Args:
        fn (str): Output filename.
        arr (ndarray): Data to write to output.
        trans (object): Trasnform to write to output.
        crs (str, optional): The projection related to transform, desired for output. Defaults to 'EPSG:4326'.
        nodata (int, optional): Value indicating no data for a coordinate in output. Defaults to -1.
    """
    try:
        if os.path.exists(fn):
            os.remove(fn)
        
        # README does not specify if dtype needs to be unit8
        r_dataset = rio.open(fn, 'w', driver='GTiff',
                        height=arr.shape[0],
                        width=arr.shape[1],
                        nodata=nodata,
                        count=1,
                        dtype=str(arr.dtype),
                        crs={'init': crs},
                        transform=trans)

        r_dataset.write(arr, 1)
        r_dataset.close()
    except Exception as e:
        print('Unable to write data to GeoTiff!')
        print(e)
    
    
def __reproject(src_fn, src_arr, to_crs):
    """Reproject ndarray to CRS specified.

    Args:
        src_fn (str): Source GeoTiff, required to extract extra data from.
        src_arr (ndarray): Data to be reprojected.
        to_crs (str): CRS to reproject to.

    Returns:
        ndarray: Data reprojected.
        object: Transform data of the reprojected data.
    """
    with rio.open(src_fn) as src:
        src_crs = src.crs
        src_transform = src.transform
        crs = {'init': to_crs}
        
        if src_crs == to_crs:
            return src_arr, src_transform
        
        transform, width, height = calculate_default_transform(
            src_crs, 
            crs, 
            src.width, 
            src.height, 
            *src.bounds)
        
        dst_arr = np.full((height, width), -1, dtype=np.float32)
        
        reproject(
            source=src_arr,
            src_transform=src_transform,
            src_crs=src_crs,
            src_nodata=-1,
            destination=dst_arr,
            dst_transform=transform,
            dst_crs=crs,
            dst_nodata=-1)
        
    return dst_arr, transform


def evaluate_band_vegetation(arr_red, arr_nir, range=[0.0, 1.0]):
    """Calculate vegetation density of red and nir bands.
    Output is represented as either 0 or 255. If the value is within the range,
    it is scaled to 255, otherwise set or left at 0.

    Args:
        arr_red (ndarray): Red band numpy array.
        arr_nir (ndarray): NIR band numpy array.
        range (list, optional): Inclusive range of NDVI values to include in output. Defaults to [0.0, 1.0].

    Returns:
        ndarray: Array of calculated NVDI values for each coordinate clamped to range.
    """
    # Calculate NVDI values
    # Exception thrown for nan values but okay to ignore
    arr_ndvi = np.divide(np.subtract(arr_nir, arr_red), np.add(arr_nir, arr_red))
    arr_nan = np.nan_to_num(arr_ndvi, nan=-1)
    
    # Code must allow client code to specify the threshold for determining which NDVI values should be considered as part of a field.    
    # Pixels in output images should have a value of 255 where fields are located and 0 elsewhere.
    arr_clamped = np.where((arr_nan >= range[0]) & (arr_nan <= range[1]), 255, 0)
    arr_masked = np.where(arr_nan == -1, arr_nan, arr_clamped)
    return arr_masked
    

def evaluate_geotiff_vegetation(fn_in, fn_out, crs='EPSG:4326', range=[0.0, 1.0], band_red_index=6, band_nir_index=8):
    """Calculate NDVI data for input and output the results as a new GeoTiff.
    Output is represented as either 0 or 255. If the value is within the range,
    it is scaled to 255, otherwise set or left at 0. The output dtype is float32.

    Args:
        fn_in (str): Input GeoTiff filename, path.
        fn_out (str): Output GeoTiff filename, path.
        crs (str, optional): Projection to assign the output. Defaults to 'EPSG:4326'.
        range (list, optional): Inclusive range of NDVI values to include in output. Defaults to [0.0, 1.0].
        band_red_index (int): Index of red band in geotiff. Defaults to 6.
        band_nir_index (int): Index of NIR band in geotiff. Defaults to 8.
    """
    ds = gdal.Open(fn_in, gdal.GA_ReadOnly)
    arr_red = ds.GetRasterBand(band_red_index).ReadAsArray().astype('f4')
    arr_nir = ds.GetRasterBand(band_nir_index).ReadAsArray().astype('f4')
    
    # Determine based on other function's inputs of bands
    arr_result = evaluate_band_vegetation(arr_red, arr_nir, range=range)
    
    # Output a geotiff one in Lat/Long (EPSG 4326) projection.
    # Reproject the results to desired CRS
    arr_projected, transform = __reproject(fn_in, arr_result, crs)
    
    # Output a geotiff one in Lat/Long (EPSG 4326) projection.
    __write(fn_out, arr_projected, transform, crs=crs)


if __name__ == "__main__":
    print('Started program.\n')
    
    print('Reading arguments...')
    parser = argparse.ArgumentParser(prog='VegetationDensity')
    parser.add_argument('fn_input')
    parser.add_argument('fn_output')
    parser.add_argument('--crs', default='EPSG:4326')
    parser.add_argument('--range_min', type=float, default=0.2)
    parser.add_argument('--range_max', type=float, default=0.5)
    args = parser.parse_args()
    
    fn_in = args.fn_input
    fn_out = args.fn_output
    crs = args.crs
    range_min = args.range_min
    range_max = args.range_max
    
    if range_min >= range_max:
        print('Unable to process range [{}, {}], min can not be greater or equal to max.'.format(range_min, range_max))
        exit()
    
    print('Arguments: target_file \'{}\' out_file \'{}\' projection \'{}\' range \'{}-{}\'\n'.format(fn_in, fn_out, crs, range_min, range_max))
    
    print('Processing...')
    evaluate_geotiff_vegetation(fn_in, fn_out, crs=crs, range=[range_min, range_max])
    print('Complete!')
