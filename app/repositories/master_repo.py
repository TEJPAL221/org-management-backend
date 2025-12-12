from typing import Optional
from bson import ObjectId
from datetime import datetime
from pymongo import ReturnDocument


class MasterRepository:
    def __init__(self, db):
        self.db = db
        self.org_coll = db.get_collection("organizations")
        self.admin_coll = db.get_collection("admins")

    # --------------------------
    # ORGANIZATION METHODS
    # --------------------------

    async def find_org_by_name(self, name: str) -> Optional[dict]:
        return await self.org_coll.find_one({"organization_name": name})

    async def create_org(self, organization_name: str, collection_name: str, admin_id: ObjectId) -> dict:
        doc = {
            "organization_name": organization_name,
            "collection_name": collection_name,
            "admin_id": admin_id,
            "created_at": datetime.utcnow(),
        }
        res = await self.org_coll.insert_one(doc)
        return await self.org_coll.find_one({"_id": res.inserted_id})

    async def update_org(self, organization_name: str, updates: dict) -> Optional[dict]:
        """
        Update the organization metadata and return the updated document.
        """
        updated = await self.org_coll.find_one_and_update(
            {"organization_name": organization_name},
            {"$set": updates},
            return_document=ReturnDocument.AFTER
        )
        return updated

    async def delete_org(self, organization_name: str) -> bool:
        res = await self.org_coll.delete_one({"organization_name": organization_name})
        return res.deleted_count == 1

    # --------------------------
    # ADMIN METHODS
    # --------------------------

    async def create_admin(self, email: str, password_hash: str, organization_id: ObjectId) -> dict:
        doc = {
            "email": email,
            "password_hash": password_hash,
            "organization_id": organization_id,
            "role": "admin",
            "created_at": datetime.utcnow(),
        }
        res = await self.admin_coll.insert_one(doc)
        return await self.admin_coll.find_one({"_id": res.inserted_id})

    async def find_admin_by_email(self, email: str) -> Optional[dict]:
        return await self.admin_coll.find_one({"email": email})

    async def get_admin(self, admin_id: str) -> Optional[dict]:
        try:
            _id = ObjectId(admin_id)
        except:
            return None
        return await self.admin_coll.find_one({"_id": _id})

    async def delete_admin(self, admin_id):
        try:
            admin_id = ObjectId(admin_id)
        except:
            return False
        res = await self.admin_coll.delete_one({"_id": admin_id})
        return res.deleted_count == 1
