import os

import sqlalchemy
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

from model import Users, Photos, Favorites, create_table

load_dotenv()


def create_connection_db():
    """Функция для создания объекта-движка, для соединения с БД"""
    
    engine = sqlalchemy.create_engine(
        f"{os.getenv('DRIVER')}://"
        f"{os.getenv('LOGIN')}:{os.getenv('PASSWORD')}@"
        f"{os.getenv('HOST')}:{os.getenv('PORT')}/{os.getenv('NAME_DB')}", echo=True
    )
    return engine


Session = sessionmaker(bind=create_connection_db())
session = Session()


if __name__ == '__main__':
    create_table(create_connection_db())

    

    
    
