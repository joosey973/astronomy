import sqlalchemy
import datetime as dt
from sqlalchemy import orm
from .data_base_session import SqlBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(SqlBase, UserMixin):
    __tablename__ = 'users'
    id = sqlalchemy.Column(
        sqlalchemy.Integer, primary_key=True, autoincrement=True)
    username = sqlalchemy.Column(
        sqlalchemy.Integer, unique=True, index=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    profile_image = sqlalchemy.Column(sqlalchemy.String)
    age = sqlalchemy.Column(sqlalchemy.Integer)
    gender = sqlalchemy.Column(sqlalchemy.String)
    hashed_password = sqlalchemy.Column(sqlalchemy.String)
    profile_url = sqlalchemy.Column(sqlalchemy.String)
    created_date = sqlalchemy.Column(
        sqlalchemy.DateTime, default=dt.datetime.now)
    records = orm.relationship('Records', back_populates="user")

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)
