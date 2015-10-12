from flask.ext.login import UserMixin
from sqlalchemy.ext.declarative import declarative_base
from lmda import db

Base = declarative_base()


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    creation_date = db.Column(db.DateTime, nullable=False)
    api_key = db.Column(db.String, nullable=False, unique=True)
    encryption_enabled = db.Column(db.Boolean, nullable=False, default=False)
    theme_name = db.Column(db.String, nullable=False, default='Material')

    @staticmethod
    def by_name(username):
        return User.query.filter(db.func.lower(User.username) == db.func.lower(username)).first()

    @staticmethod
    def by_id(id):
        return User.query.filter(User.id == id).first()

    @staticmethod
    def by_api_key(key):
        return User.query.filter(User.api_key == key).first()


class File(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner = db.Column(db.Integer)
    name = db.Column(db.String, nullable=False, unique=True)
    extension = db.Column(db.String, nullable=False)
    encrypted = db.Column(db.Boolean, nullable=False, default=False)
    local_name = db.Column(db.String)
    upload_date = db.Column(db.DateTime)
    has_thumbnail = db.Column(db.Boolean, nullable=False, default=False)

    @staticmethod
    def by_name(name):
        # Strip off extension
        name = name.rsplit('.', 1)[0]

        return File.query.filter(File.name == name).first()

    @staticmethod
    def for_user(id):
        return File.query.filter(File.owner == id)


class Paste(db.Model):
    __tablename__ = 'pastes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner = db.Column(db.Integer)
    name = db.Column(db.String, nullable=False, unique=True)
    content_json = db.Column(db.String, nullable=False)
    is_code = db.Column(db.Boolean, nullable=False)
    upload_date = db.Column(db.DateTime)

    @staticmethod
    def by_name(name):
        return Paste.query.filter(Paste.name == name).first()


class Thumbnail(db.Model):
    __tablename__ = 'thumbnails'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    parent_name = db.Column(db.String, nullable=False, unique=True)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String, nullable=False)

    @staticmethod
    def by_parent(name):
        return Thumbnail.query.filter(Thumbnail.parent_name == name).all()
