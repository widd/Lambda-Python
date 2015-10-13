from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from lmda import db
from lmda.migrate import oldmodels
from lmda.models import User, File, Paste

db.create_all()

engine = create_engine('mysql://lambda:lambda@localhost/lambda_go')
Session = sessionmaker(bind=engine)
session = Session()

for user in session.query(oldmodels.User).all():
    new_user = User(id=user.id, username=user.username, password=user.password, creation_date=user.creation_date, api_key=user.apikey, encryption_enabled=user.encryption_enabled, theme_name=user.theme_name)
    db.session.add(new_user)
    db.session.commit()

for file in session.query(oldmodels.File).all():
    new_file = File(id=file.id, owner=file.owner, name=file.name, extension=file.extension, encrypted=file.encrypted, local_name=file.local_name, upload_date=file.upload_date, has_thumbnail=False)
    db.session.add(new_file)
    db.session.commit()

for paste in session.query(oldmodels.Paste).all():
    new_paste = Paste(id=paste.id, owner=paste.owner, name=paste.name, content_json=paste.content_json, is_code=paste.is_code, upload_date=paste.upload_date)
    db.session.add(new_paste)
    db.session.commit()

exit(0)
