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


class Bot:

    def __init__(self) -> None:
        self.session = vk_api.VkApi(token=os.getenv('TOKEN_BOT'))
        self.longpoll = VkLongPoll(self.session)
        self.vk_api = VK()
        self.user = None
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
                # код пока не работает, недоделан
                # elif request == 'добавить в избранное':
                #     self.add_favorite(user_id)                                   
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
        msg = f'Привет, {name}! Нажми на кнопку и я подберу тебе пару'
        keyboard  = keyboard_main.get_keyboard()
        responce = self.send_msg(user_id, msg, keyboard=keyboard)
        return responce
    

    def send_user_info(self, user_id):  
        while True:      
            candidate_info = self.vk_api.search_couple(self.vk_api.get_user_info(user_id), self.offset)
            if main.check_users(str(candidate_info['vk_id'])) is False:
                main.add_new_user(candidate_info)
                msg = f"Как тебе? {candidate_info['first_name']} {candidate_info['last_name']}. Вот ссылка на профиль - {candidate_info['user_link']}. А вот фотографии: "
                attachment = self.vk_api.send_photo(candidate_info['vk_id'])                  
                response = self.send_msg(user_id, msg, attachment=attachment)   
            else:
                self.offset +=1
                continue           
            return response
        

        
# код пока не работает, недоделан
    # def add_favorite(self, user_id):
    #     
    #     main.add_favorite(self.vk_api.user_info_self(user_id)['vk_id'], main.last_users())
    #     response = self.send_msg(user_id, 'Добавлено в избранное')
    #     return response




if __name__ == '__main__':

    bot = Bot()
    bot.func_main()

