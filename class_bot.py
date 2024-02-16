import os
from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from class_vk import VK
import main

keyboard_main = VkKeyboard(one_time=True)
keyboard_main.add_button(label='найти пару', color=VkKeyboardColor.PRIMARY)

class Bot:

    def __init__(self) -> None:
        self.session = vk_api.VkApi(token=os.getenv('TOKEN_BOT'))
        self.longpoll = VkLongPoll(self.session)
        self.vk_api = VK()
        

    def send_msg(self, user_id, message, keyboard=None):
        """Метод для отправки сообщений ботом, возвращает отправленное сообщение"""

        responce = self.session.method('messages.send', 
                    {'user_id': user_id, 
                        'message': message,  
                        'random_id': randrange(10 ** 7),
                        'keyboard': keyboard,
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
                    # city = self.send_msg(user_id, 'Введите ваш город: ')  
                    self.send_msg(user_id, self.vk_api.search_couple(self.vk_api.get_user_info(user_id)))
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
        # Функция для кнопки начать поиск пары
        msg = f'Привет, {name}! Нажми на кнопку и я подберу тебе пару'
        keyboard  = keyboard_main.get_keyboard()
        responce = self.send_msg(user_id, msg, keyboard=keyboard)
        return responce
    



if __name__ == '__main__':

    bot = Bot()
    bot.func_main()
