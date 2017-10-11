import os.path
import psycopg2
import osgeo.ogr
import requests
from zipfile import ZipFile
from datetime import datetime, timedelta
from io import BytesIO

now = datetime.today()
day_of_year = datetime.strftime(now, "%j")
year = datetime.strftime(now, "%Y")
last_24hrs = datetime.today() - timedelta(hours=24)
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
    conn.close()

def get_activity(from_after):
    conn = psycopg2.connect("dbname=fires")
    cursor = conn.cursor()
    makeview_str = "CREATE OR REPLACE VIEW active_fire_buffers AS"\
                   " SELECT ST_Buffer(ST_Transform(geom, 3311),187.5,'quad_segs=1') AS new_geom,"\
                   " bt4temp, conf, date_time, frp FROM firedata"\
                   " WHERE date_time > %s;"
    makeview_data = (from_after,)
    cursor.execute(makeview_str, makeview_data)
    conn.commit()
    get_geojson = "SELECT row_to_json(fc)"\
                  "FROM ( SELECT 'FeatureCollection' As type, array_to_json(array_agg(f)) As features"\
                  "FROM (SELECT 'Feature' As type, "\
                  "ST_AsGeoJSON(afb.new_geom)::json As geometry, "\
                  "row_to_json((SELECT l FROM (SELECT bt4temp, conf, date_time, frp) AS l "\
                  ")) As properties "\
                  "FROM active_fire_buffers As afb   ) As f )  As fc;"
    cursor.execute(get_geojson)
    geojson = cursor.fetchall()
    with open('www/geojson/latest_fire_buffers.geojson','w') as outf:
        json.dump(geojson[0],outf)


if __name__ == '__main__':
    get_and_unzip()
    insert_rows(shapefile)
    get_activity(last_24hrs)
