import os
from collections.abc import Generator, Mapping
from functools import lru_cache

from sqlalchemy import Engine, URL, create_engine
from sqlalchemy.orm import Session


def database_url_from_environment(
    environment: Mapping[str, str] | None = None,
) -> URL:
    values = os.environ if environment is None else environment
    username = values.get("MYSQL_USER")
    password = values.get("MYSQL_PASSWORD")

    if not username or not password:
        raise RuntimeError("MYSQL_USER and MYSQL_PASSWORD must be configured.")

    return URL.create(
        "mysql+pymysql",
        username=username,
        password=password,
        host=values.get("MYSQL_HOST", "127.0.0.1"),
        port=int(values.get("MYSQL_PORT", "3306")),
        database=values.get("MYSQL_DATABASE", "planmaker"),
    )


@lru_cache
def get_engine() -> Engine:
    return create_engine(database_url_from_environment(), pool_pre_ping=True)


def get_db_session() -> Generator[Session, None, None]:
    with Session(get_engine()) as session:
        yield session
