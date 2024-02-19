import os
from datetime import datetime
import json
import operator
from random import randrange

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
            
            result = {'vk_id': user_info_self['id'],
                  'first_name': user_info_self['first_name'],
                  'last_name': user_info_self['last_name'],
                  'user_link': f"https://vk.com/id{user_info_self['id']}"
                }            
            return result



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
                # sorted_size_photo = sorting_sizes_photo(photo_data)
                attachments = []
                for photo in photo_data:
                    attachments.append({
                            'id': photo['id'],
                            'href': photo['url']
                        })
                return attachments
            
            except vk_api.ApiError as e:
                print("Ошибка при запросе к VK API:", e)

    

    def send_photo(self, user_id):
        photos_list = self.get_photo(user_id)
        attachment = ''
        for photo in photos_list:
            attachment += f'photo{user_id}_{photo["id"]},'
        return attachment



    def search_couple(self, user_info, offset):
        
        try:
            #  запрашиваем поиск:
            users = self.vk.users.search(
                offset = offset,
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
                result = {'vk_id': user['id'],
                  'first_name': user['first_name'],
                  'last_name': user['last_name'],
                  'user_link': profile_url
                }
                # main.add_new_user(result)

                return result
        except vk_api.ApiError as e:
            print("Ошибка при запросе к VK API:", e)        



def photo_data_preparation(info, weight=3):
    """
    Функция подготавливает и возвращает полученные данные фотографий,
    пользователя, которого нашли.
    """
    data = []
    for all_key in info['items']:
        try:
            id_photo = all_key['id']
            user_id = all_key["owner_id"]
            likes = all_key["likes"]['count']
            size = all_key['sizes'][0]['type']
            jpg_url = all_key['sizes'][0]['url']

            data.append({
                'id': id_photo,
                'user_id': user_id,
                'likes': likes,  # количество лайков
                'size': size,  # размер
                'url': jpg_url  # ссылка на фото в виде attachment(https://dev.vk.com/method/messages.send)
            })
        except KeyError:
            continue
    data = sorted(data, key=lambda item: item['likes'], reverse=True)[0:weight]
    return data


# if __name__ == '__main__':
#     vk_user = VK()
#     