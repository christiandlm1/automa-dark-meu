"""
AUTOMA Backend - FastAPI Entry Point
Sets up middleware, lifespan events, health checks, REST routes, and WebSocket endpoints.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import settings
settings.ensure_directories()
from database import init_db, close_db, get_db
from routes import api_router
from services.hardware_service import HardwareService

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(settings.LOGS_DIR / "backend.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("automa")


# --- WebSocket Manager ---
class ConnectionManager:
    """Manages active WebSocket connections for real-time telemetry."""

    def __init__(self) -> None:
        self.active_connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket client connected. Active: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket client disconnected. Active: {len(self.active_connections)}")

    async def broadcast(self, message: dict) -> None:
        """Send message to all connected clients, pruning dead connections."""
        if not self.active_connections:
            return
        
        dead = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead.append(connection)
                
        for connection in dead:
            self.disconnect(connection)


ws_manager = ConnectionManager()


processing_ws_manager = ConnectionManager()


async def ws_processing_broadcast(status_data: dict) -> None:
    """Send processing status update to all connected processing clients."""
    await processing_ws_manager.broadcast({
        "type": "processing_telemetry",
        "data": status_data
    })


# --- Telemetry Background Task ---
async def hardware_monitor_task() -> None:
    """Background loop that collects and broadcasts hardware telemetry."""
    # Since we need a DB session for hardware, we will resolve it on every check or skip writing it
    # We will instantiate a temporary session using the async_session_maker
    from database import async_session_maker
    
    logger.info("Starting hardware monitoring telemetry loop.")
    try:
        while True:
            async with async_session_maker() as session:
                hw_service = HardwareService(session)
                try:
                    snapshot = await hw_service.get_realtime_snapshot()
                    message = {
                        "type": "hardware_telemetry",
                        "data": snapshot.model_dump(mode="json"),
                    }
                    await ws_manager.broadcast(message)
                except Exception as e:
                    logger.error(f"Error in hardware telemetry capture: {e}")
                    
            await asyncio.sleep(settings.HARDWARE_MONITOR_INTERVAL)
    except asyncio.CancelledError:
        logger.info("Hardware monitoring loop canceled.")


# --- Lifespan Context Manager ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure folder structure is present
    settings.ensure_directories()
    
    # Initialize SQLite Database tables
    logger.info("Initializing SQLite database tables...")
    await init_db()
    
    # Seed default database settings
    from database import async_session_maker
    from services.settings_service import SettingsService
    logger.info("Seeding default settings...")
    async with async_session_maker() as session:
        settings_service = SettingsService(session)
        await settings_service.seed_defaults()
        await session.commit()
    
    # Initialize and start the Processing Engine
    from processing.engine.processing_service import processing_service
    processing_service.status_callback = ws_processing_broadcast
    await processing_service.start()
    
    # Spawn background task for telemetry
    app.state.monitor_task = asyncio.create_task(hardware_monitor_task())
    logger.info("AUTOMA backend started successfully.")
    
    yield
    
    # Shutdown logic
    logger.info("Stopping AUTOMA backend services...")
    app.state.monitor_task.cancel()
    try:
        await app.state.monitor_task
    except asyncio.CancelledError:
        pass
        
    # Stop processing service
    from processing.engine.processing_service import processing_service
    await processing_service.stop()
    
    await close_db()
    logger.info("AUTOMA backend stopped.")


# --- FastAPI Instance ---
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    debug=settings.DEBUG,
)

# CORS configuration to allow local web and electron requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_origin_regex=r"http://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static Files serving for video thumbnails
app.mount("/thumbnails", StaticFiles(directory=settings.THUMBNAILS_DIR), name="thumbnails")

# Static Files serving for preview caching
app.mount("/cache", StaticFiles(directory=str(settings.CACHE_DIR)), name="cache")

# Include all REST API endpoints
app.include_router(api_router, prefix="/api")


# --- General Endpoints ---
@app.get("/health", tags=["system"])
async def health_check():
    """Simple health check endpoint for Electron main process to poll."""
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}


# --- WebSocket Endpoints ---
@app.websocket("/ws/hardware")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket route for real-time system performance telemetry."""
    await ws_manager.connect(websocket)
    try:
        while True:
            # We keep the connection alive, ignoring any incoming payload
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket connection error: {e}")
        ws_manager.disconnect(websocket)


@app.websocket("/ws/processing")
async def websocket_processing_endpoint(websocket: WebSocket):
    """WebSocket route for real-time video processing status."""
    await processing_ws_manager.connect(websocket)
    try:
        # Broadcast immediately upon connection to send initial state
        from processing.engine.processing_service import processing_service
        await processing_service.broadcast_status()
        
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        processing_ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Processing WebSocket connection error: {e}")
        processing_ws_manager.disconnect(websocket)


# --- Standalone Runner ---
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
