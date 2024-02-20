import os
from datetime import datetime

import vk_api



class VK:
    def __init__(self):
        self.vk_api = vk_api.VkApi(token = os.getenv('VK_TOKEN'))
        self.session = vk_api.VkTools(self.vk_api)         
        self.vk = self.vk_api.get_api()
        

    def get_user_info(self, user_id: int) -> dict:
        """
        Метод для получения информации о пользователях
        """
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

            user = {'owner_id': user_info['id'],
                        'first_name': user_info['first_name'],
                        'last_name': user_info['last_name'],
                        'age': age,
                        'gender': sex,
                        'city': city_id,
                        'user_link': user_link,}
            
            return user
        except KeyError as e:
            print("Ошибка при запросе к VK API:", e)           
    


    def get_city_id(self, city_name: str):
        """
        Метод для определения id города
        """
        try:
            city_info = self.vk.database.getCities(country_id=1,
                                                q=city_name,
                                                need_all=0,
                                                count=1)  
            if city_info['count'] > 0:
                city_id = city_info['items'][0]['id']
                return city_id
            else:
                print("Город не найден")
                return None
        except vk_api.ApiError as e:
                print("Ошибка при запросе к VK API:", e)
                return None       



    def get_photo(self, owner_id: int) -> str:  
        """
        Метод для получения фотографий пользователей
        """   
        try:         
            photos = self.vk.photos.get(  
                                        owner_id=owner_id,
                                        album_id='profile',
                                        rev=1,
                                        extended=1,
                                        photo_sizes=1)

            photo_data = photo_data_preparation(photos)
            photos_list = []
            for photo in photo_data:
                photos_list.append({
                            'id': photo['id'],
                        })
            attachment = ''
            for photo in photos_list:
                attachment += f'photo{owner_id}_{photo["id"]},'
            return attachment            
        except vk_api.ApiError as e:
            print("Ошибка при запросе к VK API:", e)



    def search_couple(self, user_info: dict, offset: int) -> dict:
        """
        Метод для поиска кандидатов для знакомства
        """
        try:

            users = self.vk.users.search(
                offset = offset,
                count=1000,  
                age_from=user_info['age'], 
                age_to=user_info['age'],  
                sex=user_info['gender'],  
                city=user_info['city'],  
                fields='photo_max',  
                extended=1  
            )
            for user in users['items']:  
                if user['is_closed']:  
                    continue
                profile_url = f"https://vk.com/id{user['id']}"
                result = {'owner_id': user['id'],
                  'first_name': user['first_name'],
                  'last_name': user['last_name'],
                  'user_link': profile_url
                }
                
                return result
            
        except vk_api.ApiError as e:
            print("Ошибка при запросе к VK API:", e)        



def photo_data_preparation(info, weight=3) -> dict:
    """
    Функция подготавливает и возвращает полученные данные фотографий,
    пользователя, которого нашли.
    """
    data = []
    for all_key in info['items']:
        try:
            id_photo = all_key['id']
            likes = all_key["likes"]['count']
            data.append({
                'id': id_photo,
                'likes': likes, 
            })
        except KeyError:
            continue
    data = sorted(data, key=lambda item: item['likes'], reverse=True)[0:weight]
    return data
