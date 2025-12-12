from bson import ObjectId
from ..repositories.master_repo import MasterRepository
from ..core import security


class AuthService:
    def __init__(self, db):
        self.repo = MasterRepository(db)

    async def login(self, email: str, password: str):
        admin = await self.repo.find_admin_by_email(email)
        if not admin:
            return None
        if not security.verify_password(password, admin["password_hash"]):
            return None
        token = security.create_access_token(subject=str(admin["_id"]), org_id=str(admin["organization_id"]))
        return {"access_token": token, "token_type": "bearer"}
