import os
from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from class_vk import VK
import main

keyboard_main = VkKeyboard(one_time=False)
keyboard_main.add_button(label='найти пару', color=VkKeyboardColor.PRIMARY)
keyboard_main.add_button(label='добавить в избранное', color=VkKeyboardColor.POSITIVE)
keyboard_main.add_button(label='добавить в черный список', color=VkKeyboardColor.NEGATIVE)


class Bot:

    def __init__(self) -> None:
        self.session = vk_api.VkApi(token=os.getenv('TOKEN_BOT'))
        self.longpoll = VkLongPoll(self.session)
        self.vk_api = VK()
        # self.candidate для запоминания последнего кандидата, чтобы добавить его избранное/черный список
        self.candidate = None
        self.offset = -1
        
        

    def send_msg(self, user_id, message=None, keyboard=None, attachment=None):
        """Метод для отправки сообщений ботом, возвращает отправленное сообщение"""

        responce = self.session.method('messages.send', 
                    {'user_id': user_id, 
                        'message': message,  
                        'random_id': randrange(10 ** 7),
                        'keyboard': keyboard,
                        'attachment': attachment,                       
                        })
        return responce 
    

    def func_main(self):
        """Функция-вызов остальных функций, пока еще не знаю, как его назвать"""

        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                request = event.text.lower() 
                user_id = event.user_id
                if request == 'привет':  
                    main.add_new_user(self.vk_api.user_info_self(user_id))                  
                    self.send_first_msg(user_id)                 
                elif request == 'найти пару':
                    self.offset += 1
                    self.send_user_info(user_id)  
                elif request == 'добавить в избранное':
                    self.add_favorite(user_id)    
                elif request == 'добавить в черный список':
                    self.add_black_list(user_id)                                 
                else:
                    self.send_msg(user_id, 'Ошибка!')
        
    def get_name(self, user_id):
        vk = vk_api.VkApi(token = os.getenv('VK_TOKEN'))
        try:
            response = vk.method('users.get',
                                   {'user_ids': user_id})
            user_info = response[0]
            name = user_info['first_name']
            return name
        except KeyError as e:
            print("Ошибка при запросе к VK API:", e)    


    def send_first_msg(self, user_id):
        name = self.get_name(user_id)
        msg = f"""Привет, {name}! Нажми на кнопку "найти пару" и я подберу тебе кандидатов. 
        Если тебе понравился человек - добавь его в избранный список, 
        но если полагаешь, что звезды не сойдутся - добавь в черный список. 
        Если захочешь посмотреть на понравившихся пользователь - нажми "Показать избранное". Удачи! """
        keyboard  = keyboard_main.get_keyboard()
        responce = self.send_msg(user_id, msg, keyboard=keyboard)
        return responce
    

    def send_user_info(self, user_id):  
        self.user = self.vk_api.get_user_info(user_id)
        while True: 
            self.candidate = self.vk_api.search_couple(self.vk_api.get_user_info(user_id), self.offset)                        
            if main.check_users(str(self.candidate['owner_id'])):
                self.candidate = self.vk_api.search_couple(self.user, self.offset)
                main.add_new_user(self.candidate)
                msg = f"Как тебе? {self.candidate['first_name']} {self.candidate['last_name']}. Вот ссылка на профиль - {self.candidate['user_link']}. А вот фотографии: "
                attachment = self.vk_api.send_photo(self.candidate['owner_id'])                  
                response = self.send_msg(user_id, msg, attachment=attachment)   
            else:
                self.offset += 1
                continue           
            return response
                

    def add_favorite(self, user_id):
        main.add_favorite(self.vk_api.user_info_self(user_id), self.candidate)
        response = self.send_msg(user_id, f"{self.candidate['first_name']} {self.candidate['last_name']} теперь в избранном!")
        return response

    def add_black_list(self, user_id):
        main.add_black_list(self.vk_api.user_info_self(user_id), self.candidate)
        response = self.send_msg(user_id, f"{self.candidate['first_name']} {self.candidate['last_name']} теперь в черном списке!")
        return response


if __name__ == '__main__':

    bot = Bot()
    bot.func_main()

