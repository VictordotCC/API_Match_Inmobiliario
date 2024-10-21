import os
import requests

offset = 0
total_results = 1
limit = 1
search_url = "https://api.mercadolibre.com/sites/MLC/search"

access_token = ""

params = {
    'category': 'MLC1459',
    'q': 'La Florida',
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