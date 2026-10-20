from app.database import DatabaseConnection

class VehiculoRepository:

    # =============================================================
    # 1. PROCEDIMIENTOS ALMACENADOS DE VEHÍCULOS (5 SP)
    # =============================================================
    @staticmethod
    def obtener_vehiculos():
        """1. sp_obtener_vehiculos"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.callproc("sp_obtener_vehiculos")
            res = [r.fetchall() for r in cursor.stored_results()]
            return res[0] if res else []
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def obtener_vehiculo(id_vehiculo: int):
        """2. sp_obtener_vehiculo"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.callproc("sp_obtener_vehiculo", (id_vehiculo,))
            for result in cursor.stored_results():
                rows = result.fetchall()
                if rows:
                    return rows[0]
            
            # Fallback en caso de que el SP no devuelva filas directamente
            cursor.execute("SELECT * FROM vehiculos WHERE id_vehiculo = %s", (id_vehiculo,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def crear_vehiculo(nombre: str, descripcion: str, activo: int = 1):
        """3. sp_crear_vehiculo"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.callproc("sp_crear_vehiculo", (nombre, descripcion, activo))
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def actualizar_vehiculo(id_vehiculo: int, nombre: str, descripcion: str, activo: int):
        """4. sp_actualizar_vehiculo"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.callproc("sp_actualizar_vehiculo", (id_vehiculo, nombre, descripcion, activo))
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def eliminar_vehiculo(id_vehiculo: int):
        """5. sp_eliminar_vehiculo"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.callproc("sp_eliminar_vehiculo", (id_vehiculo,))
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()

    # =============================================================
    # 2. PROCEDIMIENTOS ALMACENADOS DE COMANDOS (4 SP)
    # =============================================================
    @staticmethod
    def obtener_comandos():
        """6. sp_obtener_comandos"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.callproc("sp_obtener_comandos")
            res = [r.fetchall() for r in cursor.stored_results()]
            return res[0] if res else []
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def obtener_comando(id_comando: int):
        """7. sp_obtener_comando"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.callproc("sp_obtener_comando", (id_comando,))
            for result in cursor.stored_results():
                rows = result.fetchall()
                if rows:
                    return rows[0]
            return None
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def crear_comando(nombre: str, codigo: str, descripcion: str):
        """8. sp_crear_comando"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.callproc("sp_crear_comando", (nombre, codigo, descripcion))
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def actualizar_comando(id_comando: int, nombre: str, codigo: str, descripcion: str):
        """9. sp_actualizar_comando"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.callproc("sp_actualizar_comando", (id_comando, nombre, codigo, descripcion))
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()

    # =============================================================
    # 3. PROCEDIMIENTOS ALMACENADOS DE ESTADO (2 SP)
    # =============================================================
    @staticmethod
    def obtener_ultimo_estado(id_vehiculo: int):
        """10. sp_obtener_ultimo_estado"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.callproc("sp_obtener_ultimo_estado", (id_vehiculo,))
            for result in cursor.stored_results():
                rows = result.fetchall()
                if rows:
                    return rows[0]
            return None
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def actualizar_estado_demo(id_vehiculo: int, id_comando: int):
        """11. sp_actualizar_estado_vehiculo (Uso directo sin historial para DEMO)"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.callproc("sp_actualizar_estado_vehiculo", (id_vehiculo, id_comando))
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()

    # =============================================================
    # 4. PROCEDIMIENTOS ALMACENADOS DE HISTORIAL (2 SP)
    # =============================================================
    @staticmethod
    def obtener_historial_reciente(id_vehiculo: int, limite: int = 10):
        """12. sp_obtener_historial_vehiculo (Límite máximo 10 registros desc)"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.callproc("sp_obtener_historial_vehiculo", (id_vehiculo, limite))
            for result in cursor.stored_results():
                rows = result.fetchall()
                if rows is not None:
                    return rows

            # Consulta flexible de respaldo
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

    @staticmethod
    def registrar_historial_comando(id_vehiculo: int, id_comando: int, origen: str):
        """13. sp_registrar_historial_comando"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.callproc("sp_registrar_historial_comando", (id_vehiculo, id_comando, origen))
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def ejecutar_movimiento_transaccion(id_vehiculo: int, id_comando: int, origen: str):
        """Ejecución atómica en una sola transacción para Movimiento Individual (POST)"""
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

    # =============================================================
    # 5. PROCEDIMIENTOS ALMACENADOS DE DEMO (4 SP)
    # =============================================================
    @staticmethod
    def obtener_demos():
        """14. sp_obtener_demos"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.callproc("sp_obtener_demos")
            res = [r.fetchall() for r in cursor.stored_results()]
            return res[0] if res else []
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def obtener_demo(id_demo: int):
        """15. sp_obtener_demo"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.callproc("sp_obtener_demo", (id_demo,))
            for result in cursor.stored_results():
                rows = result.fetchall()
                if rows:
                    return rows[0]
            return None
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def crear_demo(nombre: str, descripcion: str):
        """16. sp_crear_demo"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.callproc("sp_crear_demo", (nombre, descripcion))
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def eliminar_demo(id_demo: int):
        """17. sp_eliminar_demo"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.callproc("sp_eliminar_demo", (id_demo,))
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()

    # =============================================================
    # 6. PROCEDIMIENTOS ALMACENADOS DE MOVIMIENTOS DEMO (4 SP)
    # =============================================================
    @staticmethod
    def obtener_movimientos_demo(id_demo: int):
        """18. sp_obtener_movimientos_demo"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.callproc("sp_obtener_movimientos_demo", (id_demo,))
            for result in cursor.stored_results():
                rows = result.fetchall()
                if rows is not None:
                    return rows
            return []
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def agregar_movimiento_demo(id_demo: int, orden: int, id_comando: int, duracion_ms: int, pausa_ms: int):
        """19. sp_agregar_movimiento_demo"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.callproc("sp_agregar_movimiento_demo", (id_demo, orden, id_comando, duracion_ms, pausa_ms))
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def actualizar_movimiento_demo(id_movimiento_demo: int, orden: int, id_comando: int, duracion_ms: int, pausa_ms: int):
        """20. sp_actualizar_movimiento_demo"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.callproc("sp_actualizar_movimiento_demo", (id_movimiento_demo, orden, id_comando, duracion_ms, pausa_ms))
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def eliminar_movimiento_demo(id_movimiento_demo: int):
        """21. sp_eliminar_movimiento_demo"""
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.callproc("sp_eliminar_movimiento_demo", (id_movimiento_demo,))
            conn.commit()
            return True
        finally:
            cursor.close()
            conn.close()