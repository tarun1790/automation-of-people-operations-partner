from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from backend.app.config import APP_NAME, APP_VERSION, API_PREFIX, DEVICE, CUDA_AVAILABLE, GPU_NAME, FRAMEWORK_META
from backend.app.database import engine, Base, SessionLocal
from backend.app.services.seed_data import populate_database_if_empty
from backend.app.services.sentinel_daemon import sentinel_daemon
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

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Enterprise-grade AI workforce intelligence and decision platform that unifies heterogeneous HR data into an explainable reasoning and counterfactual simulation layer."
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

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        populate_database_if_empty(db)
    finally:
        db.close()
    sentinel_daemon.start()

@app.on_event("shutdown")
def shutdown_event():
    sentinel_daemon.stop()

@app.get("/", response_class=HTMLResponse)
def serve_index():
    index_file = TEMPLATE_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return HTMLResponse("<h2>WorkSight AI is initializing...</h2>")

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
