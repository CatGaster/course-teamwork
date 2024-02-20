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
        self.vk_api_app = vk_api.VkApi(token=os.getenv('VK_TOKEN'))
        self.vk = self.vk_api_app.get_api()

    def send_msg(self, user_id, message, keyboard=None):
        """Метод для отправки сообщений ботом, возвращает отправленное сообщение"""

        response = self.session.method('messages.send',
                                       {'user_id': user_id,
                                        'message': message,
                                        'random_id': randrange(10 ** 7),
                                        'keyboard': keyboard,
                                        })
        return response

    def func_main(self):
        """Функция-вызов остальных функций, пока еще не знаю, как его назвать"""

        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                request = event.text.lower()
                user_id = event.user_id
                print(user_id)
                if request == 'привет':
                    main.add_new_user(self.vk_api.user_info_self(user_id))
                    self.send_first_msg(user_id)
                elif request == 'найти пару':
                    # city = self.send_msg(user_id, 'Введите ваш город: ')

                    # self.send_msg(user_id, self.vk_api.search_couple(self.vk_api.get_user_info(user_id)))
                    self.search_couple(self.vk_api.get_user_info(user_id), user_id)
                    # self.send_msg(user_id, self.vk_api.search_couple(self.vk_api.get_user_info(user_id)))
                else:
                    self.send_msg(user_id, 'Ошибка!')

    def get_name(self, user_id):
        vk = vk_api.VkApi(token=os.getenv('VK_TOKEN'))
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
        keyboard = keyboard_main.get_keyboard()
        response = self.send_msg(user_id, msg, keyboard=keyboard)
        return response

    def search_couple(self, user_info, user_id):
        print(user_info)
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
                          'user_link': profile_url}

                main.add_new_user(result)  # start
                photo = self.vk_api.get_photo(result['user_id'])
                result['photo'] = photo
                # result_bot = Bot()
                result_message = (f"Как тебе? {result['first_name']} {result['last_name']} {result['user_link']} "
                                  f":). А вот фотографии: {' '.join(result['photo'])}")
                self.send_msg(user_id, result_message)

                # return (f"Как тебе? {result['first_name']} {result['last_name']} {result['user_link']} "
                #         f":). А вот фотографии: {' '.join(result['photo'])}")
        except vk_api.ApiError as e:
            print("Ошибка при запросе к VK API:", e)


if __name__ == '__main__':
    bot = Bot()
    bot.func_main()
