import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

"""Объект для хранения информации о всех отношениях и данных в них в БД"""
Base = declarative_base()


class Users(Base):
    """
    Класс для создания отношения user - содержащую информацию о пользователях:
    user_id - уникальное id пользователя в базе данных
    first_name - имя пользователя 
    last_name - фамилия пользователя
    gender - пол пользователя
    age - возраст пользователя
    link - ссылка на пользователя Вконтакте
    city - город пользователя
    """

    __tablename__ = 'users'

    user_id = sq.Column(sq.Integer, primary_key=True)
    first_name = sq.Column(sq.String(length=40), nullable=False)
    last_name = sq.Column(sq.String(length=40), nullable=False)
    gender = sq.Column(sq.String(length=40), nullable=False)
    age = sq.Column(sq.Integer, nullable=False)
    link = sq.Column(sq.String(length=40), nullable=False)
    city = sq.Column(sq.String(length=100), nullable=False)


class Photos(Base):
    """
    Класс для создания отношения photos - содержащая ссылки и количество лайков фотографий
    photo_id -  уникальное id каждой фотографии
    user_id - уникальное id пользователя из отношения user, чьи фотографии добавлены в БД
    likes - количество лайков
    link - ссылка на фотографию
    user - связь отношения photos с отношением user
    """

    __tablename__ = 'photos'
    
    photo_id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('users.user_id'), nullable=False)
    likes = sq.Column(sq.Integer, nullable=False)
    link = sq.Column(sq.String(length=40), nullable=False)
    user = relationship(Users, backref='photos')


class Favorites(Base):
    """
    Класс для создания отношения favorite, содержащая список избранных пользователей
    favorite_id - уникальное id избранного
    user_id - уникальное id пользователя из отношения user
    user - связь отношения favorite с отношением user
    
    """
    __tablename__ = 'favorite'
    favorite_id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('users.user_id'), nullable=False)
    user = relationship(Users, backref='favorite')


class BlackList(Base):
    __tablename__ = 'black_list'

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('users.user_id'), nullable=False)
    black_list_id = sq.Column(sq.Integer, sq.ForeignKey('users.user_id'), nullable=False)


def create_table(engine):
    """Функция для создания отношений и удаления, при следующем его создании"""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

