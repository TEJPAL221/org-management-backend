# app/api/v1/admin_router.py
from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from ...models.pydantic_models import AdminLoginRequest, TokenResponse
from ...services.auth_service import AuthService
from ...db import get_db

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(payload: AdminLoginRequest, db=Depends(get_db)):
    svc = AuthService(db)
    token = await svc.login(payload.email, payload.password)

    if not token:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid credentials"}
        )

    return token
