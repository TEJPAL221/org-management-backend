from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class OrgCreateRequest(BaseModel):
    organization_name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)


class OrgResponse(BaseModel):
    organization_name: str
    collection_name: str
    admin_id: str
    created_at: datetime


class OrgGetRequest(BaseModel):
    organization_name: str = Field(..., min_length=2, max_length=50)


class OrgUpdateRequest(BaseModel):
    organization_name: str = Field(..., min_length=2, max_length=50)
    # allow updating admin email/password as optional
    new_organization_name: Optional[str] = Field(None, min_length=2, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)


class OrgDeleteRequest(BaseModel):
    organization_name: str = Field(..., min_length=2, max_length=50)


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
