from reddit.database import CrudMixin
from reddit.extensions import bcrypt, db
from datetime import datetime


class User(db.Model, CrudMixin):
    __tablename__ = "user"

    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.Binary(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    bio = db.Column(db.String(300), nullable=True)
    image = db.Column(db.String(128), nullable=True)

    def __init__(self, username=None, password=None, **kwargs):
        super(User, self).__init__(username=username, password=password, **kwargs)
        if password is not None:
            self.set_password(password)
        else:
            self.password = None

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def verify(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User [{self.username}]>"

class UserProfile(db.Model, CrudMixin):
    __tablename__ = "user_profile"

    address = db.Column(db.String(64), unique=True)
