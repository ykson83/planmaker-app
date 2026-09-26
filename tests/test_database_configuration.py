import pytest
from sqlalchemy.engine import URL

from app.db.session import database_url_from_environment


def test_database_url_is_built_from_mysql_environment() -> None:
    url = database_url_from_environment(
        {
            "MYSQL_DATABASE": "planmaker_test",
            "MYSQL_USER": "test_user",
            "MYSQL_PASSWORD": "test/password",
            "MYSQL_HOST": "mysql.test",
            "MYSQL_PORT": "3307",
        }
    )

    assert isinstance(url, URL)
    assert url.drivername == "mysql+pymysql"
    assert url.username == "test_user"
    assert url.password == "test/password"
    assert url.host == "mysql.test"
    assert url.port == 3307
    assert url.database == "planmaker_test"


def test_database_url_rejects_missing_credentials() -> None:
    with pytest.raises(RuntimeError, match="MYSQL_USER and MYSQL_PASSWORD"):
        database_url_from_environment({"MYSQL_USER": "test_user"})
