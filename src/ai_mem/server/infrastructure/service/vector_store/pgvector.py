#! /usr/bin/python
#
# Copyright (C) 2025 Paradox
#
# Release: 2.5.5
# @link olivia.paradox.ai
#

__author__ = "tri.tran"
__date__ = "$Nov 17, 2025 13:45:34$"

from contextlib import contextmanager
from psycopg2.pool import ThreadedConnectionPool as ConnectionPool
from psycopg2.extras import execute_values, Json

from ai_mem.server.application.interface.vector_store import BaseVectorStore


class PgVectorStore(BaseVectorStore):
    def __init__(
        self,
        dbname="postgres",
        collection_name="temp_memory",
        minconn=1,
        maxconn=5,
        connection_string=None,
        connection_pool=None,
    ):
        self.dbname = dbname
        self.collection_name = collection_name
        self.connection_pool = None

        if connection_pool is not None:
            self.connection_pool = connection_pool
        elif connection_string is None:
            raise ValueError("Either connection_string or connection_pool must be provided")

        if self.connection_pool is None:
            self.connection_pool = ConnectionPool(minconn=minconn, maxconn=maxconn, dsn=connection_string)

    @contextmanager
    def _get_cursor(self, commit: bool = False):
        conn = self.connection_pool.getconn()
        cur = conn.cursor()
        try:
            yield cur
            if commit:
                conn.commit()
        except Exception as exc:
            conn.rollback()
            raise exc
        finally:
            cur.close()
            self.connection_pool.putconn(conn)

    def insert(self, vector, vector_id=None, payload=None):
        # todo: handle execute with ORM later

        rows = [(vector_id, vector, Json(payload))]
        with self._get_cursor(commit=True) as cur:
            execute_values(
                cur,
                f"INSERT INTO {self.collection_name} (id, vector, payload) VALUES %s",
                rows,
            )
