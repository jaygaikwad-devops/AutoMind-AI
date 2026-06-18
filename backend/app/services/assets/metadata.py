import subprocess
import json
import os
import math

class MetadataExtractor:
    @staticmethod
    def extract_video_metadata(file_path: str) -> dict:
        """
        Uses ffprobe to extract video metadata.
        Returns: duration, resolution, aspect_ratio, file_size_bytes, format
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_size_bytes = os.path.getsize(file_path)
        format_ext = os.path.splitext(file_path)[1].replace('.', '').lower()

        # Run ffprobe
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            file_path
        ]

        try:
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            probe_data = json.loads(result.stdout)
        except Exception as e:
            print(f"Error running ffprobe: {e}")
            return {
                "duration_seconds": 0,
                "resolution": "Unknown",
                "aspect_ratio": "Unknown",
                "file_size_bytes": file_size_bytes,
                "format": format_ext
            }

        # Extract duration
        duration_seconds = 0
        if 'format' in probe_data and 'duration' in probe_data['format']:
            duration_seconds = math.ceil(float(probe_data['format']['duration']))

        # Find video stream for resolution and aspect ratio
        video_stream = next((stream for stream in probe_data.get('streams', []) if stream.get('codec_type') == 'video'), None)
        
        resolution = "Unknown"
        aspect_ratio = "Unknown"

        if video_stream:
            width = video_stream.get('width', 0)
            height = video_stream.get('height', 0)
            
            if width and height:
                resolution = f"{width}x{height}"
                
                # Calculate aspect ratio
                def gcd(a, b):
                    while b:
                        a, b = b, a % b
                    return a
                
                divisor = gcd(width, height)
                if divisor:
                    w_ratio = width // divisor
                    h_ratio = height // divisor
                    
                    # Simplify standard ratios
                    if w_ratio == 8 and h_ratio == 5: # 16:10 approx sometimes shows as 8:5
                        w_ratio, h_ratio = 16, 10
                    
                    aspect_ratio = f"{w_ratio}:{h_ratio}"
                    
                    # Hardcode common overrides for standard 16:9 / 9:16 approx
                    if abs((width/height) - (16/9)) < 0.05:
                        aspect_ratio = "16:9"
                    elif abs((width/height) - (9/16)) < 0.05:
                        aspect_ratio = "9:16"

        return {
            "duration_seconds": duration_seconds,
            "resolution": resolution,
            "aspect_ratio": aspect_ratio,
            "file_size_bytes": file_size_bytes,
            "format": format_ext
        }
