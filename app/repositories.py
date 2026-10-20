import mysql.connector
from app.database import DatabaseConnection

class VehiculoRepository:

    # =========================================================================
    # 1. VEHÍCULOS (5 Endpoints / Procedimientos)
    # =========================================================================
    @staticmethod
    def obtener_vehiculos():
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_obtener_vehiculos")
                for result in cursor.stored_results():
                    return result.fetchall()
            except Exception:
                pass
            cursor.execute("SELECT * FROM vehiculos")
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def obtener_vehiculo(id_vehiculo: int):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_obtener_vehiculo", (id_vehiculo,))
                for result in cursor.stored_results():
                    res = result.fetchall()
                    return res[0] if res else None
            except Exception:
                pass
            cursor.execute("SELECT * FROM vehiculos WHERE id_vehiculo = %s", (id_vehiculo,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def crear_vehiculo(nombre: str, descripcion: str):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_crear_vehiculo", (nombre, descripcion))
            except Exception:
                cursor.execute(
                    "INSERT INTO vehiculos (nombre, descripcion) VALUES (%s, %s)",
                    (nombre, descripcion)
                )
            conn.commit()
            return {"status": "ok", "mensaje": "Vehículo creado"}
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def actualizar_vehiculo(id_vehiculo: int, nombre: str, descripcion: str):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_actualizar_vehiculo", (id_vehiculo, nombre, descripcion))
            except Exception:
                cursor.execute(
                    "UPDATE vehiculos SET nombre = %s, descripcion = %s WHERE id_vehiculo = %s",
                    (nombre, descripcion, id_vehiculo)
                )
            conn.commit()
            return {"status": "ok", "mensaje": "Vehículo actualizado"}
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def eliminar_vehiculo(id_vehiculo: int):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_eliminar_vehiculo", (id_vehiculo,))
            except Exception:
                cursor.execute("DELETE FROM vehiculos WHERE id_vehiculo = %s", (id_vehiculo,))
            conn.commit()
            return {"status": "ok", "mensaje": "Vehículo eliminado"}
        finally:
            cursor.close()
            conn.close()

    # =========================================================================
    # 2. COMANDOS (4 Endpoints / Procedimientos)
    # =========================================================================
    @staticmethod
    def obtener_comandos():
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_obtener_comandos")
                for result in cursor.stored_results():
                    return result.fetchall()
            except Exception:
                pass
            cursor.execute("SELECT * FROM comandos")
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def obtener_comando(id_comando: int):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_obtener_comando", (id_comando,))
                for result in cursor.stored_results():
                    res = result.fetchall()
                    return res[0] if res else None
            except Exception:
                pass
            cursor.execute("SELECT * FROM comandos WHERE id_comando = %s", (id_comando,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def crear_comando(nombre: str, instruccion: str):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_crear_comando", (nombre, instruccion))
            except Exception:
                cursor.execute(
                    "INSERT INTO comandos (nombre, instruccion) VALUES (%s, %s)",
                    (nombre, instruccion)
                )
            conn.commit()
            return {"status": "ok", "mensaje": "Comando creado"}
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def actualizar_comando(id_comando: int, nombre: str, instruccion: str):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_actualizar_comando", (id_comando, nombre, instruccion))
            except Exception:
                cursor.execute(
                    "UPDATE comandos SET nombre = %s, instruccion = %s WHERE id_comando = %s",
                    (nombre, instruccion, id_comando)
                )
            conn.commit()
            return {"status": "ok", "mensaje": "Comando actualizado"}
        finally:
            cursor.close()
            conn.close()

    # =========================================================================
    # 3. ESTADO Y MOVIMIENTO INDIVIDUAL
    # =========================================================================
    @staticmethod
    def obtener_ultimo_estado(id_vehiculo: int):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_obtener_ultimo_estado", (id_vehiculo,))
                for result in cursor.stored_results():
                    res = result.fetchall()
                    return res[0] if res else None
            except Exception:
                pass
            cursor.execute("SELECT * FROM estado_vehiculo WHERE id_vehiculo = %s", (id_vehiculo,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def registrar_movimiento(id_vehiculo: int, id_comando: int, origen: str):
        """
        Ejecuta la lógica de actualización de estado + inserción en el historial.
        """
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # 1. Actualizar Estado
            try:
                cursor.callproc("sp_actualizar_estado_vehiculo", (id_vehiculo, id_comando, origen))
            except Exception:
                cursor.execute(
                    "UPDATE estado_vehiculo SET ultimo_comando_id = %s, origen = %s, fecha_actualizacion = NOW() WHERE id_vehiculo = %s",
                    (id_comando, origen, id_vehiculo)
                )

            # 2. Registrar en Historial
            try:
                cursor.callproc("sp_registrar_historial_comando", (id_vehiculo, id_comando, origen))
            except Exception:
                cursor.execute(
                    "INSERT INTO historial_comandos (id_vehiculo, id_comando, origen, fecha_registro) VALUES (%s, %s, %s, NOW())",
                    (id_vehiculo, id_comando, origen)
                )

            conn.commit()
            return {"status": "ok", "mensaje": "Movimiento registrado con éxito"}
        finally:
            cursor.close()
            conn.close()

    # =========================================================================
    # 4. HISTORIAL
    # =========================================================================
    @staticmethod
    def obtener_historial_vehiculo(id_vehiculo: int):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_obtener_historial_vehiculo", (id_vehiculo,))
                for result in cursor.stored_results():
                    return result.fetchall()
            except Exception:
                pass
            cursor.execute(
                "SELECT * FROM historial_comandos WHERE id_vehiculo = %s ORDER BY fecha_registro DESC LIMIT 10",
                (id_vehiculo,)
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    # =========================================================================
    # 5. DEMO
    # =========================================================================
    @staticmethod
    def obtener_demos():
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_obtener_demos")
                for result in cursor.stored_results():
                    return result.fetchall()
            except Exception:
                pass
            cursor.execute("SELECT * FROM demo")
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def obtener_demo(id_demo: int):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_obtener_demo", (id_demo,))
                for result in cursor.stored_results():
                    res = result.fetchall()
                    return res[0] if res else None
            except Exception:
                pass
            cursor.execute("SELECT * FROM demo WHERE id_demo = %s", (id_demo,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def crear_demo(nombre: str, descripcion: str):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_crear_demo", (nombre, descripcion))
            except Exception:
                cursor.execute(
                    "INSERT INTO demo (nombre, descripcion) VALUES (%s, %s)",
                    (nombre, descripcion)
                )
            conn.commit()
            return {"status": "ok", "mensaje": "DEMO creada"}
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def eliminar_demo(id_demo: int):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_eliminar_demo", (id_demo,))
            except Exception:
                cursor.execute("DELETE FROM demo WHERE id_demo = %s", (id_demo,))
            conn.commit()
            return {"status": "ok", "mensaje": "DEMO eliminada"}
        finally:
            cursor.close()
            conn.close()

    # =========================================================================
    # 6. DEMO MOVIMIENTOS Y SECUENCIA DEMO
    # =========================================================================
    @staticmethod
    def obtener_movimientos_demo(id_demo: int):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_obtener_movimientos_demo", (id_demo,))
                for result in cursor.stored_results():
                    return result.fetchall()
            except Exception:
                pass
            cursor.execute(
                "SELECT * FROM demo_movimientos WHERE id_demo = %s ORDER BY orden ASC",
                (id_demo,)
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def agregar_movimiento_demo(id_demo: int, id_comando: int, orden: int, tiempo_espera: int):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_agregar_movimiento_demo", (id_demo, id_comando, orden, tiempo_espera))
            except Exception:
                cursor.execute(
                    "INSERT INTO demo_movimientos (id_demo, id_comando, orden, tiempo_espera) VALUES (%s, %s, %s, %s)",
                    (id_demo, id_comando, orden, tiempo_espera)
                )
            conn.commit()
            return {"status": "ok", "mensaje": "Movimiento asignado a DEMO"}
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def actualizar_movimiento_demo(id_movimiento_demo: int, orden: int, tiempo_espera: int):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_actualizar_movimiento_demo", (id_movimiento_demo, orden, tiempo_espera))
            except Exception:
                cursor.execute(
                    "UPDATE demo_movimientos SET orden = %s, tiempo_espera = %s WHERE id_movimiento_demo = %s",
                    (orden, tiempo_espera, id_movimiento_demo)
                )
            conn.commit()
            return {"status": "ok", "mensaje": "Movimiento DEMO actualizado"}
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def eliminar_movimiento_demo(id_movimiento_demo: int):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_eliminar_movimiento_demo", (id_movimiento_demo,))
            except Exception:
                cursor.execute("DELETE FROM demo_movimientos WHERE id_movimiento_demo = %s", (id_movimiento_demo,))
            conn.commit()
            return {"status": "ok", "mensaje": "Movimiento DEMO eliminado"}
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def actualizar_estado_demo(id_vehiculo: int, id_comando: int):
        """
        Regla de Negocio: Actualiza únicamente el estado sin afectar el historial.
        """
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_actualizar_estado_vehiculo", (id_vehiculo, id_comando, "DEMO"))
            except Exception:
                cursor.execute(
                    "UPDATE estado_vehiculo SET ultimo_comando_id = %s, origen = 'DEMO', fecha_actualizacion = NOW() WHERE id_vehiculo = %s",
                    (id_comando, id_vehiculo)
                )
            conn.commit()
            return {"status": "ok", "mensaje": "Estado actualizado por DEMO"}
        finally:
            cursor.close()
            conn.close()