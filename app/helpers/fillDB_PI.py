import requests

def fillDB_PI(access_token, consulta):
    offset = 0
    total_results = 1
    limit = 50
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
            if total_results >= 4000:
                total_results = 4000 #Limite de resultados impuesto por MercadoLibre

            responses.append(response.json())
            offset += limit
        else:
            print(f'Error: {response.status_code}')
            return responses
    return responses
        
