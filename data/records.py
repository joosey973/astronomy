import sqlalchemy
from .data_base_session import Base
import datetime as dt
from sqlalchemy import orm


class Records(Base):
    __tablename__ = "records"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    content = sqlalchemy.Column(sqlalchemy.String)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=dt.datetime.now)
    count_of_claims = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship("User")
