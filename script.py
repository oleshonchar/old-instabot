from api import InstagramAPI
import requests
import json
import time

api = InstagramAPI(username='iv01020', password='qwerty123456')
api.login()

def get_photo_id(url_list):
    photo_list = []
    for url in url_list:
        profile = requests.get(url + '?__a=1')

        try:
            profile = json.loads(profile.text)
        except:
            print('Пользователь не найден или доступ закрыт')
            exit()

        pictures = profile['graphql']['user']['edge_owner_to_timeline_media']['edges']
        for picture in pictures:
            photo_list.append(int(picture['node']['id']))
        time.sleep(5)
    return photo_list

def get_like_list_on_photo(photo_id_list):
    username_list = []
    for photo_id in photo_id_list:
        api.getMediaLikers(photo_id)
        users_list = api.LastJson
        users_list = users_list['users']
        for user in users_list:
            username = user['username']
            if username not in username_list:
                username_list.append(username)
        time.sleep(5)
    return username_list

def main():
    url_list = ['https://www.instagram.com/olesgonchar/']

    photo_list = get_photo_id(url_list)
    username_list = get_like_list_on_photo(photo_list)

main()