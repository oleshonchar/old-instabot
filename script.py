from api import InstagramAPI
import requests
import json
import time
import sqlite3
import random

api = InstagramAPI(username='iv01020', password='qwerty123456')
api.login()

def get_photo_id(url_list):
    photo_list = []
    for url in url_list:
        profile = requests.get(url + '?__a=1')

        try:
            profile = json.loads(profile.text)
        except:
            print('Ошибка: Пользователь не найден или доступ закрыт')
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

def save_usernames(username_list):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    try:
        cursor.execute("CREATE TABLE Usernames (username)")
    except:
        print('Ошибка: Таблица существует')

    for username in username_list:
        cursor.execute("SELECT username FROM Usernames WHERE username = ?", (username,))
        data = cursor.fetchall()
        if len(data) == 0:
            cursor.execute("INSERT INTO Usernames (username) VALUES (?)", (username,))
        else:
            print('Ошибка: Имя существует')

    conn.commit()
    conn.close()

def put_like(number_of_users):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    # try:
    #     # cursor.execute("CREATE TABLE Usernames_marked (username)")
    #     # cursor.execute("CREATE TABLE Usernames_without_a_marked (username)")
    # except:
    #     print('Ошибка: Таблица существует')

    cursor.execute("SELECT * FROM Usernames WHERE ROWID < ?", (number_of_users,))
    username_list = cursor.fetchall()

    for username in username_list:
        profile = ['https://www.instagram.com/' + username[0] + '/']
        photo_list = get_photo_id(profile)
        count = 0
        while count < 2:
            try:
                random_post_id = photo_list[random.randint(0, (len(photo_list) - 1))]
                print(str(username[0]) + ' ::::: палец вверх')
                api.like(random_post_id)
                cursor.execute("INSERT INTO Usernames_marked (username) VALUES (?)", (username[0],))
                time.sleep(5)
            except:
                print(str(username[0]) + ' ::::: ' + 'профиль закрыт или записи отсутствуют')
                cursor.execute("INSERT INTO Usernames_without_a_marked (username) VALUES (?)", (username[0],))
                count = 2
            cursor.execute("DELETE FROM Usernames WHERE username = ?", (username[0],))
            count += 1
        time.sleep(10)

    conn.commit()
    conn.close()

def main():
    url_list = ['https://www.instagram.com/yurchiikk/']

    # photo_list = get_photo_id(url_list)
    # username_list = get_like_list_on_photo(photo_list)
    # save_usernames(username_list)
    put_like(5)


main()