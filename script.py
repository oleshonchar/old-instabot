from api import InstagramAPI
import json
import time
import sqlite3
import random
import config

api = InstagramAPI(config.username, config.password)
api.login()

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

def get_user_id(username_list):
    user_id_list = []

    for username in username_list:

        api.searchUsername(username)

        try:
            user_id_list.append(int(api.LastJson['user']['pk']))

        except KeyError:
            print('Ошибка: Эта страница недоступна')
            return False

    return user_id_list

def get_photo_id(user_id_list):
    photo_list = []
    if user_id_list:

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

    else:
        print('Ошибка: Эта страница недоступна')
        return False


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
    try:
        cursor.execute("CREATE TABLE Usernames (username, like, follow)")

    except:
        print('Ошибка: Таблица существует')

    for username in username_list:
        cursor.execute("SELECT username FROM Usernames WHERE username = ?", (username,))
        data = cursor.fetchall()

        if len(data) == 0:
            cursor.execute("INSERT INTO Usernames (username) VALUES (?)", (username,))

        else:
            print('Ошибка: Имя существует')


def put_like(number_of_users):
    cursor.execute("SELECT username FROM Usernames WHERE like ISNULL LIMIT ?", (number_of_users,))
    username_list = cursor.fetchall()

    for username in username_list:
        photo_list = get_photo_id(get_user_id(username))
        count = 0

        while count < 2:

            if photo_list == False or not photo_list:
                print(str(username[0]) + ' ::::: ' + 'профиль закрыт или записи отсутствуют')
                cursor.execute("UPDATE Usernames SET like = 'not liked' WHERE username = ?", (username[0],))
                count = 2

            else:
                random_post_id = photo_list[random.randint(0, (len(photo_list) - 1))]
                api.like(random_post_id)
                print(str(username[0]) + ' ::::: палец вверх')
                cursor.execute("UPDATE Usernames SET like = 'liked' WHERE username = ?", (username[0],))
                time.sleep(15)

            count += 1

def follow(number_of_users):
    cursor.execute("SELECT username FROM Usernames WHERE follow ISNULL LIMIT ?", (number_of_users,))
    username_list = cursor.fetchall()

    for username in username_list:
        user_id = get_user_id(username)

        if user_id:
            api.follow(get_user_id(username)[0])
            print(str(username[0]) + ' ::::: ' + 'подписался')
            cursor.execute("UPDATE Usernames SET follow = 'follow' WHERE username = ?", (username[0],))
            time.sleep(35)

        else:
            cursor.execute("UPDATE Usernames SET follow = 'error' WHERE username = ?", (username[0],))
            continue


def unfollow(number_of_users):
    cursor.execute("SELECT username FROM Usernames WHERE follow == 'follow' LIMIT ?", (number_of_users,))
    username_list = cursor.fetchall()

    for username in username_list:
        api.unfollow(get_user_id(username)[0])
        print(str(username[0]) + ' ::::: ' + 'отписался')
        cursor.execute("UPDATE Usernames SET follow = 'unfollow' WHERE username = ?", (username[0],))
        time.sleep(21)

def parse_users(username_list):
    user_id_list = get_user_id(username_list)
    photo_list = get_photo_id(user_id_list)
    like_list = get_like_list_on_photo(photo_list)
    save_usernames(like_list)

def liking():
    counter = 0

    while counter < 4:
        put_like(200)
        time.sleep(7200)
        counter += 1

def following_day():
    counter = 0

    cursor.execute("SELECT COUNT(*) FROM Usernames WHERE follow ISNULL")
    amount_items = cursor.fetchone()[0]

    if amount_items > 800:

        while counter < 4:
            put_like(1)
            time.sleep(7200)
            follow(100)
            time.sleep(7200)
            counter += 1

    else:
        print('Ошибка: Недостаточное количество записей в базе данных')

def unfollowing_day():
    counter = 0

    while counter < 4:
        put_like(200)
        time.sleep(7200)
        unfollow(150)
        time.sleep(7200)
        counter += 1

def main():

    username_list = []
    # parse_users(username_list)
    # following_day()


main()

conn.commit()
conn.close()