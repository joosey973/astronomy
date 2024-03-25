import sqlalchemy
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session


__factory = None
SqlAlchemyBase = orm.declarative_base()


class DataBaseConnectionError(Exception):
    pass


def global_init(db_file: str) -> None:
    global __factory
    if __factory:
        return
    if not db_file or not db_file.strip():
        raise DataBaseConnectionError('Необходимо указать файл базы данных.')
    connection = f"sqlite:///{db_file.strip()}?check_same_thread=False"
    print(f"Подключение к базе данных {connection}")
    engine = sqlalchemy.create_engine(connection, echo=False)
    __factory = orm.sessionmaker(bind=engine)
    from . import __all_models
    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
