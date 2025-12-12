from fastapi import FastAPI
from .db import get_client
from app.api.v1.admin_router import router as admin_router
from app.api.v1.org_router import router as org_router

app = FastAPI(title="Organization Management Service", version="1.0")

# include routers
app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(org_router, prefix="/org", tags=["org"])


@app.on_event("startup")
async def startup_event():
    get_client()


@app.get("/health")
async def health():
    return {"status": "ok"}
