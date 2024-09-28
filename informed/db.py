from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from contextvars import ContextVar

from alembic import command, config
from loguru import logger as log
from sqlalchemy import Connection, Engine, create_engine
from sqlalchemy.engine.url import URL, make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from informed.config import DatabaseConfig


def upgrade_db(conn: Connection, revision: str = "head") -> None:
    conf = config.Config("alembic.ini")
    conf.attributes["connection"] = conn
    command.upgrade(conf, revision)


def downgrade_db(conn: Connection, revision: str = "base") -> None:
    conf = config.Config("alembic.ini")
    conf.attributes["connection"] = conn
    command.downgrade(conf, revision)


class DatabaseEngine:
    # TODO (peter): using contextvars allows us to run concurrent tests/evals
    # but we should probably use dependency injection instead
    use_contextvars: bool = False
    _instance: AsyncEngine | None = None
    _instance_var: ContextVar[AsyncEngine | None] = ContextVar("db_engine")

    @classmethod
    def _get_instance(cls) -> AsyncEngine | None:
        return cls._instance_var.get(None) if cls.use_contextvars else cls._instance

    @classmethod
    def _set_instance(cls, engine: AsyncEngine | None) -> None:
        if cls.use_contextvars:
            cls._instance_var.set(engine)
        else:
            cls._instance = engine

    @classmethod
    def init(
        cls,
        url: URL | str,
        max_pool_size: int = 5,
        max_overflow: int = 10,
        use_contextvars: bool = False,
    ) -> AsyncEngine:
        cls.use_contextvars = use_contextvars
        engine = cls._get_instance()
        if engine is None:
            engine = create_async_engine(url, echo=False)
            cls._set_instance(engine)
        return engine

    @classmethod
    def get(cls) -> AsyncEngine:
        engine = cls._get_instance()
        if engine is None:
            raise ValueError("DatabaseEngine not initialized")
        return engine

    @classmethod
    def get_sync_engine(cls) -> Engine:
        engine = cls._get_instance()
        if engine is None:
            raise ValueError("DatabaseEngine not initialized")
        sync_engine = create_engine(engine.url, echo=False)
        return sync_engine

    @classmethod
    async def delete(cls) -> None:
        engine = cls._get_instance()
        if engine is not None:
            await engine.dispose()
            cls._set_instance(None)


@asynccontextmanager
async def session_maker() -> AsyncGenerator[AsyncSession, None]:
    engine = DatabaseEngine.get()
    async with async_sessionmaker(
        expire_on_commit=False, bind=engine, class_=AsyncSession
    )() as session:
        yield session


# sync version of the session maker, intended primarily for testing, migrations etc rather than the core application.
def sync_session_maker() -> Session:
    sync_engine = DatabaseEngine.get_sync_engine()
    return sessionmaker(bind=sync_engine, expire_on_commit=False)()


def init_db(database_config: DatabaseConfig) -> None:
    url = make_url(database_config.db_url)
    DatabaseEngine.init(
        url,
        database_config.connection_pool_config.max_pool_size,
        database_config.connection_pool_config.max_overflow,
    )
    log.info(
        "Setting up db, drivername: {}, username: {}, host: {}, port: {}, database: {}, max_pool_size: {}, max_overflow: {}",
        url.drivername,
        url.username,
        url.host,
        url.port,
        url.database,
        database_config.connection_pool_config.max_pool_size,
        database_config.connection_pool_config.max_overflow,
    )
