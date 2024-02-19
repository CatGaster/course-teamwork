import os
from pprint import pprint
from datetime import datetime

import requests
from dotenv import load_dotenv
import vk_api

load_dotenv()


class VK:
    def __init__(self, vk_token, vk_id, version='5.199'):
        self.vk_access_token = vk_token
        self.vk_id = vk_id
        self.version = version
        self.params = {
            'access_token': vk_token,
            'v': self.version
        }

    def get_user_profile(self):
        """
        Метод, который получает данные целевого пользователя (город, пол, возраст).
        """
        host_url = 'api.vk.com'
        params_user_id = {
            'user_id': self.vk_id,
            'fields': 'city, sex, bdate'
        }
        url_users = f'https://{host_url}/method/users.get'

        # получаем данные пользователя:
        try:
            response_user_ids = requests.get(url_users, params={**self.params, **params_user_id})
            info_user_ids = response_user_ids.json()
            user = info_user_ids['response'][0]
            first_name = user['first_name']
            last_name = user['last_name']
        except KeyError as e:
            print("Ошибка при запросе к VK API:", e)
            return None

        # если у пользователя не указан в профиле его город, то спрашиваем у него
        # и получаем id этого города:
        try:
            city = user['city']['title']
            city_id = user['city']['id']
        except KeyError:
            city = input('Введите ваш город: ')
            city_id = self.get_city_id(city)

        # если у пользователя не указана в профиле его дата рождения, то спрашиваем у него
        # и рассчитываем его возраст:
        this_year = datetime.now()
        try:
            birthday = datetime.strptime(user['bdate'], '%d.%m.%Y')
            age = this_year.year - birthday.year - (
                    (this_year.month, this_year.day) < (birthday.month, birthday.day))
        except KeyError:
            birth_day = input('Введите дату вашего рождения: ')
            birthday = datetime.strptime(birth_day, '%d.%m.%Y')
            age = this_year.year - birthday.year - (
                    (this_year.month, this_year.day) < (birthday.month, birthday.day))

        print('Входящий пользователь: ')
        print(first_name, last_name)
        print(f"город: {city} city_id: {city_id}")
        gender = user['sex']

        # Определяем пол пользователя. В программе будем использовать поиск
        # людей противоположного пола.
        if gender == 1:
            sex = 2
            print('пол: женский')
        else:
            sex = 1
            print('пол: мужской')

        print('возраст:', age)
        age_from = age
        age_to = age
        print('**************************')

        self.search_users(age_from, age_to, sex, city_id)

    def get_city_id(self, city_name):
        """
        Метод ищет и возвращает id города.
        В параметре city_name название города.
        """
        vk_session = vk_api.VkApi(token=self.vk_access_token)
        vk = vk_session.get_api()

        try:
            city_info = vk.database.getCities(country_id=1,
                                              q=city_name,
                                              need_all=0,
                                              count=1)  # country_id=1 соответствует России
            if city_info['count'] > 0:
                city_id = city_info['items'][0]['id']
                return city_id
            else:
                print("Город не найден")
                return None
        except vk_api.ApiError as e:
            print("Ошибка при запросе к VK API:", e)
            return None

    def search_users(self, age_from, age_to, sex, city_id, weight=3):
        """
        Метод осуществляет поиск пользователей для знакомств, по входящим параметрам.
        """

        vk_session = vk_api.VkApi(token=self.vk_access_token)
        vk = vk_session.get_api()

        try:
            #  запрашиваем поиск:
            users = vk.users.search(
                count=1000,  # Максимальное количество результатов
                age_from=age_from,  # минимальный возраст
                age_to=age_to,  # максимальный возраст
                sex=sex,  # пол
                city=city_id,  # город
                fields='photo_max',  # Запрашиваем большие фотографии профиля
                extended=1  # разрешаем вернуть подробный результат, без этого не возвращается likes
            )

            for user in users['items']:  # итерируем для возвращения результата поиска
                if user['is_closed']:  # пропускаем если у пользователя профиль приватный
                    continue
                profile_url = f"https://vk.com/id{user['id']}"
                attachments = []
                photos = vk.photos.get(owner_id=user['id'],  # запрашиваем данные фото из профиля
                                       album_id='profile',
                                       rev=1,
                                       extended=1,
                                       photo_sizes=0)

                photo_data = photo_data_preparation(photos)
                sorted_size_photo = sorted(photo_data, key=lambda item: item['likes'], reverse=True)[0:weight]

                for photo in sorted_size_photo:
                    attachments.append({
                        'photo_name': photo['photo_name'],
                        'href': photo['url']
                    })

                # выводим результат поиска в консоль
                print('результат поиска:')
                print('**************************')
                print('id пользователя:', user['id'])
                print("Имя:", user['first_name'])
                print("Фамилия:", user['last_name'])
                print("Ссылка на профиль:", profile_url)
                pprint(attachments)
                print('**************************')

                # Запрос поиска следующего пользователя. Enter-разрешить, N-остановить программу
                next_page = input('Продолжить поиск людей? Enter/N: ').upper()
                if next_page == 'N':
                    print('*****До встречи!******')
                    break

        except vk_api.ApiError as e:
            print("Ошибка при запросе к VK API:", e)


def photo_data_preparation(info):
    """
    Функция подготавливает и возвращает полученные данные фотографий,
    пользователя, которого нашли.
    """
    data = []
    for all_key in info['items']:
        try:
            photo_name = f'{all_key["post_id"]}_{all_key["owner_id"]}.jpg',
            likes = all_key["likes"]['count']
            size = all_key['sizes'][-1]['type']
            jpg_url = all_key['sizes'][-1]['url']
            print(photo_name[0])
            data.append({
                'photo_name': photo_name[0],
                'likes': likes,  # количество лайков
                'size': size,  # размер
                'url': jpg_url  # ссылка на фото в виде attachment(https://dev.vk.com/method/messages.send)
            })
        except KeyError:
            continue

    return data


if __name__ == '__main__':
    token = os.getenv('VK_TOKEN')  # здесь нужно использовать ваш токен доступа к приложению VK
    user_owner_id = '1'  # Идентификатор входящего пользователя
    get_photo = VK(token, user_owner_id)
    get_photo.get_user_profile()
