from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from workspace_api.api.health.router import router as health_router
from workspace_api.api.shifts.router import router as shifts_router
from workspace_api.api.messages.router import router as messages_router
from workspace_api.api.events.router import router as events_router
from workspace_api.api.corrections.router import router as corrections_router
from workspace_api.api.tasks.router import router as tasks_router
from workspace_api.api.customer_requests.router import router as customer_requests_router
from workspace_api.config import settings
from workspace_api.middleware.request_id import RequestIdMiddleware

app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(shifts_router)
app.include_router(messages_router)
app.include_router(events_router)
app.include_router(corrections_router)
app.include_router(tasks_router)
app.include_router(customer_requests_router)
