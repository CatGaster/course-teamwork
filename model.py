import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

"""Объект для хранения информации о всех отношениях и данных в них в БД"""
Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    user_id = sq.Column(sq.Integer, primary_key=True)
    owner_id = sq.Column(sq.String(length=40), nullable=False)
    first_name = sq.Column(sq.String(length=40), nullable=False)
    last_name = sq.Column(sq.String(length=40), nullable=False)
    user_link = sq.Column(sq.String(length=40), nullable=False)

    def __str__(self):
        return f'{self.user_id}'


class Photos(Base):
    __tablename__ = 'photos'
    
    photo_id = sq.Column(sq.Integer, primary_key=True)
    id = sq.Column(sq.Integer, sq.ForeignKey('users.user_id'), nullable=False)
    href = sq.Column(sq.String(length=40), nullable=False)
    # user = relationship(Users, backref='photos')


class Favorites(Base):

    __tablename__ = 'favorite'
    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('users.user_id'))
    favorite_user_id = sq.Column(sq.Integer, sq.ForeignKey('users.user_id'))

    # user = relationship(Users, backref='favorite')
    # user_favorite = relationship(Users, backref='favorite')


class Blacklist(Base):
    __tablename__ = 'black_list'

    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('users.user_id'))
    black_list_id = sq.Column(sq.Integer, sq.ForeignKey('users.user_id'))

    # user = relationship(Users, backref='black_list')


def create_table(engine):
    """Функция для создания отношений и удаления, при следующем его создании"""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
