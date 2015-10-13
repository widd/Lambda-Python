from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    creation_date = Column(Date)
    apikey = Column(String)
    encryption_enabled = Column(Boolean)
    theme_name = Column(String)


class File(Base):
    __tablename__ = 'files'

    id = Column(Integer, primary_key=True)
    owner = Column(Integer)
    name = Column(String)
    extension = Column(String)
    upload_date = Column(DateTime)
    encrypted = Column(Boolean)
    local_name = Column(String)


class Paste(Base):
    __tablename__ = 'pastes'

    id = Column(Integer, primary_key=True)
    owner = Column(Integer)
    name = Column(String)
    upload_date = Column(DateTime)
    content_json = Column(String)
    is_code = Column(Boolean)
