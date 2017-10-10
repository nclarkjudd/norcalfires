#!/bin/bash

wget https://fsapps.nwcg.gov/afm/data_viirs_iband/fireptdata/viirs_iband_fire_last7_2017_282_conus_shapefile.zip
unzip viirs_iband_fire_last7_2017_282_conus_shapefile.zip -d shp
ogr2ogr -sql "SELECT * FROM viirs_iband_fire_last7_2017_282_conus WHERE CAST(DATE AS date) > CAST('2017-10-08' AS date)" -f GeoJSON -t_srs crs:84 www/geojson/viirs_iband_fire_last7_2017_282_conus.geojson shp/viirs_iband_fire_last7_2017_282_conus.shp -mapFieldType Date|DATE=String
