import sqlalchemy
from .db_session import SqlAlchemyBase


class Events(SqlAlchemyBase):
    __tablename__ = "astronomical_events"
    id = sqlalchemy.Column(sqlalchemy.Integer, autoincrement=True, primary_key=True)
    date_of_event = sqlalchemy.Column(sqlalchemy.String)
    events = sqlalchemy.Column(sqlalchemy.String)