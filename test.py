import geopandas as gpd
from app import  gdf_wgs84

import requests
import re

def leer_georef(lat, lon, address=None):
    if lat is None or lon is None:
        matches = re.findall(r'\d+', address)
        number = 0
        i = 0
        if matches:
            for match in matches:
                number += int(match)
                i += 1
            number = int(number / i)
        address = re.sub(r'\d+', '', address).replace('-', '').strip()
        address = f'{address} {number}'
        params = {
            'street': address,
            'country': 'Chile',
            'format': 'json',
            'limit': 1
        }
        response = requests.get('https://nominatim.openstreetmap.org/search', params=params)
        if response.status_code == 200:
            data = response.json()
            print('data: ' + str(data))
            lat = data[0].get('lat', None)
            lon = data[0].get('lon', None)
        else:
            return None
    if lat is None or lon is None:
        return None
    
    point = gpd.points_from_xy([lon], [lat], crs="EPSG:4326")
    mask = gdf_wgs84.contains(point[0])
    if mask.any():
        comuna = gdf_wgs84[mask]['Comuna'].values[0]
        provincia = gdf_wgs84[mask]['Provincia'].values[0]
        region = gdf_wgs84[mask]['Region'].values[0]
        return {'comuna': comuna, 'ciudad': provincia, 'region': region}
    else:
        return None


