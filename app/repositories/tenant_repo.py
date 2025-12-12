class TenantRepository:
    def __init__(self, db):
        self.db = db

    # --------------------------
    # CREATE COLLECTION
    # --------------------------
    async def create_collection(self, collection_name: str):
        """
        Create a new collection for the organization IF it does not already exist.
        """
        collections = await self.db.list_collection_names()
        if collection_name not in collections:
            await self.db.create_collection(collection_name)

    # --------------------------
    # DROP COLLECTION
    # --------------------------
    async def drop_collection(self, collection_name: str):
        """
        Drop the organization's tenant collection.
        """
        collections = await self.db.list_collection_names()
        if collection_name in collections:
            await self.db.drop_collection(collection_name)

    # --------------------------
    # COPY COLLECTION (used when renaming an org)
    # --------------------------
    async def copy_collection(self, src_name: str, dest_name: str, batch_size: int = 500):
        """
        Copies all documents from src -> dest in batches.
        Used when renaming an organization or migrating data.
        """
        src = self.db.get_collection(src_name)
        dest = self.db.get_collection(dest_name)

        cursor = src.find({})
        batch = []

        async for doc in cursor:
            doc.pop("_id", None)  # Ensure new Object IDs
            batch.append(doc)

            if len(batch) >= batch_size:
                await dest.insert_many(batch)
                batch = []

        # Insert remaining docs
        if batch:
            await dest.insert_many(batch)

    # --------------------------
    # RENAME COLLECTION
    # --------------------------
    async def rename_collection(self, old_name: str, new_name: str):
        """
        Try renaming using MongoDB operation.
        If not possible (Motor limitations), use copy → drop fallback.
        """
        try:
            # Works only if privileges allow rename
            await self.db[old_name].rename(new_name, dropTarget=True)
        except Exception:
            # fallback: manually copy & drop
            await self.copy_collection(old_name, new_name)
            await self.drop_collection(old_name)
