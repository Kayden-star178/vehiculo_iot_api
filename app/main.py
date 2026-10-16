import asyncio
from datetime import datetime
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from app.repositories import VehiculoRepository
from app.websocket_manager import manager

app = FastAPI(
    title="API Vehículo IoT",
    description="API REST y WebSocket para monitoreo y control local del vehículo IoT integrando 21 Stored Procedures.",
    version="1.0.0"
)

class MovimientoSchema(BaseModel):
    id_vehiculo: int
    id_comando: int
    origen: str = "MANUAL"

class DemoEjecutarSchema(BaseModel):
    id_vehiculo: int
    id_demo: int

# --- ENDPOINT: WEBSOCKET ---
@app.websocket("/ws/{id_vehiculo}")
async def websocket_endpoint(websocket: WebSocket, id_vehiculo: int):
    await manager.connect(websocket, id_vehiculo)
    try:
        while True:
            # Mantener la conexión abierta escuchando mensajes entrantes
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, id_vehiculo)


# --- ENDPOINT: MOVIMIENTO INDIVIDUAL (POST) ---
@app.post("/api/movimiento", summary="Registra un movimiento individual (Actualiza estado e historial)")
async def ejecutar_movimiento(data: MovimientoSchema):
    vehiculo = VehiculoRepository.obtener_vehiculo(data.id_vehiculo)
    
    # Validar existencia del vehículo
    if not vehiculo:
        raise HTTPException(status_code=400, detail="Vehículo no encontrado")
        
    # Validar campo 'activo' contemplando booleanos, enteros, strings o bytes de MySQL
    activo_val = vehiculo.get("activo")
    is_activo = activo_val in (1, True, "1", b'\x01') or str(activo_val) in ("1", "True")

    if not is_activo:
        raise HTTPException(status_code=400, detail="Vehículo inactivo")

    # Transacción atómica en BD: sp_actualizar_estado + sp_registrar_historial
    VehiculoRepository.ejecutar_movimiento_transaccion(data.id_vehiculo, data.id_comando, data.origen)
    
    # Notificación vía WebSocket
    evento = {
        "tipo": "MOVIMIENTO_INDIVIDUAL",
        "id_vehiculo": data.id_vehiculo,
        "id_comando": data.id_comando,
        "timestamp": datetime.utcnow().isoformat()
    }
    await manager.broadcast(data.id_vehiculo, evento)
    
    return {"status": "ok", "mensaje": "Movimiento registrado con éxito"}

# --- ENDPOINT: OBTENER HISTORIAL (GET) ---
@app.get("/api/historial/{id_vehiculo}", summary="Obtiene el historial de comandos de un vehículo")
async def obtener_historial(id_vehiculo: int):
    historial = VehiculoRepository.obtener_historial_reciente(id_vehiculo)
    return {"status": "ok", "historial": historial}


# --- ENDPOINT: EJECUTAR DEMO (POST VIA WEBSOCKET SIN REGLA DE HISTORIAL) ---
@app.post("/api/demo/ejecutar", summary="Ejecuta una secuencia DEMO por WebSocket sin guardar en historial")
async def ejecutar_demo(data: DemoEjecutarSchema):
    if manager.active_demos.get(data.id_vehiculo, False):
        raise HTTPException(status_code=409, detail="Ya existe una DEMO en ejecución para este vehículo")

    movimientos = VehiculoRepository.obtener_movimientos_demo(data.id_demo)
    if not movimientos:
        raise HTTPException(status_code=44, detail="No se encontraron movimientos para esta DEMO")

    async def correr_demo():
        manager.active_demos[data.id_vehiculo] = True
        try:
            await manager.broadcast(data.id_vehiculo, {"tipo": "DEMO_INICIO", "id_demo": data.id_demo})
            
            for mov in movimientos:
                if not manager.active_demos.get(data.id_vehiculo, False):
                    break # Permite cancelación

                # 1. Actualizar estado en RDS (SIN registrar historial)
                VehiculoRepository.actualizar_estado_demo(data.id_vehiculo, mov['id_comando'])
                
                # 2. Transmitir evento por WebSocket
                await manager.broadcast(data.id_vehiculo, {
                    "tipo": "DEMO_MOVIMIENTO",
                    "orden": mov['orden'],
                    "comando": mov['comando'],
                    "codigo": mov['codigo'],
                    "duracion_ms": mov['duracion_ms'],
                    "pausa_ms": mov['pausa_ms']
                })
                
                # Respetar duracion_ms y pausa_ms
                await asyncio.sleep((mov['duracion_ms'] + mov['pausa_ms']) / 1000.0)

            await manager.broadcast(data.id_vehiculo, {"tipo": "DEMO_FIN", "id_demo": data.id_demo})
        finally:
            manager.active_demos[data.id_vehiculo] = False

    asyncio.create_task(correr_demo())
    return {"status": "ok", "mensaje": "Secuencia DEMO iniciada"}