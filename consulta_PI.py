import os
import requests

offset = 0
total_results = 1
limit = 1
search_url = "https://api.mercadolibre.com/sites/MLC/search"

access_token = "APP_USR-8877411817973447-101813-fb174fefc7ba5be538005f50f1259fcf-1963157673"

params = {
    'category': 'MLC1459',
    'q': 'H Covarrubias 1.200 Mts Totales',
    'limit': limit,
    'offset': offset
    }

headers = {
    'Authorization': f'Bearer {access_token}'
}

response = requests.get(search_url, params=params, headers=headers)

if response.status_code == 200:
    total_results = response.json()['paging']['total']
    print(f'Offset: {offset} - Total: {total_results}')
    print(response.json()['results'][0])
else:
    print(f'Error: {response.json()}')