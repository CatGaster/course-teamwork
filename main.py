import os

import psycopg2
import sqlalchemy
from sqlalchemy.orm import sessionmaker

from model import Users, Photos, Favorites, Blacklist, create_table



def create_delete_db(name, command, if_):
    """Функция для создании Базы данных"""

    conn_ = psycopg2.connect(database=os.getenv('LOGIN'), user=os.getenv('LOGIN'), password=os.getenv('PASSWORD'))
    conn_.autocommit = True
    with conn_.cursor() as cur:
        sql = f"""{command} DATABASE {if_} {name}"""
        print(sql)
        cur.execute(sql)
    conn_.close()    

# create_delete_db(name=os.getenv('NAME_DB'), command='DROP', if_='IF EXISTS')
# create_delete_db(name=os.getenv('NAME_DB'), command='CREATE', if_='')  

    

def create_connection_DB():
    """Функция для создания объекта-движка, для соединения с БД"""
    
    engine = sqlalchemy.create_engine(
        f"{os.getenv('DRIVER')}://"
        f"{os.getenv('LOGIN')}:{os.getenv('PASSWORD')}@"
        f"{os.getenv('HOST')}:{os.getenv('PORT')}/{os.getenv('NAME_DB')}", echo=False
    )
    return engine

Session = sessionmaker(bind=create_connection_DB())
session = Session()

create_table(create_connection_DB())
    


def add_new_user(user):
    users = Users(**user)
    session.add(users)
    session.commit()


def check_users(candidate_id):
    # проверка на то, есть ли пользователь в БД
    checking_user = session.query(Users).filter_by(owner_id=candidate_id).first()
    return checking_user is None



def add_favorite(user, candidate):
    user_id = session.query(Users).filter_by(owner_id=str(user['owner_id'])).first()
    candidate_id = session.query(Users).filter_by(owner_id=str(candidate['owner_id'])).first()
    new_favorite_user = Favorites(user_id=user_id.user_id, 
                                  favorite_user_id=candidate_id.user_id)
    session.add(new_favorite_user) 
    session.commit()



def add_black_list(user, candidate):
    user_id = session.query(Users).filter_by(owner_id=str(user['owner_id'])).first()
    candidate_id = session.query(Users).filter_by(owner_id=str(candidate['owner_id'])).first()
    new_ignored_user = Blacklist(user_id=user_id.user_id, 
                                  black_list_id=candidate_id.user_id)
    session.add(new_ignored_user) 
    session.commit()

# print(check_users('344025107'))