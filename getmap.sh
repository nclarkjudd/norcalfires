#!/bin/bash

wget https://fsapps.nwcg.gov/afm/data_viirs_iband/fireptdata/viirs_iband_fire_last7_2017_282_conus_shapefile.zip
unzip -o viirs_iband_fire_last7_2017_282_conus_shapefile.zip -d shp 
ogr2ogr -sql "SELECT * FROM viirs_iband_fire_last7_2017_282_conus WHERE LAT < 42 AND LONG < -120 AND LONG > -124 AND LAT > 36" -f GeoJSON -t_srs crs:84 www/geojson/viirs_iband_fire_last7_2017_282_conus.geojson shp/viirs_iband_fire_last7_2017_282_conus.shp -mapFieldType Date|DATE=String
rm *.zip
