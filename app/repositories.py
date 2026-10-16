from app.database import DatabaseConnection

class VehiculoRepository:

    @staticmethod
    def obtener_vehiculos():
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.callproc("sp_obtener_vehiculos")
            res = [r.fetchall() for r in cursor.stored_results()][0]
            return res
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def obtener_vehiculo(id_vehiculo: int):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.callproc("sp_obtener_vehiculo", (id_vehiculo,))
            res = None
            for result in cursor.stored_results():
                rows = result.fetchall()
                if rows:
                    res = rows[0]
            
            if res:
                return res

            cursor.execute("SELECT * FROM vehiculos WHERE id_vehiculo = %s", (id_vehiculo,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def ejecutar_movimiento_transaccion(id_vehiculo: int, id_comando: int, origen: str):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.callproc("sp_actualizar_estado_vehiculo", (id_vehiculo, id_comando))
            cursor.callproc("sp_registrar_historial_comando", (id_vehiculo, id_comando, origen))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def obtener_historial_reciente(id_vehiculo: int, limite: int = 10):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.callproc("sp_obtener_historial_vehiculo", (id_vehiculo, limite))
            for result in cursor.stored_results():
                rows = result.fetchall()
                if rows is not None:
                    return rows

            # Consulta flexible que selecciona todos los campos de historial_comandos
            query = """
                SELECT 
                    h.*,
                    c.nombre AS comando
                FROM historial_comandos h
                LEFT JOIN comandos c ON h.id_comando = c.id_comando
                WHERE h.id_vehiculo = %s
                ORDER BY h.id_historial DESC
                LIMIT %s
            """
            cursor.execute(query, (id_vehiculo, limite))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()