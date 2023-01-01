# NDVI Detection

The task is to determine NDVI values, reproject, scale, and output a geotiff based on another 8-band geotiff.

For more information, please refer to this [explanation](https://en.wikipedia.org/wiki/Normalized_difference_vegetation_index) on wikipedia.

<img src="docs/ndvi_screenshot.png" width="700">

## Prerequisite

To run the script, libraries are required.

- GDAL
- rasterio
- numpy

These can be installed in a new virtual env or found in a pre-existing docker image [Development Seed](https://developmentseed.org/blog/2017-08-17-introducing-geolambda) offers.

## How to

The script can be ran from the command line or included in a project as an import.

### Command line

The python script can be ran from the command line. Two arguments are required, an input and output file path, name.

`python detect.py input.tif output.tif`

**Optional arguments** include `--crs` and `--range`.

Including `--crs` tells the app to reproject the output to the given projection.

Including `--range` tells the app to clamp the output NDVI values to the given range.

#### Example

*From README directory*

`python ndvidetect/detect.py sample/sample.tif output/output.tif --crs EPSG:4326 --range_min 0.2 --range_max 0.5`

The geotif included (`output/output.tif`) was generated by the above command.

<img src="docs/output_screenshot.png" width="700">

### Importing

Once the repo is built/installed with python's setup tools (`python install .`), you can access key functions to calculate NDVI values of a geotiff.

`from ndvidetect import evaluate_band_vegetation, evaluate_geotiff_vegetation`

Once imported, these two functions can be used to determine NDVI values.

#### Example Usage

```
from ndvidetect import evaluate_geotiff_vegetation
    
if __name__ == "__main__":
    fn_in = 'sample.tif'
    fn_out = 'output.tif'
    evaluate_geotiff_vegetation(fn_in, fn_out, crs='EPSG:4326', range=[0.3, 0.6])
```

Further documentation is included on the functions.