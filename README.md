# 🚗 API Backend IoT - Control y Monitoreo de Vehículo

API REST desarrollada en **Python (FastAPI)** con arquitectura orientada a objetos y comunicación bidireccional en tiempo real mediante **WebSockets seguros (WSS)**. El sistema se encuentra desplegado en un entorno de producción en la nube de **AWS**, utilizando una instancia en **Amazon EC2** conectada a una base de datos relacional en **Amazon RDS for MySQL** y un proxy inverso **Caddy** para la gestión de certificados SSL/TLS.

---

## 🌐 Enlaces Públicos Verificables
* **Documentación Interactiva (Swagger UI / HTTPS):** `https://carrito-iot.duckdns.org/docs`
* **Canal WebSocket Seguro (WSS):** `wss://carrito-iot.duckdns.org/ws/{id_vehiculo}`

---

## 🏗️ Arquitectura del Sistema
* **Infraestructura Cloud:** AWS Amazon EC2 (Hosting backend) y Amazon RDS (Base de datos MySQL).
* **Seguridad y Red:** Caddy Server como proxy inverso para habilitar protocolos seguros (`https://` y `wss://`).
* **Diseño del Software:** Patrón de Programación Orientada a Objetos (POO), separación modular en capas (Rutas, Repositorios y Modelos) y lógica de negocio basada en **21 Procedimientos Almacenados (Stored Procedures)** en la base de datos.

---

## 🛠️ Resumen de Módulos y Procedimientos Almacenados (21 SPs)
1. **Vehículos (5 SPs):** Creación, consulta general, consulta por ID, actualización y eliminación de unidades.
2. **Comandos (4 SPs):** Gestión y registro operativo de los comandos ejecutables por el vehículo.
3. **Estado y Movimientos (2 SPs + Transacción):** Actualización síncrona del estado actual del vehículo y registro persistente en la tabla de historial individual.
4. **Historial (2 SPs):** Consulta optimizada de los movimientos recientes del vehículo ordenados de forma descendente.
5. **DEMOs y Movimientos de DEMO (8 SPs):** Catálogo de secuencias de demostración, administración de pasos temporizados y ejecución asíncrona mediante tareas concurrentes (`asyncio`).

---

## 🔌 Documentación de WebSockets (WSS) y Mensajes JSON

Las conexiones en tiempo real se realizan a través de canales seguros especificando el identificador del vehículo:
```text
wss://carrito-iot.duckdns.org/ws/{id_vehiculo}

Estructura de Eventos Transmitidos:
1. Estado Inicial (ESTADO_INICIAL)
Cuándo se emite: Inmediatamente al establecer con éxito la conexión WebSocket con el servidor.

Estructura JSON:

JSON
{
  "tipo": "ESTADO_INICIAL",
  "id_vehiculo": 4,
  "estado": {
    "id_vehiculo": 4,
    "ultimo_comando": 1
  }
}

2. Movimiento Individual (MOVIMIENTO_INDIVIDUAL)
Cuándo se emite: Al procesar una petición HTTP POST /api/movimiento (actualiza estado e historial simultáneamente).

Estructura JSON:

JSON
{
  "tipo": "MOVIMIENTO_INDIVIDUAL",
  "id_vehiculo": 4,
  "id_comando": 1,
  "timestamp": "2026-10-21T06:50:27.932Z"
}

3. Inicio de DEMO (DEMO_INICIO)
Cuándo se emite: Al activar una secuencia automatizada mediante POST /api/demo/ejecutar.

Estructura JSON:

JSON
{
  "tipo": "DEMO_INICIO",
  "id_demo": 10
}


4. Movimiento de DEMO (DEMO_MOVIMIENTO)
Cuándo se emite: Paso a paso durante la ejecución de la demo. Actualiza el estado actual en RDS sin contaminar el historial individual.

Estructura JSON:

JSON
{
  "tipo": "DEMO_MOVIMIENTO",
  "orden": 1,
  "id_comando": 2,
  "duracion_ms": 1000,
  "pausa_ms": 500
}


5. Fin de DEMO (DEMO_FIN)
Cuándo se emite: Al concluir de forma exitosa todos los pasos programados de la secuencia demostrativa.

Estructura JSON:

JSON
{
  "tipo": "DEMO_FIN",
  "id_demo": 10
}

***

<ElicitationsGroup/>