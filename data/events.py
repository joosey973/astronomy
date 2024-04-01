import sqlalchemy
from .data_base_session import SqlBase


class Events(SqlBase):
    __tablename__ = "astronomical_events"
    id = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=True, primary_key=True)
    date_of_event = sqlalchemy.Column(sqlalchemy.String)
    events = sqlalchemy.Column(sqlalchemy.String)
