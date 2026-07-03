from fastapi import APIRouter
from app.api.v1.endpoints import health, sessions, tool_calls, baselines, alerts, agent, baseline_train

api_router = APIRouter()

# Register sub-routers
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["Sessions"])
api_router.include_router(tool_calls.router, prefix="/tool-calls", tags=["Tool Calls"])
api_router.include_router(baselines.router, prefix="/baselines", tags=["Baselines"])
api_router.include_router(baseline_train.router, prefix="/baseline", tags=["Baseline Training"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
api_router.include_router(agent.router, prefix="/agent", tags=["Agent"])

