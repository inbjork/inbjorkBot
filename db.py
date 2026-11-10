import sqlite3
from typing import Any, Dict, List, Optional, Tuple, Union

class Database:
    
    """
    Clase para manejar una base de datos SQLite3.
    Permite ejecutar consultas con parámetros y obtener resultados
    individuales (fetchone) o todos (fetchall).
    """

    def __init__(self, db_path: str):
        """
        Inicializa la instancia con la ruta de la base de datos.
        :param db_path: Ruta del archivo .db (ej: 'datos.db')
        """
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None

    def connect(self) -> None:
        """Establece la conexión a la base de datos."""
        self.connection = sqlite3.connect(self.db_path)
        # Permite acceder a columnas por nombre (opcional pero útil)
        self.connection.row_factory = sqlite3.Row

    def disconnect(self) -> None:
        """Cierra la conexión si está abierta."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def execute_query(
        self,
        query: str,
        params: Union[Tuple, Dict, List] = (),
        fetch_one: bool = False,
        fetch_all: bool = False,
    ) -> Union[None, sqlite3.Row, List[sqlite3.Row]]:
        """
        Ejecuta una consulta SQL (SELECT, INSERT, UPDATE, DELETE) con parámetros.
        Si fetch_one=True retorna una fila (como sqlite3.Row).
        Si fetch_all=True retorna todas las filas (lista de sqlite3.Row).
        Si ambas son False, retorna None (útil para INSERT/UPDATE/DELETE).

        :param query: Cadena SQL.
        :param params: Parámetros para la consulta (tupla, lista o dict).
        :param fetch_one: Si es True, retorna la primera fila.
        :param fetch_all: Si es True, retorna todas las filas.
        :return: Dependiendo del flag.
        """
        if not self.connection:
            self.connect()

        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params)
            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            else:
                result = None
            # Para SELECT no se debe hacer commit, pero para escritura se puede delegar
            if not (fetch_one or fetch_all):
                # Si es INSERT/UPDATE/DELETE, autocommit opcional
                self.connection.commit()
                pass
        except sqlite3.Error as e:
            print(f"Error ejecutando la consulta: {e}")
            raise
        finally:
            self.disconnect()

        return result

    def commit(self) -> None:
        """Guarda los cambios pendientes en la base de datos."""
        if self.connection:
            self.connection.commit()

    def rollback(self) -> None:
        """Deshace los cambios pendientes."""
        if self.connection:
            self.connection.rollback()

    # Métodos de conveniencia para fetch_all y fetch_one
    def fetch_all(self, query: str, params: Union[Tuple, Dict, List] = ()) -> List[sqlite3.Row]:
        """Ejecuta SELECT y retorna todas las filas."""
        return self.execute_query(query, params, fetch_all=True)

    def fetch_one(self, query: str, params: Union[Tuple, Dict, List] = ()) -> Optional[sqlite3.Row]:
        """Ejecuta SELECT y retorna solo la primera fila."""
        return self.execute_query(query, params, fetch_one=True)

    def execute(self, query: str, params: Union[Tuple, Dict, List] = ()) -> None:
        """Ejecuta una consulta que no retorna resultados (INSERT, UPDATE, DELETE)."""
        self.execute_query(query, params, fetch_one=False, fetch_all=False)

    # Context manager para usar con 'with'
    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        self.disconnect()