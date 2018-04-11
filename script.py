from api import InstagramAPI
import requests
import json

api = InstagramAPI(username='iv01020', password='qwerty123456')
api.login()

api.searchUsername('olesgonchar')

print(api.LastJson)

