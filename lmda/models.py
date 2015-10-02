from flask.ext.login import UserMixin
from sqlalchemy import Integer, Column, String, DateTime, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from lmda import database

Base = declarative_base()


class User(Base, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    creation_date = Column(DateTime, nullable=False)
    api_key = Column(String, nullable=False, unique=True)
    encryption_enabled = Column(Boolean, nullable=False, default=False)
    theme_name = Column(String, nullable=False, default='Material')

    @staticmethod
    def by_name(username):
        return database.session.query(User).filter(func.lower(User.username) == func.lower(username)).first()

    @staticmethod
    def by_id(id):
        return database.session.query(User).filter(User.id == id).first()

    @staticmethod
    def by_api_key(key):
        return database.session.query(User).filter(User.api_key == key).first()


class File(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True, autoincrement=True)
    owner = Column(Integer)
    name = Column(String, nullable=False, unique=True)
    extension = Column(String, nullable=False)
    encrypted = Column(Boolean, nullable=False, default=False)
    local_name = Column(String)
    upload_date = Column(DateTime)

    @staticmethod
    def by_name(name):
        # Strip off extension
        name = name.rsplit('.', 1)[0]

        return database.session.query(File).filter(File.name == name).first()

    @staticmethod
    def for_user(id):
        return database.session.query(File).filter(File.owner == id)


class Paste(Base):
    __tablename__ = 'pastes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    owner = Column(Integer)
    name = Column(String, nullable=False, unique=True)
    content_json = Column(String, nullable=False)
    is_code = Column(Boolean, nullable=False)
    upload_date = Column(DateTime)

    @staticmethod
    def by_name(name):
        return database.session.query(Paste).filter(Paste.name == name).first()
