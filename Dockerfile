# Dockerfile is copied over from other personal project that works with geotiffs.
# This has NOT BEEN TESTED but offered as an example of how this can be ran without
# installing required libraries onto local machine.
FROM developmentseed/geolambda:1.1.0-python36

WORKDIR /build

RUN pip install rasterio

COPY . /build

CMD ["python", "src/planetapp.py", "input.tif" "output.tif", "--range_min", "0.2", "--range_max", "0.5"]