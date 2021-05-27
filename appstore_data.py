from config import appstore_url
import requests, time, json 
from authlib.jose import jwt

def app_store_data_extraction(token, appstore_url):
    JWT = 'Bearer ' + token.decode()
    URL = appstore_url
    HEAD = {'Authorization': JWT}

    r = requests.get(URL, params={'limit': 200}, headers=HEAD)

    return r.json()
