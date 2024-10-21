import geopandas as gpd
from app import  gdf_wgs84

def leer_georef(lat, lon):
    point = gpd.points_from_xy([lon], [lat], crs="EPSG:4326")
    mask = gdf_wgs84.contains(point[0])
    comuna = gdf_wgs84[mask]['Comuna'].values[0]
    provincia = gdf_wgs84[mask]['Provincia'].values[0]
    region = gdf_wgs84[mask]['Region'].values[0]

    return {'comuna': comuna, 'ciudad': provincia, 'region': region}