import requests
import re

address = "Sergio Vieira de Mello 4500 - 4800"
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
print(address)

params = {
        'street': address,
        'country': 'Chile',
        'format': 'json',
        'limit': 1
    }
response = requests.get('https://nominatim.openstreetmap.org/search', params=params)
if response.status_code == 200:
    data = response.json()
    print(data[0].get('lat', None), data[0].get('lon', None))