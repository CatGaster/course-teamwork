import os

import psycopg2
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from model import Users, Photos, Favorites, create_table

load_dotenv()


def create_delete_db(name, command, if_):
    """Функция для создания Базы данных"""

    conn_ = psycopg2.connect(database=os.getenv('LOGIN'), user=os.getenv('LOGIN'), password=os.getenv('PASSWORD'))
    conn_.autocommit = True
    with conn_.cursor() as cur:
        sql = f"""{command} DATABASE {if_} {name}"""
        print(sql)
        cur.execute(sql)
    conn_.close()    


create_delete_db(name=os.getenv('NAME_DB'), command='DROP', if_='IF EXISTS')
create_delete_db(name=os.getenv('NAME_DB'), command='CREATE', if_='')
    

def create_connection_db():
    """Функция для создания объекта-движка, для соединения с БД"""
    
    engine = sqlalchemy.create_engine(
        f"{os.getenv('DRIVER')}://"
        f"{os.getenv('LOGIN')}:{os.getenv('PASSWORD')}@"
        f"{os.getenv('HOST')}:{os.getenv('PORT')}/{os.getenv('NAME_DB')}", echo=False
    )
    return engine


Session = sessionmaker(bind=create_connection_db())
session = Session()

create_table(create_connection_db())
    

def add_new_user(user):
    # нужна проверка, если пользователь уже есть в базе
    user = Users(**user)
    session.add(user)
    session.commit()


# def add_photos(photo_album):
#     # for photo in photo_album:
#     user_photos = Photos(photo_album)
#     session.add(user_photos)
