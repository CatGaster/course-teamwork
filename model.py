import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

"""Объект для хранения информации о всех отношениях и данных в них в БД"""
Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    user_id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.String(length=40))
    first_name = sq.Column(sq.String(length=40))
    last_name = sq.Column(sq.String(length=40))
    # gender = sq.Column(sq.String(length=40), nullable=False)
    # age = sq.Column(sq.Integer, nullable=False)
    user_link = sq.Column(sq.String(length=40))
    # city = sq.Column(sq.String(length=100), nullable=False)

    def __str__(self):
        return f'{self.user_id}'


class Photos(Base):
    __tablename__ = 'photos'
    
    photo_id = sq.Column(sq.Integer, primary_key=True)
    id = sq.Column(sq.Integer, sq.ForeignKey('users.user_id'), nullable=False)
    href = sq.Column(sq.String(length=40), nullable=False)
    user = relationship(Users, backref='photos')



class Favorites(Base):
    """
    Класс для создания отношения favorite, содержащая список избранных пользователей
    favorite_id - уникальное id избранного
    user_id - уникальное id пользователя из отношения user
    user - связь отношения favorite с отношением user
    
    """
    __tablename__ = 'favorite'
    id = sq.Column(sq.Integer, primary_key=True)
    user_id = sq.Column(sq.Integer, sq.ForeignKey('users.user_id'), nullable=False)
    favorite_user_id = sq.Column(sq.Integer, sq.ForeignKey('users.user_id'), nullable=False)

    # user = relationship(Users, backref='favorite')


# class Black_list(Base):
#     __tablename__ = 'black_list'

#     id = sq.Column(sq.Integer, primary_key=True)
#     user_id = sq.Column(sq.Integer, sq.ForeignKey('users.user_id'), nullable=False)
#     black_list_id = sq.Column(sq.Integer, sq.ForeignKey('users.user_id'), nullable=False)


def create_table(engine):
    """Функция для создания отношений и удаления, при следующем его создании"""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

