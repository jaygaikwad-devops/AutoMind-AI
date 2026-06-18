import boto3
import uuid
import os
from botocore.exceptions import ClientError
from typing import Optional, Dict, Any, Tuple
from app.core.config import settings
from .metadata import MetadataExtractor
from .thumbnail import ThumbnailService

class AssetService:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket = settings.AWS_S3_BUCKET
        self.cloudfront_domain = settings.AWS_CLOUDFRONT_DOMAIN

    def get_cdn_url(self, s3_key: str) -> str:
        """Returns the CloudFront CDN URL for a given S3 key."""
        if self.cloudfront_domain:
            return f"https://{self.cloudfront_domain}/{s3_key}"
        return f"https://{self.bucket}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"

    def get_s3_layout_key(self, user_id: str, asset_type: str, filename: str, campaign_id: str = "default") -> str:
        """
        Generates S3 key: users/{user_id}/campaigns/{campaign_id}/{asset_type}s/{filename}
        asset_type should be one of: video, image, voiceover, thumbnail, export
        """
        return f"users/{user_id}/campaigns/{campaign_id}/{asset_type}s/{filename}"

    def upload_asset(self, s3_key: str, file_path: str, content_type: str = "application/octet-stream") -> str:
        """Uploads a file to S3 and returns its CDN URL."""
        try:
            self.s3_client.upload_file(
                file_path, 
                self.bucket, 
                s3_key,
                ExtraArgs={'ContentType': content_type}
            )
            return self.get_cdn_url(s3_key)
        except ClientError as e:
            print(f"Error uploading to S3: {e}")
            raise e

    def process_and_upload_video(self, user_id: str, file_path: str, campaign_id: str = "default") -> Tuple[str, str, dict, Optional[str], Optional[str]]:
        """
        Orchestrates full video processing:
        1. Extract metadata (ffprobe)
        2. Extract thumbnail (moviepy)
        3. Upload video
        4. Upload thumbnail
        Returns: (video_s3_key, video_cdn_url, metadata_dict, thumb_s3_key, thumb_cdn_url)
        """
        # 1. Metadata
        meta = MetadataExtractor.extract_video_metadata(file_path)
        
        # 2. Thumbnail
        thumb_path = None
        try:
            thumb_path = ThumbnailService.generate_thumbnail(file_path)
        except Exception as e:
            print(f"Failed to generate thumbnail: {e}")

        # 3. S3 Keys
        base_name = f"{uuid.uuid4().hex}"
        video_ext = os.path.splitext(file_path)[1]
        video_s3_key = self.get_s3_layout_key(user_id, "video", f"{base_name}{video_ext}", campaign_id)
        
        thumb_s3_key = None
        thumb_cdn_url = None
        
        if thumb_path and os.path.exists(thumb_path):
            thumb_s3_key = self.get_s3_layout_key(user_id, "thumbnail", f"{base_name}_thumb.jpg", campaign_id)

        # 4. Uploads
        video_cdn_url = self.upload_asset(video_s3_key, file_path, f"video/{video_ext.replace('.','')}")
        
        if thumb_s3_key:
            thumb_cdn_url = self.upload_asset(thumb_s3_key, thumb_path, "image/jpeg")
            # Cleanup temp thumbnail
            try:
                os.remove(thumb_path)
            except:
                pass

        return video_s3_key, video_cdn_url, meta, thumb_s3_key, thumb_cdn_url

    def delete_asset(self, s3_key: str) -> bool:
        """Deletes an asset from S3."""
        try:
            self.s3_client.delete_object(Bucket=self.bucket, Key=s3_key)
            return True
        except ClientError as e:
            print(f"Error deleting from S3: {e}")
            return False

    def generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> str:
        """Generates a pre-signed URL to share an S3 object."""
        try:
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return response
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            raise e

    def asset_exists(self, s3_key: str) -> bool:
        """Checks if an object exists in the S3 bucket."""
        try:
            self.s3_client.head_object(Bucket=self.bucket, Key=s3_key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise e

    def get_asset(self, s3_key: str) -> Optional[Dict[str, Any]]:
        """Gets metadata/headers for a specific object."""
        try:
            response = self.s3_client.head_object(Bucket=self.bucket, Key=s3_key)
            return response
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return None
            print(f"Error getting object from S3: {e}")
            return None
