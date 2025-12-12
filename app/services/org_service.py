from bson import ObjectId
from ..repositories.master_repo import MasterRepository
from ..repositories.tenant_repo import TenantRepository
from ..core import security
import re


def slugify(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9_]+", "_", name)
    return name


class OrganizationService:
    def __init__(self, db):
        self.db = db
        self.master = MasterRepository(db)
        self.tenant = TenantRepository(db)

    async def create_organization(self, org_name: str, email: str, password: str):
        org_name_norm = org_name.strip()

        # Check if organization exists
        existing = await self.master.find_org_by_name(org_name_norm)
        if existing:
            raise ValueError("organization_exists")

        slug = slugify(org_name_norm)
        collection_name = f"org_{slug}"

        # Create the tenant collection
        await self.tenant.create_collection(collection_name)

        # OPTIONAL: Insert initial structure
        await self.db[collection_name].insert_one({"initialized": True})

        # Create admin
        pwd_hash = security.hash_password(password)
        admin_doc = await self.master.create_admin(
            email=email, password_hash=pwd_hash, organization_id=None
        )

        # Create org metadata
        org_doc = await self.master.create_org(
            organization_name=org_name_norm,
            collection_name=collection_name,
            admin_id=admin_doc["_id"]
        )

        # Update admin with org_id
        await self.master.admin_coll.update_one(
            {"_id": admin_doc["_id"]},
            {"$set": {"organization_id": org_doc["_id"]}}
        )

        return {
            "organization_name": org_doc["organization_name"],
            "collection_name": org_doc["collection_name"],
            "admin_id": str(admin_doc["_id"]),
            "created_at": org_doc["created_at"]
        }

    async def get_organization(self, org_name: str):
        return await self.master.find_org_by_name(org_name)

    async def update_organization(
        self, organization_name: str, new_organization_name: str = None,
        email: str = None, password: str = None
    ):
        org = await self.master.find_org_by_name(organization_name)
        if not org:
            raise ValueError("organization_not_found")

        updates = {}

        # Renaming organization & migrating data
        if new_organization_name:
            if await self.master.find_org_by_name(new_organization_name):
                raise ValueError("organization_name_conflict")

            old_collection = org["collection_name"]
            new_collection = f"org_{slugify(new_organization_name)}"

            # Create new tenant collection
            await self.tenant.create_collection(new_collection)

            # Copy data old → new
            await self.tenant.copy_collection(old_collection, new_collection)

            # Drop old collection
            await self.tenant.drop_collection(old_collection)

            # Update metadata
            updates["organization_name"] = new_organization_name
            updates["collection_name"] = new_collection

        # Update admin details
        if email or password:
            admin_id = org["admin_id"]
            admin_updates = {}

            if email:
                admin_updates["email"] = email
            if password:
                admin_updates["password_hash"] = security.hash_password(password)

            if admin_updates:
                await self.master.admin_coll.update_one(
                    {"_id": admin_id},
                    {"$set": admin_updates}
                )

        if updates:
            await self.master.update_org(organization_name, updates)

        return True

    async def delete_organization(self, organization_name: str, requesting_admin_id: str):
        org = await self.master.find_org_by_name(organization_name)
        if not org:
            raise ValueError("organization_not_found")

        # Only the admin of this org can delete
        if str(org["admin_id"]) != str(requesting_admin_id):
            raise PermissionError("not_authorized")

        # Drop tenant collection
        await self.tenant.drop_collection(org["collection_name"])

        # Delete admins belonging to this org
        await self.master.admin_coll.delete_many({"organization_id": org["_id"]})

        # Delete org metadata
        await self.master.delete_org(organization_name)

        return True
