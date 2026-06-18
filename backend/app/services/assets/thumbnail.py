import os
import uuid
from moviepy.editor import VideoFileClip

class ThumbnailService:
    @staticmethod
    def generate_thumbnail(video_path: str, output_dir: str = "/tmp") -> str:
        """
        Uses moviepy to extract a thumbnail at duration * 0.25 to avoid black screens.
        Returns the path to the generated .jpg file.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        try:
            clip = VideoFileClip(video_path)
            duration = clip.duration
            
            # Extract at 25% of the video duration
            target_time = duration * 0.25
            
            output_path = os.path.join(output_dir, f"thumb_{uuid.uuid4().hex}.jpg")
            
            clip.save_frame(output_path, t=target_time)
            clip.close()
            
            return output_path
        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            raise e
