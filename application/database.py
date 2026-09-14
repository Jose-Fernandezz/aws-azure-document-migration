import logging
from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row

from application.config import Config


logger = logging.getLogger(__name__)


@contextmanager
def get_connection():
    connection = None

    try:
        connection = psycopg.connect(
            Config.DATABASE_URL,
            row_factory=dict_row,
        )

        yield connection

        connection.commit()

    except Exception:
        if connection is not None:
            connection.rollback()

        logger.exception("Database operation failed.")
        raise

    finally:
        if connection is not None:
            connection.close()


def test_database_connection():
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 AS status;")
                result = cursor.fetchone()

        return result["status"] == 1

    except Exception:
        logger.exception("Database health check failed.")
        return False


def fetch_all(query, parameters=None):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, parameters or ())
            return cursor.fetchall()


def fetch_one(query, parameters=None):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, parameters or ())
            return cursor.fetchone()


def execute_query(query, parameters=None):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, parameters or ())