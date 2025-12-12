# app/api/v1/org_router.py
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from ...models.pydantic_models import OrgCreateRequest, OrgUpdateRequest, OrgDeleteRequest
from ...services.org_service import OrganizationService
from ...db import get_db
from ...core.deps import get_current_admin
from ...core.security import create_access_token

router = APIRouter()

# ---------------- CREATE ORG ----------------
@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_org(payload: OrgCreateRequest, db=Depends(get_db)):
    svc = OrganizationService(db)
    try:
        res = await svc.create_organization(
            payload.organization_name,
            payload.email,
            payload.password
        )
    except ValueError as e:
        if str(e) == "organization_exists":
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Organization already exists"}
            )
        raise
    return res


# ---------------- GET ORG ----------------
@router.get("/get", status_code=status.HTTP_200_OK)
async def get_org(organization_name: str, db=Depends(get_db)):
    svc = OrganizationService(db)
    org = await svc.get_organization(organization_name)

    if not org:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Organization not found"}
        )

    org["admin_id"] = str(org["admin_id"])
    org["_id"] = str(org["_id"])
    return org


# ---------------- UPDATE ORG ----------------
@router.put("/update", status_code=status.HTTP_200_OK)
async def update_org(
    payload: OrgUpdateRequest,
    admin=Depends(get_current_admin),
    db=Depends(get_db)
):
    svc = OrganizationService(db)

    try:
        await svc.update_organization(
            payload.organization_name,
            new_organization_name=payload.new_organization_name,
            email=payload.email,
            password=payload.password
        )
    except ValueError as e:
        code = str(e)
        if code == "organization_not_found":
            return JSONResponse(status_code=404, content={"detail": "Organization not found"})
        if code == "organization_name_conflict":
            return JSONResponse(status_code=409, content={"detail": "Organization name conflict"})
        raise

    # ------------------------------------------------------------
    # IMPORTANT FIX:
    # After updating admin email/password, issue a NEW JWT token.
    # ------------------------------------------------------------
    updated_admin = await svc.master.admin_coll.find_one({"_id": admin["_id"]})
    new_token = create_access_token(
        subject=str(updated_admin["_id"]),
        org_id=str(updated_admin["organization_id"])
    )

    return {
        "detail": "Organization updated successfully",
        "access_token": new_token,
        "token_type": "bearer"
    }


# ---------------- DELETE ORG ----------------
@router.delete("/delete", status_code=status.HTTP_200_OK)
async def delete_org(
    payload: OrgDeleteRequest,
    admin=Depends(get_current_admin),
    db=Depends(get_db)
):
    svc = OrganizationService(db)

    try:
        await svc.delete_organization(
            payload.organization_name,
            requesting_admin_id=str(admin["_id"])
        )
    except ValueError:
        return JSONResponse(status_code=404, content={"detail": "Organization not found"})
    except PermissionError:
        return JSONResponse(status_code=403, content={"detail": "Not authorized to delete"})

    return {"detail": "Organization deleted successfully"}
