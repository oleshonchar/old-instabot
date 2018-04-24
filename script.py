from api import InstagramAPI
import requests
import json
import time
import sqlite3
import random
import config

api = InstagramAPI(config.username, config.password)
api.login()

def get_user_id(username_list):
    user_id_list = []

    for username in username_list:
        api.searchUsername(username)
        user_id_list.append(int(api.LastJson['user']['pk']))
    return user_id_list

def get_photo_id(user_id_list):
    photo_list = []

    for user_id in user_id_list:
        user_feed = api.getUserFeed(user_id)

        if user_feed == False:
            print('Ошибка: Пользователь не найден или доступ закрыт')
            return False

        pictures = api.LastJson['items']

        for picture in pictures:
            photo_list.append(int(picture['pk']))
        time.sleep(5)

    return photo_list

def get_like_list_on_photo(photo_id_list):
    username_list = []

    for photo_id in photo_id_list:
        api.getMediaLikers(photo_id)
        users_list = api.LastJson['users']

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

    cursor.execute("SELECT username FROM Usernames LIMIT ?", (number_of_users,))
    username_list = cursor.fetchall()

    for username in username_list:
        photo_list = get_photo_id(get_user_id(username))
        count = 0

        while count < 2:

            if photo_list == False:
                print(str(username[0]) + ' ::::: ' + 'профиль закрыт или записи отсутствуют')
                cursor.execute("UPDATE Usernames SET like = 'not liked' WHERE username = ?", (username[0],))
                count = 2
            else:
                random_post_id = photo_list[random.randint(0, (len(photo_list) - 1))]
                api.like(random_post_id)
                print(str(username[0]) + ' ::::: палец вверх')
                cursor.execute("UPDATE Usernames SET like = 'liked' WHERE username = ?", (username[0],))
                time.sleep(5)

            count += 1
        time.sleep(10)

    conn.commit()
    conn.close()


def main():

    username_list = ['czekhov', 'a.ku4erenk0', 'shut_up_motherfucker']

    # user_id_list = get_user_id(username_list)
    # photo_list = get_photo_id(user_id_list)
    # like_list = get_like_list_on_photo(photo_list)
    # save_usernames(username_list)
    # put_like(15)


main()