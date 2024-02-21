import os

import psycopg2
import sqlalchemy 
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from model import Users, Favorites, Blacklist

load_dotenv()


def create_delete_db(name: str, command: str, if_: str):
    """
    Функция для удаления/создания Базы данных
    """
    conn_ = psycopg2.connect(database=os.getenv('LOGIN'), 
                             user=os.getenv('LOGIN'), 
                             password=os.getenv('PASSWORD'))
    conn_.autocommit = True
    with conn_.cursor() as cur:
        sql = f"""{command} DATABASE {if_} {name}"""
        print(sql)
        cur.execute(sql)
    conn_.close()    


def create_connection_db():
    """
    Функция для создания объекта-движка, для соединения с БД
    """
    
    engine = sqlalchemy.create_engine(
        f"{os.getenv('DRIVER')}://"
        f"{os.getenv('LOGIN')}:{os.getenv('PASSWORD')}@"
        f"{os.getenv('HOST')}:{os.getenv('PORT')}/{os.getenv('NAME_DB')}", echo=False
    )
    return engine


"""Создание объекта-сессии"""
Session = sessionmaker(bind=create_connection_db())
session = Session()


def check_users(candidate_id: int):
    """
    Функция для проверки пользователя в БД (Users)
    """
    checking_user = session.query(Users).filter_by(owner_id=candidate_id).first()
    return checking_user is None


def add_new_user(owner_id: str, first_name: str, last_name: str, user_link: str):
    """
    Метод добавления пользователей в БД (Users)
    """
    users = Users(owner_id=owner_id, 
                  first_name=first_name, 
                  last_name=last_name, 
                  user_link=user_link)
    session.add(users)
    session.commit()


def add_favorite(user: dict, candidate: dict):
    """
    Метод для добавления пользователя в БД (Favorites)
    """
    user_id = session.query(Users).filter_by(owner_id=user['owner_id']).first()
    candidate_id = session.query(Users).filter_by(owner_id=candidate['owner_id']).first()
    new_favorite_user = Favorites(user_id=user_id.user_id, 
                                  favorite_user_id=candidate_id.user_id)
    session.add(new_favorite_user) 
    session.commit()


def add_black_list(user: dict, candidate: dict):
    """
    Метод для добавления пользователя в БД (Blacklist)
    """    
    user_id = session.query(Users).filter_by(owner_id=user['owner_id']).first()
    candidate_id = session.query(Users).filter_by(owner_id=candidate['owner_id']).first()
    new_ignored_user = Blacklist(user_id=user_id.user_id,
                                 black_list_id=candidate_id.user_id)
    session.add(new_ignored_user) 
    session.commit()


def show_fav_list(user: dict):
    """
    Метод для извлечения информации о пользователях с БД (Favorites)
    """      
    filtered = session.query(Users.first_name, Users.last_name, Users.user_link).join(
        Favorites, (Favorites.favorite_user_id == Users.user_id == user['owner_id'])).all()
    result = []
    for item in filtered:
        result.append(item)
    return result
