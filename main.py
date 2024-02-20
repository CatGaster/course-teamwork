import os

import psycopg2
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from model import Users, Photos, Favorites, Blacklist, create_table

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


def search_show(id_):
    sales = session.query(Users.user_id).filter(Users.owner_id == id_).all()
    source_id = sales[0][0]
    with psycopg2.connect(database=os.getenv('NAME_DB'),
                          user=os.getenv('LOGIN'),
                          password=os.getenv('PASSWORD')) as conn_:
        with conn_.cursor() as cur:
            cur.execute("""
                        SELECT favorite_user_id FROM favorite
                        WHERE user_id = %s;
                        """, (source_id,))

            favorite_list = cur.fetchall()

    result = 'Cписок избранных людей:\n'
    count = 0
    for favorite_user in favorite_list:
        user = (session.query(Users.owner_id,
                              Users.first_name,
                              Users.last_name,
                              Users.user_link)
                .filter(Users.user_id == favorite_user[0])
                .all())
        count += 1
        result += f'{count}. {user[0][1]} {user[0][2]}, ссылка на профиль: {user[0][3]}\n'

    return result

# print(check_users('344025107'))


# search_show("9663572")
