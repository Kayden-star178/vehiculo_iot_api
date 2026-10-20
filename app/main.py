import asyncio
from datetime import datetime
from typing import Optional, Union
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from app.repositories import VehiculoRepository
from app.websocket_manager import manager


app = FastAPI(
    title="API Vehículo IoT",
    description="API REST y WebSocket seguro (WSS) para control y monitoreo en tiempo real del vehículo IoT.",
    version="1.0.0"
)

# =============================================================
# ESQUEMAS PYDANTIC (Modelos de entrada)
# =============================================================
class VehiculoCrearSchema(BaseModel):
    nombre: str
    descripcion: str
    activo: Optional[int] = 1

class VehiculoActualizarSchema(BaseModel):
    nombre: str
    descripcion: str
    activo: int

class ComandoSchema(BaseModel):
    id_vehiculo: Optional[int] = 0
    nombre: str
    codigo: Union[str, int]
    descripcion: Optional[str] = ""
    activo: Optional[int] = 1

class DemoSchema(BaseModel):
    id_vehiculo: Optional[int] = 1
    nombre: str
    descripcion: Optional[str] = ""

class MovimientoDemoSchema(BaseModel):
    id_demo: int
    orden: int
    id_comando: int
    duracion_ms: Optional[int] = 1000
    pausa_ms: Optional[int] = 500

class MovimientoSchema(BaseModel):
    id_vehiculo: int
    id_comando: int
    origen: Optional[str] = "API"
    duracion_ms: Optional[int] = 1000
    pausa_ms: Optional[int] = 500

class DemoEjecutarSchema(BaseModel):
    id_vehiculo: int
    id_demo: int


# Reconstruir todos los modelos explícitamente para OpenAPI/Swagger UI
VehiculoCrearSchema.model_rebuild()
VehiculoActualizarSchema.model_rebuild()
ComandoSchema.model_rebuild()
DemoSchema.model_rebuild()
MovimientoDemoSchema.model_rebuild()
MovimientoSchema.model_rebuild()
DemoEjecutarSchema.model_rebuild()

# =============================================================
# ENDPOINT WEBSOCKET (Soporte WSS)
# =============================================================
@app.websocket("/ws/{id_vehiculo}")
async def websocket_endpoint(websocket: WebSocket, id_vehiculo: int):
    await manager.connect(websocket, id_vehiculo)
    
    ultimo_estado = VehiculoRepository.obtener_ultimo_estado(id_vehiculo)
    if ultimo_estado:
        await websocket.send_json({
            "tipo": "ESTADO_INICIAL",
            "id_vehiculo": id_vehiculo,
            "estado": ultimo_estado
        })
        
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, id_vehiculo)


# =============================================================
# 1. RUTAS REST: VEHÍCULOS (5 SP)
# =============================================================
@app.get("/api/vehiculos", tags=["Vehículos"], summary="Obtener todos los vehículos")
def obtener_vehiculos():
    return {"status": "ok", "data": VehiculoRepository.obtener_vehiculos()}

@app.get("/api/vehiculos/{id_vehiculo}", tags=["Vehículos"], summary="Obtener vehículo por ID")
def obtener_vehiculo(id_vehiculo: int):
    v = VehiculoRepository.obtener_vehiculo(id_vehiculo)
    if not v:
        raise HTTPException(status_code=404, detail="Vehículo no encontrado")
    return {"status": "ok", "data": v}

@app.post("/api/vehiculos", tags=["Vehículos"], summary="Crear un nuevo vehículo")
def crear_vehiculo(data: VehiculoCrearSchema):
    VehiculoRepository.crear_vehiculo(data.nombre, data.descripcion, data.activo)
    return {"status": "ok", "mensaje": "Vehículo creado con éxito"}

@app.put("/api/vehiculos/{id_vehiculo}", tags=["Vehículos"], summary="Actualizar vehículo")
def actualizar_vehiculo(id_vehiculo: int, data: VehiculoActualizarSchema):
    VehiculoRepository.actualizar_vehiculo(id_vehiculo, data.nombre, data.descripcion, data.activo)
    return {"status": "ok", "mensaje": "Vehículo actualizado con éxito"}

@app.delete("/api/vehiculos/{id_vehiculo}", tags=["Vehículos"], summary="Eliminar vehículo")
def eliminar_vehiculo(id_vehiculo: int):
    VehiculoRepository.eliminar_vehiculo(id_vehiculo)
    return {"status": "ok", "mensaje": "Vehículo eliminado con éxito"}


# =============================================================
# 2. RUTAS REST: COMANDOS (4 SP)
# =============================================================
@app.get("/api/comandos", tags=["Comandos"], summary="Obtener lista de comandos")
def obtener_comandos():
    return {"status": "ok", "data": VehiculoRepository.obtener_comandos()}

@app.get("/api/comandos/{id_comando}", tags=["Comandos"], summary="Obtener comando por ID")
def obtener_comando(id_comando: int):
    cmd = VehiculoRepository.obtener_comando(id_comando)
    if not cmd:
        raise HTTPException(status_code=404, detail="Comando no encontrado")
    return {"status": "ok", "data": cmd}

@app.post("/api/comandos", tags=["Comandos"], summary="Crear nuevo comando")
def crear_comando_api(data: ComandoSchema):
    return VehiculoRepository.crear_comando(
        nombre=data.nombre,
        codigo=data.codigo,
        descripcion=data.descripcion or "",
        id_vehiculo=getattr(data, "id_vehiculo", 0),
        activo=getattr(data, "activo", 1)
    )

@app.put("/api/comandos/{id_comando}", tags=["Comandos"], summary="Actualizar comando existente")
def actualizar_comando(id_comando: int, data: ComandoSchema):
    return VehiculoRepository.actualizar_comando(
        id_comando=id_comando,
        nombre=data.nombre,
        codigo=data.codigo,
        descripcion=data.descripcion or "",
        id_vehiculo=getattr(data, "id_vehiculo", 1),
        activo=getattr(data, "activo", 1)
    )


# =============================================================
# 3. RUTAS REST: ESTADO Y MOVIMIENTO INDIVIDUAL (2 SP + TRANSACCIÓN)
# =============================================================
@app.get("/api/estado/{id_vehiculo}", tags=["Estado"], summary="Obtener el último estado de un vehículo")
def obtener_estado(id_vehiculo: int):
    estado = VehiculoRepository.obtener_ultimo_estado(id_vehiculo)
    if not estado:
        raise HTTPException(status_code=404, detail="Estado no encontrado")
    return {"status": "ok", "data": estado}

@app.post("/api/movimiento", tags=["Movimientos"], summary="Registra un movimiento individual (Actualiza estado e historial)")
async def ejecutar_movimiento(data: MovimientoSchema):
    vehiculo = VehiculoRepository.obtener_vehiculo(data.id_vehiculo)
    if not vehiculo:
        raise HTTPException(status_code=400, detail="Vehículo no encontrado")
        
    activo_val = vehiculo.get("activo")
    is_activo = activo_val in (1, True, "1", b'\x01') or str(activo_val) in ("1", "True")

    if not is_activo:
        raise HTTPException(status_code=400, detail="Vehículo inactivo")

    origen_val = data.origen if data.origen else "API"
    VehiculoRepository.ejecutar_movimiento_transaccion(data.id_vehiculo, data.id_comando, origen_val)
    
    evento = {
        "tipo": "MOVIMIENTO_INDIVIDUAL",
        "id_vehiculo": data.id_vehiculo,
        "id_comando": data.id_comando,
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.broadcast(data.id_vehiculo, evento)
    
    return {"status": "ok", "mensaje": "Movimiento registrado con éxito"}


# =============================================================
# 4. RUTAS REST: HISTORIAL (2 SP)
# =============================================================
@app.get("/api/historial/{id_vehiculo}", tags=["Historial"], summary="Obtiene los últimos 10 comandos del historial")
def obtener_historial(id_vehiculo: int, limite: int = 10):
    historial = VehiculoRepository.obtener_historial_reciente(id_vehiculo, limite)
    return {"status": "ok", "historial": historial}


# =============================================================
# 5 y 6. RUTAS REST Y LOGICA: DEMO Y MOVIMIENTOS DEMO (8 SP)
# =============================================================
@app.get("/api/demos", tags=["DEMO"], summary="Obtener catálogo de DEMOs")
def obtener_demos():
    return {"status": "ok", "data": VehiculoRepository.obtener_demos()}

@app.get("/api/demos/{id_demo}", tags=["DEMO"], summary="Obtener DEMO por ID")
def obtener_demo(id_demo: int):
    d = VehiculoRepository.obtener_demo(id_demo)
    if not d:
        raise HTTPException(status_code=404, detail="DEMO no encontrada")
    return {"status": "ok", "data": d}

@app.post("/api/demos", tags=["DEMO"], summary="Crear una DEMO")
def crear_demo(data: DemoSchema):
    VehiculoRepository.crear_demo(
        nombre=data.nombre,
        descripcion=data.descripcion or "",
        id_vehiculo=getattr(data, "id_vehiculo", 1)
    )
    return {"status": "ok", "mensaje": "DEMO creada con éxito"}

@app.delete("/api/demos/{id_demo}", tags=["DEMO"], summary="Eliminar una DEMO")
def eliminar_demo(id_demo: int):
    VehiculoRepository.eliminar_demo(id_demo)
    return {"status": "ok", "mensaje": "DEMO eliminada con éxito"}

@app.get("/api/demos/{id_demo}/movimientos", tags=["DEMO Movimientos"], summary="Obtener pasos de una DEMO")
def obtener_movimientos_demo(id_demo: int):
    return {"status": "ok", "data": VehiculoRepository.obtener_movimientos_demo(id_demo)}

@app.post("/api/demos/movimientos", tags=["DEMO Movimientos"], summary="Agregar paso a una DEMO")
def agregar_movimiento_demo(data: MovimientoDemoSchema):
    VehiculoRepository.agregar_movimiento_demo(
        id_demo=data.id_demo,
        orden=data.orden,
        id_comando=data.id_comando,
        duracion_ms=data.duracion_ms or 1000,
        pausa_ms=data.pausa_ms or 500
    )
    return {"status": "ok", "mensaje": "Paso agregado a la DEMO"}

@app.put("/api/demos/movimientos/{id_movimiento_demo}", tags=["DEMO Movimientos"], summary="Actualizar paso de DEMO")
def actualizar_movimiento_demo(id_movimiento_demo: int, data: MovimientoDemoSchema):
    VehiculoRepository.actualizar_movimiento_demo(
        id_movimiento_demo=id_movimiento_demo,
        orden=data.orden,
        duracion_ms=data.duracion_ms or 1000
    )
    return {"status": "ok", "mensaje": "Paso actualizado"}

@app.delete("/api/demos/movimientos/{id_movimiento_demo}", tags=["DEMO Movimientos"], summary="Eliminar paso de DEMO")
def eliminar_movimiento_demo(id_movimiento_demo: int):
    VehiculoRepository.eliminar_movimiento_demo(id_movimiento_demo)
    return {"status": "ok", "mensaje": "Paso eliminado"}

# --- EJECUCIÓN DE DEMO EN TIEMPO REAL (REGLA: SIN GUARDAR EN HISTORIAL) ---
@app.post("/api/demo/ejecutar", tags=["DEMO Control"], summary="Ejecuta una secuencia DEMO por WebSocket sin guardar en historial")
async def ejecutar_demo(data: DemoEjecutarSchema):
    if manager.active_demos.get(data.id_vehiculo, False):
        raise HTTPException(status_code=409, detail="Ya existe una DEMO en ejecución para este vehículo")

    movimientos = VehiculoRepository.obtener_movimientos_demo(data.id_demo)
    if not movimientos:
        raise HTTPException(status_code=404, detail="No se encontraron movimientos para esta DEMO")

    async def correr_demo():
        manager.active_demos[data.id_vehiculo] = True
        try:
            await manager.broadcast(data.id_vehiculo, {"tipo": "DEMO_INICIO", "id_demo": data.id_demo})
            
            for mov in movimientos:
                if not manager.active_demos.get(data.id_vehiculo, False):
                    break
                
                # 1. Actualizar estado en RDS (Sin registrar en historial)
                VehiculoRepository.actualizar_estado_demo(data.id_vehiculo, mov['id_comando'])
                
                # 2. Transmitir paso por WSS
                await manager.broadcast(data.id_vehiculo, {
                    "tipo": "DEMO_MOVIMIENTO",
                    "orden": mov.get('orden'),
                    "id_comando": mov.get('id_comando'),
                    "duracion_ms": mov.get('duracion_ms', 1000),
                    "pausa_ms": mov.get('pausa_ms', 500)
                })
                
                duracion = mov.get('duracion_ms', 1000) / 1000.0
                pausa = mov.get('pausa_ms', 500) / 1000.0
                await asyncio.sleep(duracion + pausa)

            await manager.broadcast(data.id_vehiculo, {"tipo": "DEMO_FIN", "id_demo": data.id_demo})
        finally:
            manager.active_demos[data.id_vehiculo] = False

    asyncio.create_task(correr_demo())
    return {"status": "ok", "mensaje": "Secuencia DEMO iniciada exitosamente"}