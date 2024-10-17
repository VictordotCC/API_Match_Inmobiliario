import requests
import os
from dotenv import load_dotenv
import datetime

load_dotenv()

def refresh_token():
        
    client_id = os.environ.get('CLIENT_ID')
    client_secret = os.environ.get('CLIENT_SECRET')
    refresh_token = os.environ.get('REFRESH_TOKEN')
    expires_date = os.environ.get('EXPIRES_DATE')

    token_url = 'https://api.mercadolibre.com/oauth/token'

    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret
    }

    if datetime.datetime.now() > datetime.datetime.strptime(expires_date, '%Y-%m-%d %H:%M:%S.%f'):
        print("Token expirado, renovando token...")
        response = requests.post(token_url, data=payload)

        if response.status_code == 200:
            respuesta = response.json()
            print(f"Access Token: {respuesta}")
            with open('.env', 'r') as file:
                lines = file.readlines()

            with open('.env', 'w') as file:
                for line in file:
                    if "ACCESS_TOKEN" in line:
                        file.write(f'ACCESS_TOKEN={respuesta["access_token"]}\n')
                    elif "REFRESH_TOKEN" in line:
                        file.write(f'REFRESH_TOKEN={respuesta["refresh_token"]}\n')
                    elif "EXPIRES_DATE" in line:
                        file.write(f'EXPIRES_DATE={datetime.datetime.now() + datetime.timedelta(seconds=respuesta["expires_in"])}\n')
                    else:
                        file.write(line)
            os.environ['ACCESS_TOKEN'] = respuesta['access_token']
            os.environ['REFRESH_TOKEN'] = respuesta['refresh_token']
        else:
            print(f"Error al obtener el token: {response.status_code} - {response.text}")
    else:
        print("Token aun no ha expirado")
    return

        