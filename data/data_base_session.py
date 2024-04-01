import sqlalchemy
from sqlalchemy.orm import Session


__main_factory = None
SqlBase = sqlalchemy.orm.declarative_base()


class DataBaseConnectionError(Exception):
    pass


def data_base_init(db_file: str) -> None:
    global __main_factory
    if __main_factory:
        return
    if not db_file or not db_file.strip():
        raise DataBaseConnectionError('Необходимо указать файл базы данных.')
    connection = f"sqlite:///{db_file.strip()}?check_same_thread=False"
    print(f"Подключение к базе данных {connection}")
    base_engine = sqlalchemy.create_engine(connection, echo=False)
    __main_factory = sqlalchemy.orm.sessionmaker(bind=base_engine)
    from . import __all_models
    SqlBase.metadata.create_all(base_engine)


def new_session() -> Session:
    global __main_factory
    return __main_factory()
