import os
from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

# Тут будут кнопки
keyboard_main = VkKeyboard(one_time=True)
keyboard_main.add_button(label='найти пару', color=VkKeyboardColor.PRIMARY)


class Bot:
    def __init__(self) -> None:
        self.session = vk_api.VkApi(token=os.getenv('TOKEN_BOT'))
        self.longpoll = VkLongPoll(self.session)

    def func_main(self):
        """Функция-вызов остальных функций, пока еще не знаю, как его назвать"""

        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                # текст, который ввел пользователь
                request = event.text.lower() 
                # айди пользователя
                user_id = event.user_id
                if request == 'привет':
                    self.start(user_id)
                else:
                    self.send_msg(user_id, 'Тут пока я еще недодела хехе')

    def start(self, user_id):
        # Функция для кнопки начать поиск пары
        msg = f'Привет, {user_id}. Нажми на кнопку и я подберу тебе пару'
        keyboard  = keyboard_main.get_keyboard()
        responce = self.send_msg(user_id, msg, keyboard=keyboard)
        return responce

    def send_msg(self, user_id, message, keyboard=None):
        """Метод для отправки сообщений ботом, возвращает отправленное сообщение"""

        responce = self.session.method('messages.send', 
                    {'user_id': user_id, 
                        'message': message,  
                        'random_id': randrange(10 ** 7),
                        'keyboard': keyboard,
                        })
        return responce


if __name__ == '__main__':

    VKinder = Bot()
    VKinder.func_main()