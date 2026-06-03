import os
import json
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Dict, Any

from app.core.config import settings

# Initialize OpenAI Client
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# Define internal Pydantic models for Structured Outputs from OpenAI
class PersonaList(BaseModel):
    personas: List[dict] # Will parse into the DB model format

class CompetitorList(BaseModel):
    competitors: List[str]
    opportunities: List[str]
    positioning: str
    messaging_gaps: List[str]
    feature_gaps: List[str]

class AngleList(BaseModel):
    angles: List[dict]

class HookList(BaseModel):
    hooks: List[dict]

class HeadlineList(BaseModel):
    headlines: List[dict]

class CTAList(BaseModel):
    ctas: List[dict]

class AdCopyList(BaseModel):
    copies: List[dict]

class ConceptList(BaseModel):
    concepts: List[dict]

class ScriptList(BaseModel):
    scripts: List[dict]

class ScoreOutput(BaseModel):
    score: int
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]

def _call_llm(system: str, prompt: str, response_format: type[BaseModel]) -> BaseModel:
    """Wrapper to call OpenAI with Structured Outputs."""
    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini", # Use mini for speed/cost, can upgrade to gpt-4o
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            response_format=response_format,
            temperature=0.7
        )
        return response.choices[0].message.parsed
    except Exception as e:
        print(f"LLM Error: {e}")
        # Return empty/default if it fails to prevent crashing the pipeline
        return response_format(**{})

def generate_personas(context: str) -> List[dict]:
    sys = "You are a senior growth marketer. Generate 3-5 highly detailed target customer personas based on the product context."
    prompt = f"Product Context:\n{context}\n\nGenerate personas including name, demographics, job_role, pain_points (list), goals (list), motivations (list), buying_triggers (list), objections (list)."
    res = _call_llm(sys, prompt, PersonaList)
    return getattr(res, 'personas', [])

def generate_competitor_insights(context: str) -> dict:
    sys = "You are a senior creative strategist. Analyze the market for the given product and identify competitors, gaps, and opportunities."
    prompt = f"Product Context:\n{context}\n\nGenerate competitor insights."
    res = _call_llm(sys, prompt, CompetitorList)
    return res.model_dump() if res else {}

def generate_angles(context: str) -> List[dict]:
    sys = "You are a master copywriter. Generate exactly 10 distinct marketing angles (e.g. Time Saving, Cost Reduction, FOMO, Social Proof)."
    prompt = f"Product Context:\n{context}\n\nGenerate angles with a 'name' and 'description'."
    res = _call_llm(sys, prompt, AngleList)
    return getattr(res, 'angles', [])

def generate_hooks(context: str) -> List[dict]:
    sys = "You are a direct-response marketer. Generate 15 thumb-stopping hooks categorized by type (Curiosity, Pain, Emotional, Fear, Authority, Contrarian)."
    prompt = f"Product Context:\n{context}\n\nGenerate hooks with 'type', 'content', and a 'score' (1-100) predicting its virality."
    res = _call_llm(sys, prompt, HookList)
    return getattr(res, 'hooks', [])

def generate_headlines(context: str) -> List[dict]:
    sys = "You are a media buyer. Generate 15 high-converting headlines optimized for different platforms (Meta, LinkedIn, Google)."
    prompt = f"Product Context:\n{context}\n\nGenerate headlines with 'platform' and 'content'."
    res = _call_llm(sys, prompt, HeadlineList)
    return getattr(res, 'headlines', [])

def generate_ctas(context: str) -> List[dict]:
    sys = "Generate 10 Call-to-Actions (CTAs) for this product."
    prompt = f"Context:\n{context}\n\nInclude type (Direct, Soft, Urgency, Demo, Trial) and content."
    res = _call_llm(sys, prompt, CTAList)
    return getattr(res, 'ctas', [])

def generate_ad_copy(context: str, angles: List[dict]) -> List[dict]:
    sys = "You are a senior copywriter. Write full ad copy following the PAS (Problem-Agitation-Solution) framework."
    prompt = f"Context:\n{context}\n\nAngles:\n{json.dumps(angles[:3])}\n\nGenerate 4 copies (1 for Meta, 1 for LinkedIn, 2 for Google Search). Format: platform, problem, agitation, solution, benefits, cta."
    res = _call_llm(sys, prompt, AdCopyList)
    return getattr(res, 'copies', [])

def generate_creative_concepts(context: str) -> List[dict]:
    sys = "You are an art director. Generate 5 highly visual ad creative concepts (e.g. Before/After, Founder Story)."
    prompt = f"Context:\n{context}\n\nGenerate concepts with concept_name, visual_direction, marketing_goal, and a storyboard (list of objects with 'scene' and 'visual')."
    res = _call_llm(sys, prompt, ConceptList)
    return getattr(res, 'concepts', [])

def generate_video_scripts(context: str) -> List[dict]:
    sys = "You are a TikTok/Reels viral scriptwriter."
    prompt = f"Context:\n{context}\n\nGenerate 3 video scripts (TikTok, Instagram Reel, YouTube Shorts). Include platform, hook, body, cta, and timestamps (list of objects with 'time' and 'action')."
    res = _call_llm(sys, prompt, ScriptList)
    return getattr(res, 'scripts', [])

def generate_campaign_score(context: str, copies: List[dict], scripts: List[dict]) -> dict:
    sys = "You are a Chief Marketing Officer. Score the generated campaign out of 100."
    prompt = f"Copies:\n{json.dumps(copies)}\n\nScripts:\n{json.dumps(scripts)}\n\nEvaluate the persuasiveness, clarity, and emotional impact. Provide score, strengths, weaknesses, and recommendations."
    res = _call_llm(sys, prompt, ScoreOutput)
    return res.model_dump() if res else {}
