from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Any, Dict
from datetime import datetime

class CampaignCreate(BaseModel):
    website_url: Optional[str] = None
    product_url: Optional[str] = None
    product_description: Optional[str] = None
    brand_information: Optional[str] = None
    target_audience: Optional[str] = None
    campaign_goal: Optional[str] = None

class PersonaOut(BaseModel):
    id: str
    name: str
    demographics: str
    job_role: str
    pain_points: List[str]
    goals: List[str]
    motivations: List[str]
    buying_triggers: List[str]
    objections: List[str]

    class Config:
        from_attributes = True

class CompetitorInsightOut(BaseModel):
    id: str
    competitors: List[str]
    opportunities: List[str]
    positioning: str
    messaging_gaps: List[str]
    feature_gaps: List[str]

    class Config:
        from_attributes = True

class AngleOut(BaseModel):
    id: str
    name: str
    description: str

    class Config:
        from_attributes = True

class HookOut(BaseModel):
    id: str
    type: str
    content: str
    score: int

    class Config:
        from_attributes = True

class HeadlineOut(BaseModel):
    id: str
    platform: str
    content: str

    class Config:
        from_attributes = True

class CTAOut(BaseModel):
    id: str
    type: str
    content: str

    class Config:
        from_attributes = True

class AdCopyOut(BaseModel):
    id: str
    platform: str
    problem: str
    agitation: str
    solution: str
    benefits: str
    cta: str

    class Config:
        from_attributes = True

class CreativeConceptOut(BaseModel):
    id: str
    concept_name: str
    visual_direction: str
    marketing_goal: str
    storyboard: List[Dict[str, Any]]

    class Config:
        from_attributes = True

class VideoScriptOut(BaseModel):
    id: str
    platform: str
    hook: str
    body: str
    cta: str
    timestamps: List[Dict[str, Any]]

    class Config:
        from_attributes = True

class CampaignScoreOut(BaseModel):
    id: str
    score: int
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]

    class Config:
        from_attributes = True

class CampaignOut(BaseModel):
    id: str
    status: str
    website_url: Optional[str] = None
    campaign_goal: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class CampaignFullOut(CampaignOut):
    personas: List[PersonaOut] = []
    competitor_insights: List[CompetitorInsightOut] = []
    angles: List[AngleOut] = []
    hooks: List[HookOut] = []
    headlines: List[HeadlineOut] = []
    ctas: List[CTAOut] = []
    ad_copies: List[AdCopyOut] = []
    creative_concepts: List[CreativeConceptOut] = []
    video_scripts: List[VideoScriptOut] = []
    scores: List[CampaignScoreOut] = []

    class Config:
        from_attributes = True
