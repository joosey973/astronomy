import sqlalchemy
from .data_base_session import SqlBase
import datetime as dt
from sqlalchemy import orm


class Records(SqlBase):
    __tablename__ = "records"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=dt.datetime.now)
    post_url = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    edit = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    delete = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    claim = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    count_of_likes = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=False)
    count_of_claims = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=False)
    count_of_views = sqlalchemy.Column(sqlalchemy.Integer, default=0, nullable=False)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship("User")
