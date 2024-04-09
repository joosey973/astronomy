import sqlalchemy
from .data_base_session import SqlBase
import datetime as dt
from sqlalchemy import orm


class Comments(SqlBase):
    __tablename__ = "comments"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    comment_content = sqlalchemy.Column(sqlalchemy.String)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=dt.datetime.now)
    count_of_likes = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    post_id = sqlalchemy.Column(sqlalchemy.Integer)
    commenter_username = sqlalchemy.Column(sqlalchemy.String)
