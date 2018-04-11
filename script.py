from api import InstagramAPI
import requests
import json
import time

api = InstagramAPI(username='iv01020', password='qwerty123456')
api.login()

def get_photo_id(url_list):
    id_list = []
    for url in url_list:
        profile = requests.get(url + '?__a=1')

        try:
            profile = json.loads(profile.text)
        except:
            print('Пользователь не найден или доступ закрыт')
            exit()

        pictures = profile['graphql']['user']['edge_owner_to_timeline_media']['edges']
        for picture in pictures:
            id_list.append(int(picture['node']['id']))
        time.sleep(5)
    return id_list

print(get_photo_id(['https://www.instagram.com/olesgonchar/', 'https://www.instagram.com/dr._.marcus/', 'https://www.instagram.com/masha_polosukhina/']))