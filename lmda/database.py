import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

_script_dir = os.path.dirname(os.path.realpath(__file__))
engine = create_engine('sqlite:///' + _script_dir + '/dev.db', echo=True)
session = sessionmaker(bind=engine)()
