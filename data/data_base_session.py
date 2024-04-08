import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine, async_session, AsyncSession


__main_factory = None
SqlBase = sqlalchemy.orm.declarative_base()


class DataBaseConnectionError(Exception):
    pass


async def data_base_init(db_file: str) -> None:
    global __main_factory
    if __main_factory:
        return
    if not db_file or not db_file.strip():
        raise DataBaseConnectionError('Необходимо указать файл базы данных.')
    connection = f"sqlite+aiosqlite:///{db_file.strip()}?check_same_thread=False"
    print(f"Подключение к базе данных {connection}")
    base_engine = create_async_engine(connection, echo=False)
    __main_factory = async_session(base_engine, class_=AsyncSession)
    from . import __all_models
    async with base_engine.begin() as conn:
        await conn.run_sync(SqlBase.metadata.create_all)


async def new_session():
    global __main_factory
    async with __main_factory() as session:
        yield session
