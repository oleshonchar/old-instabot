from api import InstagramAPI
import time
import sqlite3
import random
import config


conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()
api = None


def get_login(user_id):
    cursor.execute("SELECT login, password FROM Instagram WHERE userid = ?", (user_id,))
    data = cursor.fetchone()

    if len(data) == 0:
        print('Такой пользователь не зарегистрирован!')
    else:
        login = data[0]
        password = data[1]
        return {'login': login, 'password': password}


def auth(user_id):
    msg = get_login(user_id)
    global login, password, api
    login = msg['login']
    password = msg['password']
    api = InstagramAPI(login, password)
    api.login()


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


def save_usernames(username_list, user_id):
    try:
        cursor.execute("CREATE TABLE Usernames (userid, username, like, follow)")
        cursor.execute("CREATE TABLE Instagram (userid, login, password)")

    except:
        print('Ошибка: Таблица существует')

    for username in username_list:
        cursor.execute("SELECT username FROM Usernames WHERE username = ? AND userid = ?", (username, user_id))
        data = cursor.fetchall()

        if len(data) == 0:
            cursor.execute("INSERT INTO Usernames (username, userid) VALUES (?, ?)", (username, user_id))

        else:
            print('Ошибка: Имя существует')

    conn.commit()


def put_like(number_of_users, user_id):
    cursor.execute("SELECT username FROM Usernames WHERE like ISNULL AND userid = ? LIMIT ?", (user_id, number_of_users))
    username_list = cursor.fetchall()
    done = 0
    error = 0

    for username in username_list:
        photo_list = get_photo_id(get_user_id(username))
        count = 0

        while count < 2:

            if photo_list == False or not photo_list:
                print(str(username[0]) + ' ::::: ' + 'профиль закрыт или записи отсутствуют')
                cursor.execute("UPDATE Usernames SET like = 'not liked' WHERE username = ? AND userid = ?", (username[0], user_id))
                error += 1
                count = 2

            else:
                random_post_id = photo_list[random.randint(0, (len(photo_list) - 1))]
                api.like(random_post_id)
                print(str(username[0]) + ' ::::: палец вверх')
                cursor.execute("UPDATE Usernames SET like = 'liked' WHERE username = ? AND userid = ?", (username[0], user_id))
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


def follow(number_of_users, user_id):
    cursor.execute("SELECT username FROM Usernames WHERE follow ISNULL AND userid = ? LIMIT ?", (user_id, number_of_users,))
    username_list = cursor.fetchall()
    done = 0
    error = 0

    for username in username_list:
        userid = get_user_id(username)

        if userid:
            api.follow(get_user_id(username)[0])
            print(str(username[0]) + ' ::::: ' + 'подписался')
            cursor.execute("UPDATE Usernames SET follow = 'follow' WHERE username = ? AND userid = ?", (username[0], user_id,))
            done += 1
            time.sleep(35)

        else:
            cursor.execute("UPDATE Usernames SET follow = 'error' WHERE username = ? AND userid = ?", (username[0], user_id,))
            error += 1
            continue

    return("Новых подписок: {}, неудачных подписок: {}".format(done, error))


def unfollow(number_of_users, user_id):
    cursor.execute("SELECT username FROM Usernames WHERE follow == 'follow' AND userid = ? LIMIT ?", (user_id, number_of_users,))
    username_list = cursor.fetchall()
    done = 0
    error = 0

    for username in username_list:
        userid = get_user_id(username)

        if userid:
            api.unfollow(get_user_id(username)[0])
            print(str(username[0]) + ' ::::: ' + 'отписался')
            cursor.execute("UPDATE Usernames SET follow = 'unfollow' WHERE username = ? AND userid = ?", (username[0], user_id))
            done += 1
            time.sleep(21)

        else:
            cursor.execute("UPDATE Usernames SET follow = 'error' WHERE username = ? AND userid = ?", (username[0], user_id,))
            error += 1
            continue

    return("Отписок: {}".format(done))


def parse_users(username_list, user_id):
    print('Начинаем парсить!')
    user_id_list = get_user_id(username_list)
    photo_list = get_photo_id(user_id_list)
    like_list = get_like_list_on_photo(photo_list)
    save_usernames(like_list, user_id)


def check_for_emptiness_db(user_id):
    cursor.execute("SELECT COUNT(*) FROM Usernames WHERE follow ISNULL AND userid = (?)", (user_id,))
    amount_items = cursor.fetchone()[0]

    if amount_items > 800:
        return False

    else:
        return('Ошибка: Недостаточное количество записей в базе данных')


def check_registration(user_id):
    try:
        cursor.execute("SELECT userid FROM Instagram WHERE userid = ?", (user_id,))

    except:
        cursor.execute("CREATE TABLE Instagram (userid, login, password)")

    data = cursor.fetchall()

    if len(data) == 0:
        return {'key': False, 'text': 'вы не зарегистрированы!'}
    else:
        return {'key': True, 'text': 'вы зарегистрированы!'}


def registration_user(user_id):
    cursor.execute("INSERT INTO Instagram (userid) VALUES (?)", (user_id,))
    conn.commit()
    return 'Вы успешно зарегистрированы!'


def check_instagram_data(user_id):
    cursor.execute("SELECT login FROM Instagram WHERE userid = ?", (user_id,))
    data_login = cursor.fetchall()
    cursor.execute("SELECT password FROM Instagram WHERE userid = ?", (user_id,))
    data_password = cursor.fetchall()

    if len(data_login) == 0 and len(data_password) == 0:
        return {'key': False, 'text': 'вы не зарегистрированы'}
    else:
        return {'key': True, 'text': 'вы зарегистрированы'}


def registration_instagram_data(user_id, key, value):

    if key == 'login':
        cursor.execute("UPDATE Instagram SET login = (?) WHERE userid = (?)", (value, user_id))
    else:
        cursor.execute("UPDATE Instagram SET password = (?) WHERE userid = (?)", (value, user_id))

    conn.commit()
    return ('Ваш {} добавлен!'.format(key))


def get_and_save_following_list(user_id):
    cursor.execute("SELECT login FROM Instagram WHERE userid = ?", (user_id,))
    selfid = cursor.fetchall()[0]
    selfid = get_user_id(selfid)
    followers = api.getTotalFollowings(selfid[0])

    try:
        cursor.execute("CREATE TABLE Whitelist (userid, username)")
    except:
        print('Ошибка: Таблица существует')

    for i in followers:
        cursor.execute("INSERT INTO Whitelist (userid, username) VALUES (?, ?)", (user_id, i['username']))
