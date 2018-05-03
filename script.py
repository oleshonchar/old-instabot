from api import InstagramAPI
import time
import sqlite3
import random
import config

api = InstagramAPI(config.username, config.password)
api.login()

conn = sqlite3.connect("database.db", check_same_thread=False)
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
    done = 0
    error = 0

    for username in username_list:
        photo_list = get_photo_id(get_user_id(username))
        count = 0

        while count < 2:

            if photo_list == False or not photo_list:
                print(str(username[0]) + ' ::::: ' + 'профиль закрыт или записи отсутствуют')
                cursor.execute("UPDATE Usernames SET like = 'not liked' WHERE username = ?", (username[0],))
                error += 1
                count = 2

            else:
                random_post_id = photo_list[random.randint(0, (len(photo_list) - 1))]
                api.like(random_post_id)
                print(str(username[0]) + ' ::::: палец вверх')
                cursor.execute("UPDATE Usernames SET like = 'liked' WHERE username = ?", (username[0],))
                done += 1
                time.sleep(15)

            count += 1

    return 'Новых лайков: {}, неудачных лайков: {}'.format(done, error)

def liking_feed():
    api.timelineFeed()
    media_id_list = api.LastJson['items']
    done = 0
    print('Лайкинг ленты запущен')

    for media_id in media_id_list:

        try:
            media_id = media_id['pk']
            api.like(media_id)
            done += 1

        except KeyError:
            pass

    print('Лайкинг ленты завершен! Новых лайков: {}'.format(done))


def follow(number_of_users):
    cursor.execute("SELECT username FROM Usernames WHERE follow ISNULL LIMIT ?", (number_of_users,))
    username_list = cursor.fetchall()
    done = 0
    error = 0

    for username in username_list:
        user_id = get_user_id(username)

        if user_id:
            api.follow(get_user_id(username)[0])
            print(str(username[0]) + ' ::::: ' + 'подписался')
            cursor.execute("UPDATE Usernames SET follow = 'follow' WHERE username = ?", (username[0],))
            done += 1
            time.sleep(35)

        else:
            cursor.execute("UPDATE Usernames SET follow = 'error' WHERE username = ?", (username[0],))
            error += 1
            continue

    return("Новых подписок: {}, неудачных подписок: {}".format(done, error))


def unfollow(number_of_users):
    cursor.execute("SELECT username FROM Usernames WHERE follow == 'follow' LIMIT ?", (number_of_users,))
    username_list = cursor.fetchall()
    done = 0

    for username in username_list:
        api.unfollow(get_user_id(username)[0])
        print(str(username[0]) + ' ::::: ' + 'отписался')
        cursor.execute("UPDATE Usernames SET follow = 'unfollow' WHERE username = ?", (username[0],))
        done += 1
        time.sleep(21)

    return("Отписок: {}".format(done))

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

def check_for_emptiness_db():
    cursor.execute("SELECT COUNT(*) FROM Usernames WHERE follow ISNULL")
    amount_items = cursor.fetchone()[0]

    if amount_items > 800:
        return False

    else:
        return('Ошибка: Недостаточное количество записей в базе данных')

def unfollowing_day():
    counter = 0

    while counter < 4:
        put_like(100)
        time.sleep(7200)
        unfollow(75)
        time.sleep(7200)
        counter += 1