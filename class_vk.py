import os
from datetime import datetime
import json
import operator


import vk_api

import main

class VK:
    def __init__(self):
        self.vk_api = vk_api.VkApi(token = os.getenv('VK_TOKEN'))
        self.session = vk_api.VkTools(self.vk_api)                    
        self.vk = self.vk_api.get_api()






    def get_user_info(self, user_id):
        try:
            response = self.vk_api.method('users.get',
                                   {'user_ids': user_id,
                                       'fields': 'bdate, city, sex'})
            user_info = response[0]
            

            this_year = datetime.now()
            try:
                birthday = datetime.strptime(user_info['bdate'], '%d.%m.%Y')
                age = this_year.year - birthday.year - (
                        (this_year.month, this_year.day) < (birthday.month, birthday.day))
                
            except KeyError:
                birth_day = input('Введите дату вашего рождения: ')
                birthday = datetime.strptime(birth_day, '%d.%m.%Y')
                age = this_year.year - birthday.year - (
                        (this_year.month, this_year.day) < (birthday.month, birthday.day))            
                 
            gender = user_info['sex']
            if gender == 1:
                sex = 2
            else:
                sex = 1

            try:
                city = user_info['city']['title']
                city_id = user_info['city']['id']
            except KeyError:
                city = input('Введите ваш город: ')
                city_id = self.get_city_id(city)

            user_link = f"https://vk.com/id{user_info['id']}"

            user = {'user_id': user_info['id'],
                        'first_name': user_info['first_name'],
                        'last_name': user_info['last_name'],
                        'age': age,
                        'gender': sex,
                        'city': city_id,
                        'user_link': user_link,}
            
            return user
        except KeyError as e:
            print("Ошибка при запросе к VK API:", e)           
    
    def user_info_self(self, user_id):
            response = self.vk_api.method('users.get',
                                   {'user_ids': user_id})
            user_info_self = response[0]
            
            result = {'user_id': user_info_self['id'],
                  'first_name': user_info_self['first_name'],
                  'last_name': user_info_self['last_name'],
                  'user_link': f"https://vk.com/id{user_info_self['id']}"
                }
            
            return result
            
            
    
        #     main.add_new_user
        #     return user_info
        
 
        

    def get_city_id(self, city_name):
            try:
                city_info = self.vk.database.getCities(country_id=1,
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
        
    def get_photo(self, owner_id):     
            try:       
                attachments = []
                photos = self.vk.photos.get(  # запрашиваем данные фото из профиля
                                        owner_id=owner_id,
                                        album_id='profile',
                                        rev=1,
                                        extended=1,
                                        photo_sizes=1)

                photo_data = photo_data_preparation(photos)
                sorted_size_photo = sorting_sizes_photo(photo_data)
                attachments = []
                for photo in sorted_size_photo:
                    attachments.append({
                            'user_id': photo['user_id'],
                            'href': photo['url']
                        })
                photos_album = [attachments[i]['href'] for i in range(len(attachments))]  
                # main.add_photos(photos_album)
                return photos_album
            except vk_api.ApiError as e:
                print("Ошибка при запросе к VK API:", e)

    def search_couple(self, user_info):
        try:
            #  запрашиваем поиск:
            users = self.vk.users.search(
                count=1000,  # Максимальное количество результатов
                age_from=user_info['age'],  # минимальный возраст
                age_to=user_info['age'],  # максимальный возраст
                sex=user_info['gender'],  # пол
                city=user_info['city'],  # город
                fields='photo_max',  # Запрашиваем большие фотографии профиля
                extended=1  # разрешаем вернуть подробный результат, без этого не возвращается likes
            )

            for user in users['items']:  # итерируем для возвращения результата поиска
                if user['is_closed']:  # пропускаем если у пользователя профиль приватный
                    continue
                profile_url = f"https://vk.com/id{user['id']}"
                result = {'user_id': user['id'],
                  'first_name': user['first_name'],
                  'last_name': user['last_name'],
                  'user_link': profile_url
                }
                main.add_new_user(result)
                photo = self.get_photo(result['user_id'])
                result['photo'] = photo
                return f"Как тебе? {result['first_name']} {result['last_name']} {result['user_link']} :). А вот фотографии: {' '.join(result['photo'])}"
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
            user_id = all_key["owner_id"]
            likes = all_key["likes"]['count']
            size = all_key['sizes'][-1]['type']
            jpg_url = all_key['sizes'][-1]['url']

            data.append({
                'user_id': user_id,
                'likes': likes,  # количество лайков
                'size': size,  # размер
                'url': jpg_url  # ссылка на фото в виде attachment(https://dev.vk.com/method/messages.send)
            })
        except KeyError:
            continue

    return data


def sorting_sizes_photo(data, weight=3):
    """
    Функция сортирует и возвращает топ-3 фотографий пользователя, в максимальном размере
    """
    with open('size_photo.json', encoding='utf-8') as file:  # Файл size_photo.json шаблон размеров фотографий.
        size_info = json.load(file)                             # по которому сравниваем и находим максимальный размер.

    for data_key in data:
        for size_photo_key in size_info:
            if data_key['size'] in size_photo_key['size']:
                data_key['max_side'] = size_photo_key['max_side']

    data_sorted = sorted(data, key=lambda item: item['likes'], reverse=True)[0:weight]
    return data_sorted



# if __name__ == '__main__':
#     vk_user = VK()
#     user_info = vk_user.get_user_info('354906977')
    
#     print(vk_user.user_info_self('354906977'))
#     print(vk_user.search_couple(user_info))
#     print(vk_user.get_photo())
    