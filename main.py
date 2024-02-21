import os

from db import create_connection_db, create_delete_db, session
from model import create_table
from class_bot import Bot
from dotenv import load_dotenv

load_dotenv()

if __name__ == '__main__':
    create_delete_db(name=os.getenv('NAME_DB'),
                     command='DROP',
                     if_='IF EXISTS')
    create_delete_db(name=os.getenv('NAME_DB'),
                     command='CREATE',
                     if_='')

    create_table(create_connection_db())
    session.close()

    bot = Bot()
    bot.func_main()
