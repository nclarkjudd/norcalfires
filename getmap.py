import gdaltools
import requests
from zipfile import ZipFile
from datetime import datetime

now = datetime.today()
day_of_year = datetime.strftime(now, "%j")
year = datetime.strftime(now, "%Y")
table = 'viirs_iband_fire_last7_' + year + '_' + day_of_year + '_conus'
url =  'https://fsapps.nwcg.gov/afm/data_viirs_iband/fireptdata/' + table + '_shapefile.zip'
shapefile = 'shp/' + table + '.shp'


def get_and_unzip():
    zipped = requests.get(url)
    unzipped = zipfile.ZipFile(BytesIO(request.content))
    unzipped.extractall(path='shp')

if __name__ == '__main__':
    get_and_unzip()
