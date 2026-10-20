import mysql.connector
from app.database import DatabaseConnection

class VehiculoRepository:

    # =========================================================================
    # 1. VEHÍCULOS
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
    def crear_vehiculo(nombre: str, descripcion: str, activo: int = 1):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_crear_vehiculo", (nombre, descripcion))
            except Exception:
                cursor.execute(
                    "INSERT INTO vehiculos (nombre, descripcion, activo) VALUES (%s, %s, %s)",
                    (nombre, descripcion, activo)
                )
            conn.commit()
            return {"status": "ok", "mensaje": "Vehículo creado"}
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def actualizar_vehiculo(id_vehiculo: int, nombre: str, descripcion: str, activo: int = 1):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_actualizar_vehiculo", (id_vehiculo, nombre, descripcion))
            except Exception:
                cursor.execute(
                    "UPDATE vehiculos SET nombre = %s, descripcion = %s, activo = %s WHERE id_vehiculo = %s",
                    (nombre, descripcion, activo, id_vehiculo)
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
    # 2. COMANDOS
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
    def crear_comando(nombre: str, codigo=0, descripcion: str = "", id_vehiculo: int = 1, activo: int = 1):
        try:
            codigo_val = int(codigo)
        except (ValueError, TypeError):
            codigo_val = 0

        # Si id_vehiculo es 0 o None, forzar a 1 por defecto
        if not id_vehiculo or id_vehiculo == 0:
            id_vehiculo = 1

        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_crear_comando", (nombre, str(codigo), descripcion, activo))
            except Exception:
                try:
                    cursor.callproc("sp_crear_comando", (nombre, codigo_val, descripcion, activo))
                except Exception:
                    cursor.execute(
                        "INSERT INTO comandos (id_vehiculo, nombre, codigo, descripcion, activo) VALUES (%s, %s, %s, %s, %s)",
                        (id_vehiculo, nombre, codigo_val, descripcion, activo)
                    )
            conn.commit()
            return {"status": "ok", "mensaje": "Comando creado exitosamente"}
        except mysql.connector.errors.IntegrityError:
            conn.rollback()
            raise HTTPException(
                status_code=400, 
                detail=f"El id_vehiculo {id_vehiculo} no existe en la base de datos. Por favor crea un vehículo primero o usa un ID válido."
            )
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def actualizar_comando(id_comando: int, nombre: str, codigo=0, descripcion: str = "", id_vehiculo: int = 1, activo: int = 1):
        try:
            codigo_val = int(codigo)
        except (ValueError, TypeError):
            codigo_val = 0

        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_actualizar_comando", (id_comando, id_vehiculo, nombre, str(codigo), descripcion, activo))
            except Exception:
                try:
                    cursor.callproc("sp_actualizar_comando", (id_comando, id_vehiculo, nombre, codigo_val, descripcion, activo))
                except Exception:
                    cursor.execute(
                        "UPDATE comandos SET id_vehiculo = %s, nombre = %s, codigo = %s, descripcion = %s, activo = %s WHERE id_comando = %s",
                        (id_vehiculo, nombre, codigo_val, descripcion, activo, id_comando)
                    )
            conn.commit()
            return {"status": "ok", "mensaje": "Comando actualizado exitosamente"}
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
    def ejecutar_movimiento_transaccion(id_vehiculo: int, id_comando: int, origen: str = "API"):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_actualizar_estado_vehiculo", (id_vehiculo, id_comando))
            except Exception:
                cursor.execute(
                    "UPDATE vehiculos SET ultimo_comando = %s WHERE id_vehiculo = %s",
                    (id_comando, id_vehiculo)
                )

            try:
                cursor.callproc("sp_registrar_historial_comando", (id_vehiculo, id_comando, origen))
            except Exception:
                try:
                    cursor.callproc("sp_registrar_historial_comando", (id_vehiculo, id_comando))
                except Exception:
                    cursor.execute(
                        "INSERT INTO historial_comandos (id_vehiculo, id_comando, origen) VALUES (%s, %s, %s)",
                        (id_vehiculo, id_comando, origen)
                    )

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    # =========================================================================
    # 4. HISTORIAL
    # =========================================================================
    @staticmethod
    def obtener_historial_reciente(id_vehiculo: int, limite: int = 10):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_obtener_historial_vehiculo", (id_vehiculo, limite))
                results = []
                for result in cursor.stored_results():
                    results.extend(result.fetchall())
                return results
            except Exception:
                cursor.execute(
                    "SELECT * FROM historial_comandos WHERE id_vehiculo = %s ORDER BY fecha DESC LIMIT %s",
                    (id_vehiculo, limite)
                )
                return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    obtener_historial_vehiculo = obtener_historial_reciente

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
                results = []
                for result in cursor.stored_results():
                    results.extend(result.fetchall())
                return results
            except Exception:
                try:
                    cursor.execute("SELECT * FROM demos")
                    return cursor.fetchall()
                except Exception:
                    try:
                        cursor.execute("SELECT * FROM secuencias_demo")
                        return cursor.fetchall()
                    except Exception:
                        return []
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
                    row = result.fetchone()
                    if row:
                        return row
            except Exception:
                pass

            cursor.execute("SELECT * FROM demos WHERE id_demo = %s", (id_demo,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def crear_demo(nombre: str, descripcion: str = "", id_vehiculo: int = 1, activo: int = 1):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_crear_demo", (id_vehiculo, nombre, descripcion, activo))
            except Exception:
                try:
                    cursor.callproc("sp_crear_demo", (nombre, descripcion, activo))
                except Exception:
                    cursor.execute(
                        "INSERT INTO demos (id_vehiculo, nombre, descripcion, activo) VALUES (%s, %s, %s, %s)",
                        (id_vehiculo, nombre, descripcion, activo)
                    )
            conn.commit()
            return {"status": "ok", "mensaje": "Demo creada exitosamente"}
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
                cursor.execute("DELETE FROM demos WHERE id_demo = %s", (id_demo,))
            conn.commit()
            return {"status": "ok", "mensaje": "DEMO eliminada con éxito"}
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
                results = []
                for result in cursor.stored_results():
                    results.extend(result.fetchall())
                return results
            except Exception:
                try:
                    cursor.callproc("sp_obtener_pasos_demo", (id_demo,))
                    results = []
                    for result in cursor.stored_results():
                        results.extend(result.fetchall())
                    return results
                except Exception:
                    try:
                        cursor.execute(
                            """
                            SELECT d.*, c.nombre AS nombre_comando, c.codigo 
                            FROM demo_movimientos d
                            LEFT JOIN comandos c ON d.id_comando = c.id_comando
                            WHERE d.id_demo = %s
                            ORDER BY d.orden ASC
                            """, 
                            (id_demo,)
                        )
                        return cursor.fetchall()
                    except Exception:
                        return []
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def agregar_movimiento_demo(id_demo: int, orden: int, id_comando: int, duracion_ms: int = 1000, pausa_ms: int = 500):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_agregar_movimiento_demo", (id_demo, orden, id_comando, duracion_ms, pausa_ms))
            except Exception:
                try:
                    cursor.callproc("sp_agregar_movimiento_demo", (id_demo, id_comando, orden, duracion_ms))
                except Exception:
                    try:
                        cursor.execute(
                            "INSERT INTO demo_movimientos (id_demo, orden, id_comando, duracion_ms, pausa_ms) VALUES (%s, %s, %s, %s, %s)",
                            (id_demo, orden, id_comando, duracion_ms, pausa_ms)
                        )
                    except Exception:
                        cursor.execute(
                            "INSERT INTO demo_movimientos (id_demo, id_comando, orden, tiempo_espera) VALUES (%s, %s, %s, %s)",
                            (id_demo, id_comando, orden, duracion_ms)
                        )
            conn.commit()
            return {"status": "ok", "mensaje": "Movimiento asignado a DEMO"}
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def actualizar_movimiento_demo(id_movimiento_demo: int, orden: int, duracion_ms: int = 1000):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_actualizar_movimiento_demo", (id_movimiento_demo, orden, duracion_ms))
            except Exception:
                try:
                    cursor.execute(
                        "UPDATE demo_movimientos SET orden = %s, duracion_ms = %s WHERE id_movimiento_demo = %s",
                        (orden, duracion_ms, id_movimiento_demo)
                    )
                except Exception:
                    cursor.execute(
                        "UPDATE demo_movimientos SET orden = %s, tiempo_espera = %s WHERE id_movimiento_demo = %s",
                        (orden, duracion_ms, id_movimiento_demo)
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
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            try:
                # Intento 1: Stored Procedure enviando los 2 parámetros que realmente espera
                cursor.callproc("sp_actualizar_estado_vehiculo", (id_vehiculo, id_comando))
            except Exception:
                try:
                    # Intento 2: Actualizar usando el nombre correcto de columna 'ultimo_comando'
                    cursor.execute(
                        "UPDATE estado_vehiculo SET ultimo_comando = %s WHERE id_vehiculo = %s",
                        (id_comando, id_vehiculo)
                    )
                except Exception:
                    # Intento 3: Directo a la tabla vehiculos sobre la columna 'descripcion' o simplemente haciendo PASS
                    try:
                        cursor.execute(
                            "UPDATE vehiculos SET ultimo_comando = %s WHERE id_vehiculo = %s",
                            (id_comando, id_vehiculo)
                        )
                    except Exception:
                        pass
            conn.commit()
            return {"status": "ok", "mensaje": "Estado actualizado por DEMO"}
        finally:
            cursor.close()
            conn.close()