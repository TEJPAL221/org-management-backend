# app/core/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .security import decode_access_token
from ..db import get_db
from ..repositories.master_repo import MasterRepository
from bson import ObjectId

security_scheme = HTTPBearer()


async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    token = credentials.credentials

    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    admin_id = payload.get("sub")
    org_id = payload.get("org_id")

    db = get_db()
    repo = MasterRepository(db)

    # ---------------------------------------------------
    # FIX: Support both ObjectId and string IDs (FakeDB)
    # ---------------------------------------------------
    admin = None

    # Try ObjectId lookup first
    try:
        admin_oid = ObjectId(admin_id)
        admin = await repo.admin_coll.find_one({"_id": admin_oid})
    except Exception:
        pass

    # If not found, try plain string match (_id stored as string in FakeDB)
    if admin is None:
        admin = await repo.admin_coll.find_one({"_id": admin_id})

    if not admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin not found")

    # ---------------------------------------------------
    # FIX: organization_id may be ObjectId or string
    # ---------------------------------------------------
    if str(admin.get("organization_id")) != str(org_id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin organization mismatch")

    return admin
