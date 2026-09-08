from typing import Any, Optional, dict, list

import mssql_python


class MSSQLClient:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._conn = None

    def get_connection(self):
        if self._conn is None:
            self._conn = mssql_python.connect(self.connection_string)
        return self._conn

    def execute_query(self, query: str, params: tuple = ()) -> list[dict[str, Any]]:
        try:
            conn = self.get_connection()
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                columns = [column[0] for column in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception:
            self.close()
            raise

    def close(self):
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass
            finally:
                self._conn = None

db_client = MSSQLClient()