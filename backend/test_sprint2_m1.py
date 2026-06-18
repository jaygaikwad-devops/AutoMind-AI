import asyncio
import os
import uuid
from app.core.config import settings
from app.db import AsyncSessionLocal
from app.models.asset import Asset
from app.services.assets.asset_service import AssetService

async def test_milestone_1():
    print("=== Testing Sprint 2: Milestone 1 ===")
    
    # 1. Create a dummy file to upload
    test_file_path = "test.mp4"
    with open(test_file_path, "w") as f:
        f.write("dummy video content")
    print(f"Created dummy file: {test_file_path}")

    asset_service = AssetService()
    s3_key = f"users/test_user/videos/test_{uuid.uuid4()}.mp4"

    try:
        # 2. Upload to S3
        print(f"\nAttempting to upload to S3: {s3_key}")
        cdn_url = asset_service.upload_asset(s3_key, test_file_path, "video/mp4")
        print(f"✅ Upload successful!")
        print(f"CDN URL generated: {cdn_url}")

        # 3. Check if exists
        exists = asset_service.asset_exists(s3_key)
        print(f"Asset exists in S3: {exists}")

        # 4. Generate Presigned URL
        presigned_url = asset_service.generate_presigned_url(s3_key)
        print(f"\n✅ Presigned URL generated:\n{presigned_url}")

        # 5. Create Database Record
        print("\nCreating Database Record...")
        async with AsyncSessionLocal() as session:
            new_asset = Asset(
                user_id="test_user",
                type="video",
                provider="test",
                s3_key=s3_key,
                cdn_url=cdn_url,
                status="ready"
            )
            session.add(new_asset)
            await session.commit()
            await session.refresh(new_asset)
            print(f"✅ DB Record Created! Asset ID: {new_asset.id}")

        # 6. Delete Asset
        print(f"\nDeleting asset from S3...")
        deleted = asset_service.delete_asset(s3_key)
        print(f"✅ Asset deleted: {deleted}")

    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        print("Note: Ensure you have set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_REGION in your .env file.")
    finally:
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

if __name__ == "__main__":
    asyncio.run(test_milestone_1())
