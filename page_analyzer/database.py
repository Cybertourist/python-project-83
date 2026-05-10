import os
from datetime import datetime

import psycopg2
from psycopg2.extras import NamedTupleCursor


def get_db_connection():
    return psycopg2.connect(os.getenv('DATABASE_URL'))


def get_urls():
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curr:
            curr.execute("""
                SELECT
                    urls.id,
                    urls.name,
                    url_checks.created_at AS last_check,
                    url_checks.status_code
                FROM urls
                LEFT JOIN url_checks ON urls.id = url_checks.url_id
                AND url_checks.id = (
                    SELECT MAX(id) FROM url_checks WHERE url_id = urls.id
                )
                ORDER BY urls.id DESC
            """)
            return curr.fetchall()


def get_url_by_name(name):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curr:
            curr.execute("SELECT id FROM urls WHERE name = %s", (name,))
            return curr.fetchone()


def add_url(name):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curr:
            curr.execute(
                "INSERT INTO urls (name, created_at) VALUES (%s, %s) "
                "RETURNING id",
                (name, datetime.now())
            )
            inserted_id = curr.fetchone().id
            conn.commit()
            return inserted_id


def get_url_by_id(url_id):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curr:
            curr.execute("SELECT * FROM urls WHERE id = %s", (url_id,))
            return curr.fetchone()


def get_checks_by_url_id(url_id):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curr:
            curr.execute(
                "SELECT * FROM url_checks WHERE url_id = %s ORDER BY id DESC",
                (url_id,)
            )
            return curr.fetchall()


def add_check(url_id, status_code, h1, title, description):
    with get_db_connection() as conn:
        with conn.cursor() as curr:
            curr.execute(
                """
                INSERT INTO url_checks
                (url_id, status_code, h1, title, description, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (url_id, status_code, h1, title, description, datetime.now())
            )
            conn.commit()