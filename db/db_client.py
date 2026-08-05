import sqlite3
import psycopg2


class DBClient:
    def __init__(self, db_type: str = 'postrgres', **kwargs):
        self.db_type = db_type
        self.kwargs = kwargs

    def _get_connection(self):
        if self.db_type == 'sqlite':
            path = self.kwargs['path']
            return sqlite3.connect(f'file:{path}?mode=ro', uri=True)

        elif self.db_type == 'postgres':
            return psycopg2.connect(
                host=self.kwargs['host'],
                port=self.kwargs['port'],
                dbname=self.kwargs['dbname'],
                user=self.kwargs['user'],
                password=self.kwargs['password']
            )

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
