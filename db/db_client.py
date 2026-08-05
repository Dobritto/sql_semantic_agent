import psycopg2


class DBClient:
    def __init__(self, host: str, port: int, dbname: str, user: str, password: str):
        self.connection_params = dict(
            host=host, port=port, dbname=dbname, user=user, password=password,
        )

    def _get_connection(self):
        return psycopg2.connect(**self.connection_params)

    def run(self, sql: str) -> tuple[bool, list[str] | str, list[tuple] | None]:
        """
        Возвращает (success, columns, rows)
        success=True (True, columns, rows)
        success=False (False, text error, None)
        """
        conn = self._get_connection()

        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return True, columns, rows

        except psycopg2.Error as e:
            return False, str(e), None

        finally:
            conn.close()
