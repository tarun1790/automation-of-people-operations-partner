import asyncio
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from backend.app.config import APP_NAME, APP_VERSION, API_PREFIX, DEVICE, CUDA_AVAILABLE, GPU_NAME, FRAMEWORK_META
from backend.app.database import engine, Base, SessionLocal
from backend.app.services.seed_data import populate_database_if_empty
from backend.app.services.sentinel_daemon import sentinel_daemon
from backend.app.services.ws_manager import ws_manager
from backend.app.routes import (
    dashboard_router,
    simulation_router,
    action_router,
    talent_router,
    employee_router,
    policy_router,
    auth_router,
    agent_router
)

# Initialize database schema
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        populate_database_if_empty(db)
    finally:
        db.close()
    sentinel_daemon.start()
    yield
    sentinel_daemon.stop()

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Atlas — Autonomous People Operations Partner platform unifying workforce intelligence, predictive risk modeling, and automated workflows.",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(dashboard_router, prefix=API_PREFIX)
app.include_router(simulation_router, prefix=API_PREFIX)
app.include_router(action_router, prefix=API_PREFIX)
app.include_router(talent_router, prefix=API_PREFIX)
app.include_router(employee_router, prefix=API_PREFIX)
app.include_router(policy_router, prefix=API_PREFIX)
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(agent_router, prefix=API_PREFIX)

# Static and UI Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = BASE_DIR / "frontend" / "static"
TEMPLATE_DIR = BASE_DIR / "frontend" / "templates"

STATIC_DIR.mkdir(parents=True, exist_ok=True)
TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    # Send initial connection handshake
    await websocket.send_json({
        "type": "handshake",
        "status": "connected",
        "system": APP_NAME,
        "device": GPU_NAME if CUDA_AVAILABLE else "CPU",
        "cuda_active": CUDA_AVAILABLE,
        "message": "Atlas Real-Time Live Stream Connected"
    })
    try:
        while True:
            try:
                # Wait for client heartbeat or ping
                data = await asyncio.wait_for(websocket.receive_text(), timeout=4.0)
                if data == "ping":
                    await websocket.send_json({"type": "pong"})
            except asyncio.TimeoutError:
                # Push periodic live telemetry heartbeat
                await websocket.send_json({
                    "type": "heartbeat",
                    "status": "live",
                    "sentinel_active": sentinel_daemon.is_running
                })
    except (WebSocketDisconnect, Exception):
        ws_manager.disconnect(websocket)

@app.get("/", response_class=HTMLResponse)
def serve_index():
    index_file = TEMPLATE_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("<h2>Atlas is initializing...</h2>")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app_name": APP_NAME,
        "version": APP_VERSION,
        "hardware_acceleration": {
            "device": str(DEVICE),
            "cuda_available": CUDA_AVAILABLE,
            "gpu_name": GPU_NAME
        },
        "academic_grounding": FRAMEWORK_META
    }
