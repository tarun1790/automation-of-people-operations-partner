from backend.app.routes.dashboard_routes import router as dashboard_router
from backend.app.routes.simulation_routes import router as simulation_router
from backend.app.routes.action_routes import router as action_router
from backend.app.routes.talent_routes import router as talent_router
from backend.app.routes.employee_routes import router as employee_router
from backend.app.routes.policy_routes import router as policy_router
from backend.app.routes.auth_routes import router as auth_router

__all__ = [
    "dashboard_router",
    "simulation_router",
    "action_router",
    "talent_router",
    "employee_router",
    "policy_router",
    "auth_router"
]
