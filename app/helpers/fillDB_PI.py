import requests
import math

def fillDB_PI(access_token, consulta):
    offset = 0
    total_results = 1
    limit = 1
    responses = []
    search_url = "https://api.mercadolibre.com/sites/MLC/search"

    while offset < total_results:

        params = {
            'category': 'MLC1459',
            'q': consulta,
            'limit': limit,
            'offset': offset
            }
        
        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        response = requests.get(search_url, params=params, headers=headers)

        """if response.status_code == 200:
            print(response.json()['results'][0])
            break"""

        if response.status_code == 200:
            total_results = response.json()['paging']['total']
            print(f'Offset: {offset} - Total: {total_results}')

            responses.append(response.json())
            offset += limit

            return responses
        else:
            print(f'Error: {response.status_code}')
            return responses
        
