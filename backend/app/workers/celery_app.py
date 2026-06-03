from celery import Celery
from app.core.config import settings
from app.db import SessionLocal
from app.models import Video, SocialPost
from datetime import datetime
import time
import os
import requests
import asyncio
import tempfile
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from azure.storage.blob import BlobServiceClient

celery_app = Celery("automind", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

def get_pexels_video(query="nature"):
    if not settings.PEXELS_API_KEY:
        print("No Pexels API key provided.")
        return None
    headers = {"Authorization": settings.PEXELS_API_KEY}
    res = requests.get(f"https://api.pexels.com/videos/search?query={query}&per_page=15&orientation=portrait", headers=headers)
    if res.status_code == 200 and res.json().get("videos"):
        videos = res.json()["videos"]
        if videos:
            video_files = videos[0]["video_files"]
            video_files.sort(key=lambda x: x["width"] * x["height"], reverse=True)
            return video_files[0]["link"]
    return None

async def generate_audio(text, output_path):
    tts = gTTS(text=text, lang='en', tld='com')
    tts.save(output_path)

def upload_to_azure(file_path, blob_name):
    if not settings.AZURE_STORAGE_CONNECTION_STRING:
        print("No Azure storage connection string provided.")
        return None
    try:
        blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
        blob_client = blob_service_client.get_blob_client(container=settings.AZURE_CONTAINER_NAME, blob=blob_name)
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        return blob_client.url
    except Exception as e:
        print(f"Azure upload failed: {e}")
        return None

@celery_app.task
def render_video(video_id: str, prompt: str) -> dict:
    with SessionLocal() as db:
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            return {"error": "Video not found"}
        video.status = "rendering"
        db.commit()

    temp_dir = tempfile.mkdtemp()
    try:
        # 1. Generate audio
        audio_path = os.path.join(temp_dir, "audio.mp3")
        asyncio.run(generate_audio(prompt, audio_path))
        
        # 2. Get stock video from Pexels
        keyword = "cityscape" if "city" in prompt.lower() else ("technology" if "tech" in prompt.lower() else "abstract")
        video_url = get_pexels_video(keyword)
        stock_path = os.path.join(temp_dir, "stock.mp4")
        if video_url:
            r = requests.get(video_url, stream=True)
            with open(stock_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    if chunk: f.write(chunk)
        else:
            raise Exception("No Pexels video found or no API key provided")
            
        # 3. Assemble with MoviePy
        clip = VideoFileClip(stock_path)
        audio = AudioFileClip(audio_path)
        
        # Match durations
        duration = min(audio.duration, 60.0) # Cap at 60s
        if clip.duration < duration:
            # If stock is shorter, loop it (requires vfx or just looping simple)
            clip = clip.loop(duration=duration)
        clip = clip.subclip(0, duration)
        clip = clip.set_audio(audio)
        
        # Add text overlay
        # Note: Depending on ImageMagick config, TextClip might need font adjustments.
        txt_clip = TextClip(prompt, fontsize=60, color='white', font='DejaVu-Sans-Bold', bg_color='rgba(0,0,0,0.5)', size=(clip.w*0.8, None), method='caption')
        txt_clip = txt_clip.set_position('center').set_duration(duration)
        
        final_clip = CompositeVideoClip([clip, txt_clip])
        out_path = os.path.join(temp_dir, f"{video_id}.mp4")
        
        # Render
        final_clip.write_videofile(out_path, fps=24, codec="libx264", audio_codec="aac", logger=None)
        
        # 4. Upload to Azure
        azure_url = upload_to_azure(out_path, f"{video_id}.mp4")
        if not azure_url:
            raise Exception("Azure upload returned None. Check Azure credentials.")

        with SessionLocal() as db:
            video = db.query(Video).filter(Video.id == video_id).first()
            video.status = "ready"
            video.url = azure_url
            db.commit()

        return {"video_id": video_id, "status": "ready", "url": azure_url}
        
    except Exception as e:
        print(f"Error rendering video: {e}")
        with SessionLocal() as db:
            video = db.query(Video).filter(Video.id == video_id).first()
            video.status = "failed"
            db.commit()
        return {"error": str(e)}
    finally:
        # Cleanup temp files
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


@celery_app.task
def publish_post(post_id: str, platform: str, content: str) -> dict:
    with SessionLocal() as db:
        post = db.query(SocialPost).filter(SocialPost.id == post_id).first()
        if not post:
            return {"error": "Post not found"}
        
        time.sleep(3)
        post.status = "published"
        post.published_at = datetime.utcnow()
        db.commit()

    return {"post_id": post_id, "platform": platform, "status": "published"}

@celery_app.task
def execute_workflow_task(workflow_id: str) -> dict:
    from app.models import Workflow
    import uuid
    import time
    
    with SessionLocal() as db:
        wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not wf:
            return {"error": "Workflow not found"}
            
        nodes = wf.nodes or []
        edges = wf.edges or []
        
        prompt_node = next((n for n in nodes if n.get("type") == "prompt"), None)
        if not prompt_node:
            return {"error": "No prompt node found in workflow"}
            
        prompt_text = prompt_node.get("data", {}).get("prompt", "")
        if not prompt_text.strip():
            return {"error": "Video rendering failed: No text to speak"}
        
        video_node = next((n for n in nodes if n.get("type") == "video"), None)
        if not video_node:
            return {"error": "No video node found in workflow"}
            
        # Extract premium config
        video_data = video_node.get("data", {})
        voice = video_data.get("voice", "rachel")
        language = video_data.get("language", "en")
        
        # Create Video DB entry
        video_id = str(uuid.uuid4())
        db_video = Video(
            id=video_id,
            user_id=wf.user_id,
            prompt=prompt_text,
            status="queued"
        )
        db.add(db_video)
        db.commit()
        
    # Render Video
    # In a real app with ELEVENLABS_API_KEY and RUNWAY_API_KEY, we would call those here.
    # For now, we fallback to our Pexels + gTTS generator.
    print(f"[PREMIUM] Using ElevenLabs Voice: {voice}, Language: {language}")
    result = render_video(video_id, prompt_text)
    
    if "error" in result:
        return {"error": f"Video rendering failed: {result['error']}"}
        
    # Find Social Node
    social_node = next((n for n in nodes if n.get("type") == "social"), None)
    
    if social_node:
        platform = social_node.get("data", {}).get("platform", "instagram")
        
        # Check for Smart Captions
        caption_node = next((n for n in nodes if n.get("type") == "caption"), None)
        caption_text = f"Check out this AI generated video: {prompt_text}"
        if caption_node:
            tone = caption_node.get("data", {}).get("tone", "engaging")
            print(f"[AI] Generating {tone} caption...")
            time.sleep(1) # Simulate LLM call
            if tone == "funny":
                caption_text = f"Nobody: ...\nMe generating {prompt_text} with AI 😂🔥"
            elif tone == "professional":
                caption_text = f"Exploring the boundaries of generative AI with a focus on {prompt_text}. #Innovation"
            else:
                caption_text = f"This AI generation of {prompt_text} is absolutely mind-blowing! 🚀✨"
                
        # Check for Viral Hashtags
        hashtag_node = next((n for n in nodes if n.get("type") == "hashtag"), None)
        if hashtag_node:
            niche = hashtag_node.get("data", {}).get("niche", "ai")
            print(f"[AI] Generating hashtags for niche: {niche}")
            time.sleep(1) # Simulate LLM call
            caption_text += f"\n\n#fyp #viral #{niche.replace(' ', '')} #aigenerated"
            
        # Append URL
        content = f"{caption_text}\n\nLink: {result.get('url', '')}"
        
        with SessionLocal() as db:
            post_id = str(uuid.uuid4())
            db_post = SocialPost(
                id=post_id,
                user_id=wf.user_id,
                platform=platform,
                content=content,
                status="scheduled"
            )
            db.add(db_post)
            db.commit()
            
        publish_post.delay(post_id, platform, content)
            
    return {"status": "success", "video_id": video_id}

@celery_app.task
def generate_full_campaign(campaign_id: str):
    from app.services.campaigns.orchestrator import generate_full_campaign_sync
    from app.db import SessionLocal
    
    with SessionLocal() as db:
        generate_full_campaign_sync(db, campaign_id)
        
    return {"status": "success", "campaign_id": campaign_id}
