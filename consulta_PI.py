import os
import requests

offset = 0
total_results = 1
limit = 50
search_url = "https://api.mercadolibre.com/sites/MLC/search"
results = []

access_token = "APP_USR-8877411817973447-102113-5dd9429b860861341b0615bf3cc54aec-1963157673"

while offset < total_results:

    params = {
        'category': 'MLC1459',
        'q': 'La Florida Casa',
        'limit': limit,
        'offset': offset
        }

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(search_url, params=params, headers=headers)

    if response.status_code == 200:
        total_results = response.json()['paging']['total']
        print(total_results)
        if total_results >= 4000:
            total_results = 4000
        print(f'Offset: {offset} - Total: {total_results}')
        results.append(response.json())
        offset += limit
    else:
        print(f'Error: {response.json()}')
        break
print(len(results), total_results)