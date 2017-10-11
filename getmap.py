import os.path
import psycopg2
import osgeo.ogr
import requests
from zipfile import ZipFile
from datetime import datetime
from io import BytesIO

now = datetime.today()
day_of_year = datetime.strftime(now, "%j")
year = datetime.strftime(now, "%Y")
table = 'viirs_iband_fire_last7_' + year + '_' + day_of_year + '_conus'
url =  'https://fsapps.nwcg.gov/afm/data_viirs_iband/fireptdata/' + table + '_shapefile.zip'
shapefile = 'shp/' + table + '.shp'
geojson = 'www/geojson/' + table + '.geojson'

def get_and_unzip():
    zipped = requests.get(url)
    unzipped = ZipFile(BytesIO(zipped.content))
    unzipped.extractall(path='shp')

def insert_rows(raw_shapefile):
    conn = psycopg2.connect("dbname=fires")
    cursor = conn.cursor()
    cursor.execute("TRUNCATE firedata;")
    conn.commit()
    shp = osgeo.ogr.Open(raw_shapefile)
    layer = shp.GetLayer()
    for i in range(layer.GetFeatureCount()):
        feature = layer.GetFeature(i)
        wkt = feature.GetGeometryRef().ExportToWkt()
        bt4temp = feature.GetField("BT4TEMP")
        conf = feature.GetField("CONF")
        date_time = datetime.strptime(feature.GetField("DATE") + " " + str(feature.GetField("GMT")),"%Y/%m/%d %H%M")
        fire = feature.GetField("FIRE_")
        fire_id = feature.GetField("FIRE_ID")
        frp = feature.GetField("FRP")
        julian = feature.GetField("JULIAN")
        lat = feature.GetField("LAT")
        long = feature.GetField("LONG")
        sat_src = feature.GetField("SAT_SRC")
        spix = feature.GetField("SPIX")
        src = feature.GetField("SRC")
        tpix = feature.GetField("TPIX")
        cursor.execute("INSERT INTO firedata VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ST_GeometryFromText(%s, 4269))",
                    (bt4temp, conf, date_time, fire, fire_id, frp, julian, lat, long, sat_src, src, spix, tpix, wkt))
    conn.commit()


if __name__ == '__main__':
    get_and_unzip()
    insert_rows(shapefile)
