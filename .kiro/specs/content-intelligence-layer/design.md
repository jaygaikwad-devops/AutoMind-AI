# Design Document — Content Intelligence Layer (Sprint 3.1C)

## Overview

This design defines the architecture for Sprint 3.1C: five new content agents, a ContentBundle model, a PromptRegistry with versioning, an upgraded ValidationLayer, explicit JSON content schemas, and a full-content-bundle orchestrator. The design optimizes for AWS-native deployment, multi-tenant SaaS scalability, credit-based monetization, and minimum future refactoring across Sprints 3.2–6.

## Architecture

---

## 1. Campaign Intelligence Graph

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              CAMPAIGN INTELLIGENCE PIPELINE                              │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌──────────┐     ┌──────────────────────────────────────────────────────────────────┐  │
│  │ Website  │────▶│              MarketIntelligenceService                           │  │
│  │   URL    │     │  ┌────────────┐  ┌──────────────┐  ┌────────────────────┐       │  │
│  └──────────┘     │  │ Website    │  │TrendSnapshot │  │CompetitorSnapshot  │       │  │
│                   │  │ Scraper    │  │ (24h cache)  │  │   (24h cache)      │       │  │
│                   │  └─────┬──────┘  └──────┬───────┘  └─────────┬──────────┘       │  │
│                   └────────┼────────────────┼────────────────────┼───────────────────┘  │
│                            │                │                    │                       │
│                            ▼                ▼                    ▼                       │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                     ResearchSnapshot (MarketResearchAgent)                       │    │
│  └──────────────────────────────────────┬──────────────────────────────────────────┘    │
│                                         │                                               │
│                                         ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                           Persona (PersonaAgent)                                 │    │
│  └──────────────────────────────────────┬──────────────────────────────────────────┘    │
│                                         │                                               │
│                                         ▼                                               │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                            Hooks (HookAgent)                                     │    │
│  └──────┬───────────────┬───────────────┬────────────────┬─────────────────────────┘    │
│         │               │               │                │                              │
│         ▼               ▼               ▼                ▼                              │
│  ┌───────────┐   ┌───────────┐   ┌───────────┐   ┌───────────┐                        │
│  │ Captions  │   │ Hashtags  │   │  Ad Copy  │   │    SEO    │                        │
│  │(+Brand)   │   │(+Trends)  │   │(+Compete) │   │(+Trends   │                        │
│  └─────┬─────┘   └─────┬─────┘   └─────┬─────┘   │+Compete)  │                        │
│        │               │               │          └─────┬─────┘                        │
│        │               │               │                │                              │
│        │               │               ▼                │                              │
│        │               │         ┌───────────┐          │                              │
│        │               │         │    CTA    │          │                              │
│        │               │         │(+Brand    │          │                              │
│        │               │         │+Ad Copy)  │          │                              │
│        │               │         └─────┬─────┘          │                              │
│        │               │               │                │                              │
│        ▼               ▼               ▼                ▼                              │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                          ContentBundle (all outputs)                             │    │
│  └──────────────────────────────────────┬──────────────────────────────────────────┘    │
│                                         │                                               │
├─────────────────────────────────────────┼───────────────────────────────────────────────┤
│          FUTURE SPRINTS                 │                                               │
│                                         ▼                                               │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐            │
│  │Creative Studio│  │  Publishing   │  │  Analytics    │  │Media Buyer AI │            │
│  │  (Sprint 3.2) │  │ (Sprint 3.4)  │  │ (Sprint 3.5)  │  │ (Sprint 6)    │            │
│  └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘            │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Components and Interfaces

The Content Intelligence Layer introduces these components:

| Component                    | Type            | Interfaces                                           |
|------------------------------|-----------------|------------------------------------------------------|
| CaptionAgent                 | BaseAgent       | run(), validate(), persist(), emit_event()           |
| HashtagAgent                 | BaseAgent       | run(), validate(), persist(), emit_event()           |
| AdCopyAgent                  | BaseAgent       | run(), validate(), persist(), emit_event()           |
| SEOAgent                     | BaseAgent       | run(), validate(), persist(), emit_event()           |
| CTAAgent                     | BaseAgent       | run(), validate(), persist(), emit_event()           |
| ContentBundleOrchestrator    | Orchestrator    | execute(payload, user_id, db) → dict                 |
| PromptRegistry               | Singleton       | get(), register(), set_active_version(), list_versions() |
| ValidationLayer (enhanced)   | Utility         | validate_content(content, content_type) → dict       |
| ContentBundle                | SQLAlchemy Model| ORM fields (see Data Models)                         |

All agents implement the BaseAgent abstract interface and are executed via the existing AgentRunner without modification.

---

## Data Models

### ContentBundle Model (NEW)

| Column                 | Type     | Nullable | Description                              |
|------------------------|----------|:--------:|------------------------------------------|
| id                     | String   | PK       | UUID primary key                         |
| user_id                | String   | No       | FK → users.id                            |
| campaign_id            | String   | Yes      | FK → campaigns.id                        |
| status                 | String   | No       | running / completed / partial / failed   |
| total_credits_reserved | Integer  | No       | Default 44                               |
| total_credits_committed| Integer  | No       | Sum of committed credits                 |
| completed_agents       | JSON     | Yes      | List of event_types that succeeded       |
| failed_agent           | String   | Yes      | event_type of failed agent               |
| error_message          | Text     | Yes      | Error details                            |
| avg_quality_score      | Float    | Yes      | Mean quality across agents               |
| min_quality_score      | Integer  | Yes      | Lowest agent score                       |
| quality_breakdown      | JSON     | Yes      | {agent: score} map                       |
| input_metadata         | JSON     | Yes      | Original request params                  |
| generation_metadata    | JSON     | Yes      | Model versions, timings                  |
| created_at             | DateTime | No       | Auto-set                                 |
| completed_at           | DateTime | Yes      | Set on completion                        |

### CampaignContent Model (MODIFIED)

| Column Added | Type   | Nullable | Description                    |
|--------------|--------|:--------:|--------------------------------|
| bundle_id    | String | Yes      | FK → content_bundles.id, ON DELETE SET NULL |

---

## 2. ContentBundle Architecture

### 2.1 ContentBundle Model

**Module:** `backend/app/models/content_bundle.py`

```python
class ContentBundle(Base):
    __tablename__ = "content_bundles"
    __table_args__ = (
        Index("ix_content_bundles_user_id", "user_id"),
        Index("ix_content_bundles_campaign_id", "campaign_id"),
        Index("ix_content_bundles_status", "status"),
        Index("ix_content_bundles_created_at", "created_at"),
    )

    id                      = Column(String, primary_key=True, default=_id)
    user_id                 = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    campaign_id             = Column(String, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=True)

    # ── Status & Lifecycle ───────────────────────────────────────────
    status                  = Column(String, nullable=False, default="running")
    # Values: "running" | "completed" | "partial" | "failed"

    # ── Credit Accounting ────────────────────────────────────────────
    total_credits_reserved  = Column(Integer, default=44)
    total_credits_committed = Column(Integer, default=0)

    # ── Completion Tracking ──────────────────────────────────────────
    completed_agents        = Column(JSON, nullable=True)   # list[str] of event_types
    failed_agent            = Column(String, nullable=True)  # event_type that failed
    error_message           = Column(Text, nullable=True)

    # ── Quality Scoring (bundle-level) ───────────────────────────────
    avg_quality_score       = Column(Float, nullable=True)   # Average of all agent scores
    min_quality_score       = Column(Integer, nullable=True)  # Lowest agent score
    quality_breakdown       = Column(JSON, nullable=True)     # {agent: score} map

    # ── Bundle Metadata ──────────────────────────────────────────────
    input_metadata          = Column(JSON, nullable=True)     # Original request params
    generation_metadata     = Column(JSON, nullable=True)     # Model versions, timings

    # ── Timestamps ───────────────────────────────────────────────────
    created_at              = Column(DateTime, default=datetime.utcnow)
    completed_at            = Column(DateTime, nullable=True)
```

### 2.2 CampaignContent → ContentBundle Relationship

CampaignContent gains an optional `bundle_id` foreign key:

```python
# Added to existing CampaignContent model:
bundle_id = Column(String, ForeignKey("content_bundles.id", ondelete="SET NULL"), nullable=True, index=True)
```

**Relationship semantics:**
- One ContentBundle → many CampaignContent records (one per agent in the bundle)
- Individual agent calls (not part of a bundle) have `bundle_id = NULL`
- ON DELETE SET NULL: Deleting a bundle doesn't delete content (content survives independently)

### 2.3 Bundle-Level Quality Scoring

Bundle quality is computed after all agents complete:

```python
# Computed in ContentBundleOrchestrator after all agents finish:
quality_scores = {agent_name: result["quality_score"] for agent_name, result in results.items()}
bundle.avg_quality_score = sum(quality_scores.values()) / len(quality_scores)
bundle.min_quality_score = min(quality_scores.values())
bundle.quality_breakdown = quality_scores
```

**Quality interpretation for downstream systems:**
| avg_quality_score | Label     | Downstream Behavior                               |
|:-----------------:|-----------|---------------------------------------------------|
| 90–100            | Excellent | Auto-approve for publishing                       |
| 80–89             | Good      | Approve with review flag                          |
| 70–79             | Fair      | Manual review required before publishing          |
| < 70              | Poor      | Flag for regeneration or manual editing           |

### 2.4 Bundle-Level Metadata

```json
{
  "input_metadata": {
    "website_url": "https://example.com",
    "product_name": "Example Product",
    "industry": "saas",
    "brand_profile_id": "bp-uuid",
    "campaign_id": "camp-uuid"
  },
  "generation_metadata": {
    "model_version": "claude-sonnet-4-20250514",
    "validation_model": "claude-haiku",
    "total_duration_ms": 45200,
    "per_agent_duration_ms": {
      "research": 8500,
      "persona": 6200,
      "hooks": 5800,
      "captions": 5100,
      "hashtags": 3200,
      "adcopy": 7400,
      "seo": 12000,
      "cta": 3500
    },
    "trend_snapshot_id": "ts-uuid",
    "competitor_snapshot_ids": ["cs-uuid-1", "cs-uuid-2"]
  }
}
```

### 2.5 Bundle Lifecycle States

```
                    ┌─────────────────┐
                    │     CREATED     │  (ContentBundle row inserted)
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     RUNNING     │  (Agents executing sequentially)
                    └────────┬────────┘
                             │
                    ┌────────┼────────┐
                    │        │        │
                    ▼        │        ▼
          ┌──────────────┐   │   ┌──────────────┐
          │  COMPLETED   │   │   │   PARTIAL    │
          │(all 8 done)  │   │   │(some failed) │
          └──────────────┘   │   └──────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     FAILED      │  (First agent failed, no content produced)
                    └─────────────────┘
```

**State transitions:**
- `running` → `completed`: All 8 agents succeeded
- `running` → `partial`: An agent failed after at least one agent succeeded
- `running` → `failed`: The first agent (Research) failed, no content produced

---

## 3. PromptRegistry Architecture

### 3.1 Purpose

Centralizes all LLM prompt templates in a versioned registry, enabling:
- Prompt version control independent of agent logic
- A/B testing of prompt variants
- Consistent context injection (BrandProfile, TrendSnapshot, CompetitorSnapshot)
- Separation of concerns: agents handle orchestration, PromptRegistry handles content
- Auditing: track which prompt version produced which content

### 3.2 Module Location

```
backend/app/services/llm/prompt_registry.py
```

### 3.3 Design

```python
@dataclass(frozen=True)
class PromptTemplate:
    """Immutable prompt template with version tracking."""
    name: str                            # e.g. "caption_v1"
    version: int                         # Incrementing version number
    system: str                          # Static system prompt
    user_builder: Callable[[dict], str]  # Builds user prompt from context dict
    max_context_chars: int = 8000        # Truncation limit for context injection
    max_tokens: int = 4096              # Bedrock max_tokens override
    metadata: dict = field(default_factory=dict)  # A/B test tags, notes


class PromptRegistry:
    """
    Singleton registry of system prompts and user prompt builders.
    Each agent calls PromptRegistry.get(agent_name) to obtain its prompt pair.
    Supports versioning: get(agent_name, version=N) for specific versions.
    """

    _prompts: dict[str, list[PromptTemplate]] = {}  # agent_name → [versions]
    _active_versions: dict[str, int] = {}           # agent_name → active version

    @classmethod
    def get(cls, agent_name: str, version: int | None = None) -> PromptTemplate:
        """Returns the active PromptTemplate (or specific version) for an agent."""

    @classmethod
    def register(cls, template: PromptTemplate) -> None:
        """Register a new prompt version. Latest registered = active by default."""

    @classmethod
    def set_active_version(cls, agent_name: str, version: int) -> None:
        """Explicitly set the active version (for A/B testing or rollbacks)."""

    @classmethod
    def list_versions(cls, agent_name: str) -> list[int]:
        """List all registered versions for an agent."""
```

### 3.4 Registered Prompts

#### caption_prompt (v1)

```python
CAPTION_SYSTEM = """You are an expert social media copywriter who creates platform-native content.
Generate one unique caption per platform, tailored to each platform's norms and audience expectations.

PLATFORM GUIDELINES:
- Instagram: Casual, emoji-rich, max 2200 chars. Hook in first line, CTA at end.
- LinkedIn: Professional, insight-driven, max 3000 chars. No excessive emojis, value-first.
- Facebook: Conversational, warm, max 500 chars. Question-based engagement.
- TikTok: Punchy, trend-aware, max 150 chars. Very short, hook-first.
- YouTube Shorts: Descriptive, SEO-aware, max 100 chars. Keywords in first 40 chars.

BRAND VOICE RULES:
- Match the provided brand tone exactly
- Maintain consistent personality across all platforms while adapting format

Return ONLY valid JSON:
{
  "captions": {
    "instagram": {"text": "...", "character_count": N, "hashtag_suggestions": [...], "cta": "..."},
    "linkedin": {"text": "...", "character_count": N, "hashtag_suggestions": [...], "cta": "..."},
    "facebook": {"text": "...", "character_count": N, "hashtag_suggestions": [...], "cta": "..."},
    "tiktok": {"text": "...", "character_count": N, "hashtag_suggestions": [...], "cta": "..."},
    "youtube_shorts": {"text": "...", "character_count": N, "hashtag_suggestions": [...], "cta": "..."}
  },
  "brand_tone_applied": ["tone1", "tone2"]
}

CRITICAL: No two captions may share identical text. Each must be uniquely written for its platform."""
```

#### hashtag_prompt (v1)

```python
HASHTAG_SYSTEM = """You are a hashtag strategist and social media growth expert.
Generate hashtags in three categories based on the trending data and research provided.

CATEGORIES:
- Viral: High trend_score (60+), broad reach, currently trending
- Niche: High relevance_score (80+), targeted audience, lower competition
- Brand: Product-specific, company-related, high relevance to the brand

SCORING:
- relevance_score (0-100): How relevant is this hashtag to the product/industry?
- trend_score (0-100): How much is this hashtag trending right now?

Generate at least 5 hashtags per category (15+ total).

Return ONLY valid JSON:
{
  "viral_hashtags": [{"hashtag": "#...", "relevance_score": N, "trend_score": N}],
  "niche_hashtags": [{"hashtag": "#...", "relevance_score": N, "trend_score": N}],
  "brand_hashtags": [{"hashtag": "#...", "relevance_score": N, "trend_score": N}],
  "platform": "<platform>",
  "total_hashtags": N
}"""
```

#### adcopy_prompt (v1)

```python
ADCOPY_SYSTEM = """You are a direct-response advertising copywriter.
Generate ad copy using 5 proven frameworks. Use competitor weaknesses as leverage.

FRAMEWORKS:
1. PAS (Problem-Agitate-Solution): Lead with pain, amplify, offer solution
2. AIDA (Attention-Interest-Desire-Action): Classic attention funnel
3. Problem-Aware: For audience that knows the problem but not the solution
4. Solution-Aware: For audience that knows solutions exist but hasn't chosen
5. Offer-Focused: Lead with the value proposition and specific offer

AD SPECS (Meta/Google compatible):
- headline: max 40 characters
- primary_text: max 125 characters
- description: max 90 characters

Return ONLY valid JSON:
{
  "frameworks": {
    "pas": {"headline": "...", "primary_text": "...", "description": "..."},
    "aida": {"headline": "...", "primary_text": "...", "description": "..."},
    "problem_aware": {"headline": "...", "primary_text": "...", "description": "..."},
    "solution_aware": {"headline": "...", "primary_text": "...", "description": "..."},
    "offer_focused": {"headline": "...", "primary_text": "...", "description": "..."}
  },
  "competitor_angles_used": ["angle1", "angle2"]
}"""
```

#### seo_prompt (v1)

```python
SEO_SYSTEM = """You are an SEO content strategist and long-form blog writer.
Generate a complete SEO content package based on the research and trending data provided.

OUTPUT REQUIREMENTS:
- SEO Title: max 60 chars, includes primary keyword
- Meta Description: max 160 chars, compelling with primary keyword
- Outline: 5+ sections with subheadings
- Keywords: primary (1), secondary (3-5), long_tail (2-3)
- Blog Draft: MINIMUM 1500 words, well-structured with H2/H3 headings

TREND INTEGRATION:
- Use trending keywords naturally in the content
- Reference competitor content gaps as opportunities

Return ONLY valid JSON:
{
  "seo_title": "...",
  "meta_description": "...",
  "outline": [{"heading": "...", "subheadings": ["..."]}],
  "keywords": {"primary": "...", "secondary": [...], "long_tail": [...]},
  "blog_draft": "# Full markdown blog content here...",
  "word_count": N
}

CRITICAL: blog_draft MUST be at least 1500 words. Count carefully."""
```

#### cta_prompt (v1)

```python
CTA_SYSTEM = """You are a conversion optimization specialist.
Generate CTAs using psychological triggers, tailored to the brand voice.

CATEGORIES:
- Urgency: Time pressure, deadline-driven
- Scarcity: Limited availability, exclusive access
- Authority: Social proof, expert endorsement, credibility
- Curiosity: Knowledge gap, mystery, intrigue
- Offer: Value proposition, discount, free trial

Each CTA must include:
- text: The CTA copy itself
- context: Where it works best (landing_page, email, ad, popup, social, pricing_page)

Generate at least 2 CTAs per category (10+ total).

BRAND VOICE: Match the provided tone exactly.

Return ONLY valid JSON:
{
  "ctas": {
    "urgency": [{"text": "...", "context": "..."}],
    "scarcity": [{"text": "...", "context": "..."}],
    "authority": [{"text": "...", "context": "..."}],
    "curiosity": [{"text": "...", "context": "..."}],
    "offer": [{"text": "...", "context": "..."}]
  },
  "brand_tone_applied": ["tone1", "tone2"],
  "total_ctas": N
}"""
```

### 3.5 Versioning Support

**Strategy:** In-memory registry with version history. Sprint 3.1C ships with v1 of all prompts. Future sprints can:
1. Register v2 with improved instructions
2. A/B test by setting different active versions per user cohort
3. Roll back to previous versions if quality degrades

**Version metadata stored in generation_metadata:**
```json
{
  "prompt_version": 1,
  "prompt_name": "caption_v1",
  "model": "claude-sonnet"
}
```

This metadata is persisted in CampaignContent.content_json.generation_metadata, enabling analytics to correlate prompt versions with quality outcomes.

---

## 4. Explicit JSON Content Schemas

All schemas are designed to be **frontend-renderable without transformation** — keys map directly to UI components.

### 4.1 CaptionAgent Output Schema

```json
{
  "content_type": "caption",
  "content_json": {
    "captions": {
      "instagram": {
        "text": "Your Instagram caption here with emojis 🚀✨...",
        "character_count": 142,
        "hashtag_suggestions": ["#marketing", "#growth", "#ai"],
        "cta": "Link in bio 👆"
      },
      "linkedin": {
        "text": "Professional insight about AI in marketing...",
        "character_count": 280,
        "hashtag_suggestions": ["#B2B", "#SaaS", "#MarketingTech"],
        "cta": "What's your take? Drop a comment below."
      },
      "facebook": {
        "text": "Engaging Facebook caption with a question...",
        "character_count": 200,
        "hashtag_suggestions": ["#digital", "#tips"],
        "cta": "Share if you agree!"
      },
      "tiktok": {
        "text": "Short punchy TikTok caption 🔥",
        "character_count": 80,
        "hashtag_suggestions": ["#fyp", "#viral", "#marketingtok"],
        "cta": "Follow for more 🔥"
      },
      "youtube_shorts": {
        "text": "AI Marketing Tips for 2025 | Quick Guide",
        "character_count": 100,
        "hashtag_suggestions": ["#shorts", "#tutorial", "#marketing"],
        "cta": "Subscribe for daily tips!"
      }
    },
    "brand_tone_applied": ["professional", "witty"],
    "generation_metadata": {
      "model": "claude-sonnet",
      "prompt_version": 1,
      "platforms_count": 5,
      "brand_profile_id": "bp-uuid"
    }
  }
}
```

### 4.2 HashtagAgent Output Schema

```json
{
  "content_type": "hashtags",
  "content_json": {
    "viral_hashtags": [
      {"hashtag": "#MarketingTips", "relevance_score": 85, "trend_score": 92},
      {"hashtag": "#GrowthHacking", "relevance_score": 78, "trend_score": 88},
      {"hashtag": "#AITools", "relevance_score": 82, "trend_score": 95},
      {"hashtag": "#ContentCreator", "relevance_score": 70, "trend_score": 90},
      {"hashtag": "#DigitalMarketing", "relevance_score": 88, "trend_score": 85}
    ],
    "niche_hashtags": [
      {"hashtag": "#SaaSMarketing", "relevance_score": 95, "trend_score": 45},
      {"hashtag": "#B2BContent", "relevance_score": 90, "trend_score": 38},
      {"hashtag": "#MarketingAutomation", "relevance_score": 92, "trend_score": 52},
      {"hashtag": "#ContentStrategy", "relevance_score": 88, "trend_score": 48},
      {"hashtag": "#AIMarketing", "relevance_score": 94, "trend_score": 62}
    ],
    "brand_hashtags": [
      {"hashtag": "#AutoMindAI", "relevance_score": 100, "trend_score": 15},
      {"hashtag": "#AIContentGen", "relevance_score": 88, "trend_score": 42},
      {"hashtag": "#SmartMarketing", "relevance_score": 85, "trend_score": 55},
      {"hashtag": "#MarketingAI", "relevance_score": 92, "trend_score": 68},
      {"hashtag": "#ContentIntelligence", "relevance_score": 96, "trend_score": 35}
    ],
    "platform": "instagram",
    "total_hashtags": 15,
    "generation_metadata": {
      "model": "claude-sonnet",
      "prompt_version": 1,
      "trend_snapshot_id": "ts-uuid",
      "trend_data_cached": true
    }
  }
}
```

### 4.3 AdCopyAgent Output Schema

```json
{
  "content_type": "adcopy",
  "content_json": {
    "frameworks": {
      "pas": {
        "headline": "Tired of wasting hours on content?",
        "primary_text": "Problem: Manual content creation eats 20+ hours weekly. Solution: AI does it in minutes.",
        "description": "AutoMind AI generates weeks of content in minutes. Start free."
      },
      "aida": {
        "headline": "What if your marketing ran itself?",
        "primary_text": "Imagine never staring at a blank page again. 10,000+ marketers already automated.",
        "description": "Join the AI marketing revolution. Free trial, no credit card."
      },
      "problem_aware": {
        "headline": "Your competitors publish 10x more content",
        "primary_text": "You know content matters. There's never enough time. They have AI. You don't. Yet.",
        "description": "Level the playing field with AI-powered content generation."
      },
      "solution_aware": {
        "headline": "AI tools exist — most produce generic slop",
        "primary_text": "You've tried ChatGPT. Generic. AutoMind generates brand-specific, research-backed content.",
        "description": "Not just AI writing. Intelligence-driven marketing content."
      },
      "offer_focused": {
        "headline": "44 marketing assets in one click — Free",
        "primary_text": "Full content bundle: captions, hashtags, ad copy, SEO, CTAs. All brand-aligned.",
        "description": "Start free. No credit card required. Cancel anytime."
      }
    },
    "competitor_angles_used": ["positioning gap", "pricing weakness", "feature limitation"],
    "generation_metadata": {
      "model": "claude-sonnet",
      "prompt_version": 1,
      "frameworks_count": 5,
      "competitor_snapshot_used": true,
      "competitor_count": 3
    }
  }
}
```

### 4.4 SEOAgent Output Schema

```json
{
  "content_type": "seo",
  "content_json": {
    "seo_title": "How AI Marketing Tools Transform Content Strategy in 2025",
    "meta_description": "Discover how AI marketing platforms automate content creation, boost engagement, and drive organic traffic. Complete guide with actionable strategies.",
    "outline": [
      {"heading": "Introduction", "subheadings": ["The content bottleneck problem", "Why AI changes everything"]},
      {"heading": "What Are AI Marketing Tools?", "subheadings": ["Types of AI marketing tools", "Key capabilities"]},
      {"heading": "Top Benefits of AI Content Generation", "subheadings": ["Speed", "Consistency", "Personalization", "Cost efficiency"]},
      {"heading": "How to Choose the Right AI Marketing Tool", "subheadings": ["Must-have features", "Pricing models", "Integration requirements"]},
      {"heading": "Implementation Strategy", "subheadings": ["Getting started", "Measuring ROI", "Scaling content production"]},
      {"heading": "Conclusion", "subheadings": ["Key takeaways", "Next steps"]}
    ],
    "keywords": {
      "primary": "AI marketing tools",
      "secondary": ["content automation", "AI copywriting", "marketing AI platform", "automated content creation"],
      "long_tail": ["best AI tools for social media marketing 2025", "how to automate content creation with AI"]
    },
    "blog_draft": "# How AI Marketing Tools Transform Content Strategy in 2025\n\n## Introduction\n\n### The Content Bottleneck Problem\n\nEvery marketer knows the feeling...\n\n(1500+ words of formatted markdown content)...",
    "word_count": 1650,
    "generation_metadata": {
      "model": "claude-sonnet",
      "prompt_version": 1,
      "max_tokens_used": 8192,
      "trend_keywords_injected": 8,
      "competitor_angles_used": 3,
      "trend_snapshot_id": "ts-uuid"
    }
  }
}
```

### 4.5 CTAAgent Output Schema

```json
{
  "content_type": "cta",
  "content_json": {
    "ctas": {
      "urgency": [
        {"text": "Start your free trial before midnight", "context": "landing_page"},
        {"text": "This week only: 50% off your first month", "context": "email"},
        {"text": "24 hours left to claim your bonus credits", "context": "popup"}
      ],
      "scarcity": [
        {"text": "Only 50 early-access seats remaining", "context": "landing_page"},
        {"text": "Limited beta access — join the waitlist", "context": "social"},
        {"text": "Exclusive to first 100 subscribers", "context": "email"}
      ],
      "authority": [
        {"text": "Join 10,000+ marketers who switched to AI", "context": "landing_page"},
        {"text": "Recommended by industry leaders at HubSpot", "context": "ad"},
        {"text": "See why Forbes called it 'the future of marketing'", "context": "social"}
      ],
      "curiosity": [
        {"text": "See what 44 AI-generated assets look like →", "context": "email"},
        {"text": "What happens when you automate your content?", "context": "ad"},
        {"text": "The marketing hack your competitors don't want you to know", "context": "social"}
      ],
      "offer": [
        {"text": "Get your first content bundle free", "context": "landing_page"},
        {"text": "No credit card required — start generating now", "context": "pricing_page"},
        {"text": "Free plan includes 100 credits monthly", "context": "landing_page"}
      ]
    },
    "brand_tone_applied": ["professional", "witty"],
    "total_ctas": 15,
    "generation_metadata": {
      "model": "claude-sonnet",
      "prompt_version": 1,
      "adcopy_context_used": true,
      "brand_profile_id": "bp-uuid"
    }
  }
}
```

### 4.6 Enhanced Validation Output Schema

```json
{
  "quality_score": 85,
  "dimensions": {
    "readability": {"score": 90, "weight": 0.20},
    "marketing_strength": {"score": 82, "weight": 0.25},
    "clarity": {"score": 88, "weight": 0.20},
    "platform_fit": {"score": 85, "weight": 0.20},
    "cta_presence": {"score": 78, "weight": 0.15}
  },
  "issues": [
    "CTA could be more specific to the target action",
    "LinkedIn caption slightly informal for the platform"
  ],
  "recommendations": [
    "Add a specific metric or number to increase credibility",
    "Consider splitting the long sentence in paragraph 3"
  ],
  "passed": true,
  "content_type_evaluated": "caption",
  "dimensions_applicable": ["readability", "marketing_strength", "clarity", "platform_fit", "cta_presence"]
}
```

**Dimension applicability by content_type:**

| Dimension          | caption | hashtags | adcopy | seo | cta |
|--------------------|:-------:|:--------:|:------:|:---:|:---:|
| Readability        | ✓       | ✓        | ✓      | ✓   | ✓   |
| Marketing Strength | ✓       | ✓        | ✓      | ✓   | ✓   |
| Clarity            | ✓       | ✓        | ✓      | ✓   | ✓   |
| Platform Fit       | ✓       | ✓        | ✗      | ✗   | ✗   |
| CTA Presence       | ✓       | ✗        | ✓      | ✓   | ✓   |

When a dimension is N/A, it is excluded from the weighted score calculation and its weight is redistributed proportionally.

---

## 5. Credit Cost Matrix

### 5.1 Individual Agent Costs

| Agent              | Credit Cost | Token Estimate | Justification                                           |
|--------------------|:-----------:|:--------------:|---------------------------------------------------------|
| MarketResearchAgent| 5           | ~2,000 out     | Website scrape + Bedrock Sonnet generation              |
| PersonaAgent       | 5           | ~1,500 out     | Single Sonnet call, moderate structured output          |
| HookAgent          | 5           | ~2,500 out     | Single Sonnet call, 40 items output                     |
| **CaptionAgent**   | **5**       | ~2,000 out     | Sonnet call with 5 platform variations                  |
| **HashtagAgent**   | **3**       | ~1,000 out     | Simpler generation, shorter structured output           |
| **AdCopyAgent**    | **8**       | ~3,000 out     | Complex multi-framework (5 × 3 fields) + competitor context |
| **SEOAgent**       | **10**      | ~6,000 out     | Largest output (1500+ words blog + metadata), max_tokens=8192 |
| **CTAAgent**       | **3**       | ~800 out       | Shorter output, focused generation                      |

### 5.2 Bundle Costs

| Bundle             | Total Credits | Composition                                                        |
|--------------------|:-------------:|--------------------------------------------------------------------|
| Full Analysis      | 15            | Research(5) + Persona(5) + Hooks(5)                                |
| **Full Content Bundle** | **44**   | Research(5) + Persona(5) + Hooks(5) + Captions(5) + Hashtags(3) + AdCopy(8) + SEO(10) + CTA(3) |

### 5.3 Bundle Pricing Justification

**No bundle discount in Sprint 3.1C.** Rationale:
1. **Cost-based pricing**: Each credit maps to real AWS Bedrock costs (~$0.003/credit target margin)
2. **Predictability**: Users can calculate exact costs before executing
3. **No hidden subsidies**: MarketIntelligenceService (trend/competitor generation) is platform infrastructure cost, not billed to users
4. **Validation calls are free**: Claude Haiku validation is absorbed as quality assurance overhead

**Bundle discount strategy (future):**
```python
# constants.py — Sprint 3.2+ consideration
BUNDLE_DISCOUNT_PERCENT = 0  # Set to 10, 15, or 20 for future promotions
BUNDLE_BASE_COST = 44
BUNDLE_DISCOUNTED_COST = int(BUNDLE_BASE_COST * (1 - BUNDLE_DISCOUNT_PERCENT / 100))
```

### 5.4 Future Scaling Strategy

| Sprint | New Agent / Feature            | Estimated Cost | Rationale                      |
|--------|-------------------------------|:--------------:|--------------------------------|
| 3.2    | Video Script Generator         | 12 credits     | Long-form structured output    |
| 3.2    | Storyboard Generator           | 15 credits     | Multi-scene complex output     |
| 4.0    | Growth Intelligence Agent      | 5 credits      | Analysis, not generation       |
| 5.0    | Distribution Engine            | 15 credits     | Multi-platform scheduling      |
| 6.0    | Media Buyer AI                 | 20 credits     | Budget allocation + copy gen   |

Credit costs scale with:
- Output token count (primary factor)
- Input context size (secondary factor)
- Retry probability (agents with complex validation may need regeneration)

---

## 6. CampaignContent Storage Strategy

### 6.1 Content Types (complete registry)

| content_type | Agent Source          | Introduced | Description                         |
|--------------|----------------------|------------|-------------------------------------|
| `research`   | MarketResearchAgent  | Sprint 3.1A| Market research output              |
| `persona`    | PersonaAgent         | Sprint 3.1A| Audience persona profiles           |
| `hooks`      | HookAgent            | Sprint 3.1A| 40 marketing hooks                  |
| `caption`    | CaptionAgent         | Sprint 3.1C| Platform-specific captions          |
| `hashtags`   | HashtagAgent         | Sprint 3.1C| Categorized hashtags with scores    |
| `adcopy`     | AdCopyAgent          | Sprint 3.1C| Multi-framework ad copy             |
| `seo`        | SEOAgent             | Sprint 3.1C| SEO content package + blog draft    |
| `cta`        | CTAAgent             | Sprint 3.1C| Categorized calls-to-action         |

### 6.2 Indexing Strategy

```sql
-- Existing indexes (Sprint 3.1A):
CREATE INDEX ix_campaign_content_user_id ON campaign_content(user_id);
CREATE INDEX ix_campaign_content_campaign_id ON campaign_content(campaign_id);
CREATE INDEX ix_campaign_content_content_type ON campaign_content(content_type);

-- New indexes (Sprint 3.1C):
CREATE INDEX ix_campaign_content_bundle_id ON campaign_content(bundle_id);
CREATE INDEX ix_campaign_content_quality_score ON campaign_content(quality_score);
CREATE INDEX ix_campaign_content_created_at ON campaign_content(created_at);

-- Composite indexes for common queries:
CREATE INDEX ix_campaign_content_user_type ON campaign_content(user_id, content_type);
CREATE INDEX ix_campaign_content_campaign_type ON campaign_content(campaign_id, content_type);
CREATE INDEX ix_campaign_content_bundle_type ON campaign_content(bundle_id, content_type);
```

### 6.3 Query Patterns

| Query Pattern                           | Index Used                          | Use Case                          |
|-----------------------------------------|-------------------------------------|-----------------------------------|
| All content for a user                  | ix_campaign_content_user_id         | User dashboard                    |
| All content for a campaign              | ix_campaign_content_campaign_id     | Campaign detail view              |
| All content of a type for a user        | ix_campaign_content_user_type       | "Show me all my captions"         |
| All content in a bundle                 | ix_campaign_content_bundle_id       | Bundle detail view                |
| Specific type in a bundle               | ix_campaign_content_bundle_type     | "Show captions from bundle X"     |
| Highest quality content                 | ix_campaign_content_quality_score   | "Best content" sorting            |
| Recent content                          | ix_campaign_content_created_at      | Activity feed, chronological      |

### 6.4 Searchability

Content searchability via JSON fields (PostgreSQL JSONB operators):

```sql
-- Find captions mentioning a keyword:
SELECT * FROM campaign_content 
WHERE content_type = 'caption' 
AND content_json::jsonb -> 'captions' -> 'instagram' ->> 'text' ILIKE '%keyword%';

-- Find hashtags with high trend scores:
SELECT * FROM campaign_content
WHERE content_type = 'hashtags'
AND EXISTS (
  SELECT 1 FROM jsonb_array_elements(content_json::jsonb -> 'viral_hashtags') elem
  WHERE (elem ->> 'trend_score')::int > 80
);
```

**Note:** For Sprint 3.1C, JSON field searches are sufficient. Sprint 4+ may introduce a dedicated full-text search index or ElasticSearch integration if query volume justifies it.

### 6.5 Future Analytics Compatibility

Every CampaignContent record includes:
- `quality_score`: Enables quality-over-time analytics
- `content_type`: Enables per-type performance analysis
- `bundle_id`: Enables bundle-level ROI analysis
- `campaign_id`: Enables campaign-level attribution
- `created_at`: Enables time-series analysis
- `content_json.generation_metadata`: Enables model/prompt version correlation

---

## 7. Creative Studio Compatibility (Sprint 3.2)

### 7.1 How Content Agents Feed Creative Studio

| Agent Output     | Creative Studio Consumer              | Data Flow                                          |
|------------------|----------------------------------------|----------------------------------------------------|
| CaptionAgent     | Video Script Generator                 | caption.text → script opening/closing narration    |
| CaptionAgent     | Social Post Editor                     | caption per platform → pre-populated fields        |
| HookAgent        | Storyboard Generator                   | hooks → scene openers, attention-grabbers          |
| CTAAgent         | Video CTA Overlay Generator            | cta.text → overlay text, cta.context → placement  |
| AdCopyAgent      | Ad Creative Builder                    | headline → creative headline, primary_text → body  |
| SEOAgent         | Blog Post Editor                       | blog_draft → pre-populated editor content          |

### 7.2 Design Decisions for Zero-Refactor Integration

1. **Stable content_json schemas**: Frontend and Creative Studio can build UI components against the schemas defined in Section 4 without migration risk.
2. **`context` field on CTAs**: Tells Creative Studio WHERE to place the CTA (overlay position, button text, email subject).
3. **`platform` field on captions**: Tells Creative Studio WHICH template to use.
4. **`generation_metadata.brand_profile_id`**: Allows Creative Studio to pull matching brand colors/fonts.
5. **ContentBundle as project root**: Creative Studio can use `bundle_id` to load all related content for a single creative project.

### 7.3 UGC Generator Integration

The UGC (User-Generated Content) Generator in Sprint 3.2 will consume:
- `hooks.curiosity_hooks[0].hook` → Video opening script
- `captions.tiktok.text` → TikTok video description
- `ctas.curiosity[0].text` → Video ending CTA
- `brand_tone_applied` → Voice tone selection for TTS

No schema changes needed — all data is already structured for direct consumption.

---

## 8. Asset Library Compatibility (Sprint 3.3)

### 8.1 ContentBundle as Asset Group

```
Asset Library hierarchy:
├── Campaign
│   ├── ContentBundle (= asset group)
│   │   ├── CampaignContent (type=caption)    → Text Asset
│   │   ├── CampaignContent (type=hashtags)   → Text Asset
│   │   ├── CampaignContent (type=adcopy)     → Text Asset
│   │   ├── CampaignContent (type=seo)        → Text Asset + Document Asset
│   │   ├── CampaignContent (type=cta)        → Text Asset
│   │   └── [Future: Video, Image, Voiceover] → Media Assets
```

### 8.2 Design Decisions

1. **No new FK on Asset model**: Asset Library references CampaignContent.id as `source_content_id` (added in Sprint 3.3, not 3.1C).
2. **content_type as asset filter**: Asset Library queries `SELECT * FROM campaign_content WHERE bundle_id = ? AND content_type IN (?)`.
3. **quality_score as sort criteria**: Asset Library can sort by quality ("Show best content first").
4. **Immutable content**: CampaignContent records are never updated after creation. New generations create new records. This prevents asset reference breakage.

### 8.3 Export Compatibility

Content schemas support direct export:
- `captions.instagram.text` → Copy to clipboard / export as .txt
- `seo.blog_draft` → Export as .md or .html
- `adcopy.frameworks.pas` → Export as ad spec CSV (headline, primary_text, description columns)
- `hashtags.viral_hashtags` → Export as hashtag list (.txt, one per line)

---

## 9. Social Publishing Compatibility (Sprint 3.4)

### 9.1 Content → Publishing Flow

```
┌──────────────────────┐         ┌──────────────────────┐
│   CampaignContent    │         │      SocialPost      │
│   (source of truth)  │────────▶│  (publishing record) │
│                      │  READ   │                      │
│  bundle_id           │         │  source_content_id   │  ← Added Sprint 3.4
│  content_type        │         │  platform            │
│  content_json        │         │  caption             │  ← Copied from content_json
│                      │         │  hashtags            │  ← Copied from content_json
│  NEVER WRITTEN TO    │         │  status (draft|      │
│  BY PUBLISHER        │         │   scheduled|posted)  │
└──────────────────────┘         └──────────────────────┘
```

### 9.2 Platform-Specific Publishing

| Platform       | Source Data                                    | SocialPost Fields              |
|----------------|------------------------------------------------|--------------------------------|
| Instagram      | captions.instagram.text + hashtags.viral[0:5]  | caption, hashtags, media_url   |
| LinkedIn       | captions.linkedin.text                         | caption, article_url           |
| Facebook       | captions.facebook.text + hashtags.niche[0:3]   | caption, link_preview          |
| TikTok         | captions.tiktok.text + hashtags.viral[0:8]     | caption, video_url             |
| YouTube Shorts | captions.youtube_shorts.text                   | title, description             |

### 9.3 Design Decisions

1. **One-way data flow**: CampaignContent → SocialPost (read-only). Publisher NEVER modifies CampaignContent.
2. **No duplication at generation time**: Content lives in CampaignContent. SocialPost copies the relevant fields at publish-time.
3. **Platform field already exists**: CaptionAgent outputs are keyed by platform, enabling direct lookup.
4. **Hashtag merging**: Publisher can merge viral + niche hashtags up to platform limit (Instagram: 30, TikTok: 15, LinkedIn: 5).
5. **Scheduling support**: SocialPost.scheduled_at allows future publishing without affecting source content.

---

## 10. Analytics Compatibility (Sprint 3.5)

### 10.1 Performance Measurement Design

Analytics correlates content quality with real-world performance:

```
┌─────────────────┐     ┌─────────────────────┐     ┌──────────────────┐
│CampaignContent  │     │   SocialPost        │     │ EngagementMetric │
│                 │     │                     │     │                  │
│ id ─────────────┼────▶│ source_content_id   │────▶│ post_id          │
│ quality_score   │     │ platform            │     │ likes            │
│ content_type    │     │ posted_at           │     │ comments         │
│ bundle_id       │     │                     │     │ shares           │
│ validation_json │     │                     │     │ impressions      │
│                 │     │                     │     │ ctr              │
│                 │     │                     │     │ conversions      │
└─────────────────┘     └─────────────────────┘     └──────────────────┘
```

### 10.2 Measurable Metrics by Content Type

| Content Type | Key Metrics                              | Correlation Target            |
|--------------|------------------------------------------|-------------------------------|
| caption      | Engagement rate, reach, saves            | quality_score vs engagement   |
| hashtags     | Hashtag impressions, discovery reach     | trend_score vs actual reach   |
| adcopy       | CTR, CPC, conversion rate               | framework comparison          |
| seo          | Organic traffic, SERP position, dwell time| word_count vs ranking        |
| cta          | Click-through rate, conversion rate      | category vs conversion        |

### 10.3 Analytics-Ready Data Points

Already available in Sprint 3.1C schemas (no future migration needed):

1. **quality_score** → Correlate with engagement (does higher score = better performance?)
2. **validation_json.dimensions** → Per-dimension correlation (does "platform_fit" predict engagement?)
3. **content_json.generation_metadata.prompt_version** → A/B test prompt effectiveness
4. **bundle_id** → Bundle-level ROI (44 credits → how much revenue/engagement?)
5. **content_json.character_count** → Optimal length analysis per platform
6. **content_json.hashtag_suggestions / viral_hashtags** → Hashtag performance tracking
7. **content_json.frameworks.{name}** → Which ad framework converts best?
8. **content_json.word_count** → SEO content length vs ranking correlation

---

## 11. Quality Scoring Framework

### 11.1 Agent Quality Score

Each agent's output is scored by Claude Haiku against applicable dimensions:

```python
# Enhanced validation system prompt (expanded):
ENHANCED_VALIDATION_SYSTEM = """Evaluate the marketing content against these dimensions.
Score each applicable dimension 0-100.

DIMENSIONS:
1. Readability (weight: 0.20): Is the message immediately understandable?
2. Marketing Strength (weight: 0.25): Does it create desire, urgency, or action?
3. Clarity (weight: 0.20): Is the value proposition clear and unambiguous?
4. Platform Fit (weight: 0.20): Is the content appropriate for its target platform?
5. CTA Presence (weight: 0.15): Does it include a compelling call to action?

Return JSON:
{
  "quality_score": <weighted average of applicable dimensions>,
  "dimensions": {
    "<dim_name>": {"score": <0-100>, "weight": <float>}
  },
  "issues": [...],
  "recommendations": [...]
}

If a dimension is not applicable (e.g. platform_fit for SEO), omit it
and redistribute its weight proportionally among remaining dimensions."""
```

### 11.2 Bundle Quality Score

Computed after all agents complete:

```python
bundle.avg_quality_score = mean([agent.quality_score for agent in completed_agents])
bundle.min_quality_score = min([agent.quality_score for agent in completed_agents])
bundle.quality_breakdown = {
    "research": 88,
    "persona": 85,
    "hooks": 82,
    "captions": 90,
    "hashtags": 87,
    "adcopy": 84,
    "seo": 79,
    "cta": 86
}
```

### 11.3 Validation Rules

| Rule                         | Threshold | Action                                    |
|------------------------------|:---------:|-------------------------------------------|
| Individual agent score       | < 80      | Regenerate once                           |
| Retry score                  | < 80      | Persist with validation_passed=0          |
| Bundle average               | < 70      | Flag bundle for manual review             |
| Any agent score              | < 50      | Log critical warning, alert ops           |

### 11.4 Regeneration Thresholds

```python
QUALITY_THRESHOLD = 80       # Below this → regenerate
MAX_REGENERATION_ATTEMPTS = 1 # Maximum retries before persisting anyway
CRITICAL_QUALITY_THRESHOLD = 50  # Below this → log critical alert
BUNDLE_REVIEW_THRESHOLD = 70     # Bundle avg below this → flag
```

### 11.5 Growth Intelligence Dashboard Support (Sprint 4)

The quality framework supports future Growth Intelligence dashboards:
- **Quality trend over time**: Track avg_quality_score per bundle over weeks/months
- **Agent performance**: Which agent consistently scores lowest? (improvement target)
- **Prompt version comparison**: v1 vs v2 quality scores
- **Industry variation**: Does quality vary by industry? (e.g., SaaS vs ecommerce)
- **User cohort analysis**: Free tier vs paid tier quality differences

---

## 12. ContentBundleOrchestrator Design

### 12.1 Module Location

```
backend/app/services/agents/content_bundle_orchestrator.py
```

### 12.2 Sequence Diagram

```
Client                 Orchestrator          AgentRunner         Agent            DB
  │                        │                     │                 │               │
  │ POST /full-content-bundle                    │                 │               │
  │───────────────────────▶│                     │                 │               │
  │                        │                     │                 │               │
  │                        │ CREATE ContentBundle │                 │               │
  │                        │─────────────────────────────────────────────────────▶│
  │                        │                     │                 │               │
  │                        │ ── Agent 1: Research ──              │               │
  │                        │ execute(research_agent, payload)      │               │
  │                        │────────────────────▶│                 │               │
  │                        │                     │ reserve credits │               │
  │                        │                     │────────────────────────────────▶│
  │                        │                     │ run()           │               │
  │                        │                     │────────────────▶│               │
  │                        │                     │ validate()      │               │
  │                        │                     │────────────────▶│               │
  │                        │                     │ persist()       │               │
  │                        │                     │────────────────▶│──────────────▶│
  │                        │                     │ emit_event()    │               │
  │                        │                     │────────────────▶│──────────────▶│
  │                        │◀────────────────────│ result          │               │
  │                        │                     │                 │               │
  │                        │ ── Agent 2: Persona (with research result) ──        │
  │                        │ ... (same pattern for all 8 agents)  │               │
  │                        │                     │                 │               │
  │                        │ UPDATE ContentBundle (status=completed)│              │
  │                        │─────────────────────────────────────────────────────▶│
  │                        │                     │                 │               │
  │                        │ EMIT content_bundle_completed event   │               │
  │                        │─────────────────────────────────────────────────────▶│
  │                        │                     │                 │               │
  │◀───────────────────────│ FullContentBundleOut│                 │               │
  │                        │                     │                 │               │
```

### 12.3 Failure Handling Sequence

```
  │                        │ ── Agent N fails ──                  │               │
  │                        │────────────────────▶│                 │               │
  │                        │                     │ run() → EXCEPTION               │
  │                        │                     │────────────────▶│               │
  │                        │                     │ refund credits  │               │
  │                        │                     │────────────────────────────────▶│
  │                        │                     │ emit failure event              │
  │                        │                     │────────────────────────────────▶│
  │                        │◀────────────────────│ exception raised│               │
  │                        │                     │                 │               │
  │                        │ HALT — skip agents N+1 through 8     │               │
  │                        │                     │                 │               │
  │                        │ UPDATE ContentBundle (status=partial) │               │
  │                        │─────────────────────────────────────────────────────▶│
  │                        │                     │                 │               │
  │◀───────────────────────│ FullContentBundleOut (partial results)│              │
```

### 12.4 Implementation Pattern

```python
class ContentBundleOrchestrator:
    """
    NOT a BaseAgent subclass. Orchestrates agents via AgentRunner.
    Manages ContentBundle lifecycle independently.
    """

    AGENT_SEQUENCE = [
        ("research", MarketResearchAgent, "research_generated"),
        ("persona", PersonaAgent, "persona_generated"),
        ("hooks", HookAgent, "hooks_generated"),
        ("captions", CaptionAgent, "captions_generated"),
        ("hashtags", HashtagAgent, "hashtags_generated"),
        ("adcopy", AdCopyAgent, "adcopy_generated"),
        ("seo", SEOAgent, "seo_generated"),
        ("cta", CTAAgent, "cta_generated"),
    ]

    async def execute(self, payload: dict, user_id: str, db: AsyncSession) -> dict:
        bundle = ContentBundle(user_id=user_id, ...)
        db.add(bundle)
        await db.commit()

        results = {}
        completed = []

        for agent_name, AgentClass, event_type in self.AGENT_SEQUENCE:
            try:
                agent_payload = self._build_payload(agent_name, payload, results)
                agent = AgentClass(db, user_id)
                runner = AgentRunner(db, user_id)
                result = await runner.execute(agent, agent_payload, campaign_id=payload.get("campaign_id"))
                results[agent_name] = result
                completed.append(event_type)
            except Exception as exc:
                bundle.status = "partial" if completed else "failed"
                bundle.failed_agent = event_type
                bundle.error_message = str(exc)
                break

        bundle.completed_agents = completed
        bundle.total_credits_committed = sum(r.get("credits_committed", 0) for r in results.values())
        # ... compute quality scores ...
        await db.commit()
        return self._build_response(bundle, results)
```

---

## 13. API Endpoint Design

### 13.1 New Endpoints Summary

| Method | Path                                    | Handler                    | Credits | Auth Required |
|--------|----------------------------------------|----------------------------|:-------:|:-------------:|
| POST   | /api/v1/marketing/captions             | run_captions()             | 5       | ✓             |
| POST   | /api/v1/marketing/hashtags             | run_hashtags()             | 3       | ✓             |
| POST   | /api/v1/marketing/adcopy               | run_adcopy()               | 8       | ✓             |
| POST   | /api/v1/marketing/seo                  | run_seo()                  | 10      | ✓             |
| POST   | /api/v1/marketing/cta                  | run_cta()                  | 3       | ✓             |
| POST   | /api/v1/marketing/full-content-bundle  | run_full_content_bundle()  | 44      | ✓             |

### 13.2 Request Schemas

```python
class CaptionRequest(BaseModel):
    snapshot_id: Optional[str] = None            # From prior /research call
    persona_content_id: Optional[str] = None     # From prior /persona call
    hooks_content_id: Optional[str] = None       # From prior /hooks call
    brand_profile_id: Optional[str] = None       # Uses user's default if not specified
    research: Optional[dict] = None              # Inline research data
    personas: Optional[dict] = None              # Inline persona data
    hooks: Optional[dict] = None                 # Inline hooks data
    campaign_id: Optional[str] = None

class HashtagRequest(BaseModel):
    snapshot_id: Optional[str] = None
    platform: str = "instagram"                  # Target platform
    industry: Optional[str] = None               # For TrendSnapshot lookup
    research: Optional[dict] = None
    campaign_id: Optional[str] = None

class AdCopyRequest(BaseModel):
    snapshot_id: Optional[str] = None
    persona_content_id: Optional[str] = None
    hooks_content_id: Optional[str] = None
    industry: Optional[str] = None               # For CompetitorSnapshot lookup
    research: Optional[dict] = None
    personas: Optional[dict] = None
    hooks: Optional[dict] = None
    campaign_id: Optional[str] = None

class SEORequest(BaseModel):
    snapshot_id: Optional[str] = None
    industry: Optional[str] = None
    research: Optional[dict] = None
    campaign_id: Optional[str] = None

class CTARequest(BaseModel):
    persona_content_id: Optional[str] = None
    adcopy_content_id: Optional[str] = None
    brand_profile_id: Optional[str] = None
    personas: Optional[dict] = None
    adcopy: Optional[dict] = None
    campaign_id: Optional[str] = None

class FullContentBundleRequest(BaseModel):
    website_url: Optional[str] = None
    product_name: str
    product_description: Optional[str] = None
    industry: Optional[str] = None
    brand_profile_id: Optional[str] = None
    campaign_id: Optional[str] = None
```

### 13.3 Response Schemas

```python
class CaptionOut(BaseModel):
    content_id: str
    job_id: str
    credits_committed: int
    quality_score: Optional[int] = None
    validation: Optional[ValidationOut] = None
    captions: dict[str, Any]

class HashtagOut(BaseModel):
    content_id: str
    job_id: str
    credits_committed: int
    quality_score: Optional[int] = None
    validation: Optional[ValidationOut] = None
    hashtags: dict[str, Any]
    platform: str
    total_hashtags: int

class AdCopyOut(BaseModel):
    content_id: str
    job_id: str
    credits_committed: int
    quality_score: Optional[int] = None
    validation: Optional[ValidationOut] = None
    frameworks: dict[str, Any]

class SEOOut(BaseModel):
    content_id: str
    job_id: str
    credits_committed: int
    quality_score: Optional[int] = None
    validation: Optional[ValidationOut] = None
    seo_content: dict[str, Any]
    word_count: int

class CTAOut(BaseModel):
    content_id: str
    job_id: str
    credits_committed: int
    quality_score: Optional[int] = None
    validation: Optional[ValidationOut] = None
    ctas: dict[str, Any]
    total_ctas: int

class FullContentBundleOut(BaseModel):
    bundle_id: str
    status: str
    research: Optional[ResearchOut] = None
    personas: Optional[PersonaOut] = None
    hooks: Optional[HookOut] = None
    captions: Optional[CaptionOut] = None
    hashtags: Optional[HashtagOut] = None
    adcopy: Optional[AdCopyOut] = None
    seo: Optional[SEOOut] = None
    cta: Optional[CTAOut] = None
    total_credits_committed: int
    completed_agents: list[str]
    failed_agent: Optional[str] = None
    avg_quality_score: Optional[float] = None
```

---

## 14. Agent Implementation Details

### 14.1 CaptionAgent

**Module:** `backend/app/services/agents/caption_agent.py`

| Property      | Value                |
|---------------|----------------------|
| credit_cost   | 5                    |
| event_type    | "captions_generated" |
| model         | Claude Sonnet        |
| max_tokens    | 4096                 |

**Input Resolution:**
1. Resolve research: snapshot_id → DB lookup OR inline `research` dict
2. Resolve personas: persona_content_id → DB lookup OR inline `personas` dict
3. Resolve hooks: hooks_content_id → DB lookup OR inline `hooks` dict
4. Resolve brand profile: brand_profile_id → DB lookup OR user's default BrandProfile

**Key Behaviors:**
- Generates one caption per platform (5 total)
- Deduplication: Verifies no two captions share >80% text similarity
- BrandProfile tone injected into system prompt context
- Platform norms enforced per prompt guidelines

### 14.2 HashtagAgent

**Module:** `backend/app/services/agents/hashtag_agent.py`

| Property      | Value                 |
|---------------|------------------------|
| credit_cost   | 3                      |
| event_type    | "hashtags_generated"   |
| model         | Claude Sonnet          |
| max_tokens    | 4096                   |

**Input Resolution:**
1. Resolve research: snapshot_id → DB lookup OR inline `research` dict
2. Resolve trend data: industry → MarketIntelligenceService.get_trends()
3. Platform: from request payload (default: "instagram")

**Key Behaviors:**
- Injects TrendSnapshot.hashtags_json and keywords_json into prompt
- Categorizes: viral (high trend_score), niche (high relevance_score), brand (product-specific)
- Minimum 5 hashtags per category (15 total minimum)
- Each hashtag scored 0-100 on both relevance and trend axes

### 14.3 AdCopyAgent

**Module:** `backend/app/services/agents/adcopy_agent.py`

| Property      | Value               |
|---------------|---------------------|
| credit_cost   | 8                   |
| event_type    | "adcopy_generated"  |
| model         | Claude Sonnet       |
| max_tokens    | 4096                |

**Input Resolution:**
1. Resolve research: snapshot_id → DB lookup OR inline `research` dict
2. Resolve personas: persona_content_id → DB lookup OR inline `personas` dict
3. Resolve hooks: hooks_content_id → DB lookup OR inline `hooks` dict
4. Resolve competitor data: industry → MarketIntelligenceService.get_competitors()

**Key Behaviors:**
- Single Bedrock call generates all 5 frameworks
- CompetitorSnapshot weaknesses inform Problem-Aware and Solution-Aware angles
- Character limits enforced: headline(40), primary_text(125), description(90)
- These limits match Meta/Google Ads specifications

### 14.4 SEOAgent

**Module:** `backend/app/services/agents/seo_agent.py`

| Property      | Value           |
|---------------|-----------------|
| credit_cost   | 10              |
| event_type    | "seo_generated" |
| model         | Claude Sonnet   |
| max_tokens    | 8192            |

**Input Resolution:**
1. Resolve research: snapshot_id → DB lookup OR inline `research` dict
2. Resolve trend data: industry → MarketIntelligenceService.get_trends()
3. Resolve competitor data: industry → MarketIntelligenceService.get_competitors()

**Key Behaviors:**
- Elevated max_tokens (8192) for long-form blog content
- TrendSnapshot keywords injected as "trending topics to target"
- CompetitorSnapshot content_opportunities injected as "content gaps to fill"
- Word count validation: if blog_draft < 1500 words, retry once
- SEO title limited to 60 chars, meta description to 160 chars

### 14.5 CTAAgent

**Module:** `backend/app/services/agents/cta_agent.py`

| Property      | Value          |
|---------------|----------------|
| credit_cost   | 3              |
| event_type    | "cta_generated"|
| model         | Claude Sonnet  |
| max_tokens    | 4096           |

**Input Resolution:**
1. Resolve personas: persona_content_id → DB lookup OR inline `personas` dict
2. Resolve ad copy: adcopy_content_id → DB lookup OR inline `adcopy` dict
3. Resolve brand profile: brand_profile_id → DB lookup OR user's default BrandProfile

**Key Behaviors:**
- Generates 2+ CTAs per category (10+ total)
- Each CTA includes `context` field (landing_page, email, ad, popup, social, pricing_page)
- BrandProfile tone/voice injected for brand consistency
- AdCopy frameworks inform psychological angles

---

## 15. Database Migrations

### 15.1 New Table: content_bundles

```sql
CREATE TABLE content_bundles (
    id VARCHAR PRIMARY KEY,
    user_id VARCHAR NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    campaign_id VARCHAR REFERENCES campaigns(id) ON DELETE CASCADE,
    status VARCHAR NOT NULL DEFAULT 'running',
    total_credits_reserved INTEGER DEFAULT 44,
    total_credits_committed INTEGER DEFAULT 0,
    completed_agents JSON,
    failed_agent VARCHAR,
    error_message TEXT,
    avg_quality_score FLOAT,
    min_quality_score INTEGER,
    quality_breakdown JSON,
    input_metadata JSON,
    generation_metadata JSON,
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);
CREATE INDEX ix_content_bundles_user_id ON content_bundles(user_id);
CREATE INDEX ix_content_bundles_campaign_id ON content_bundles(campaign_id);
CREATE INDEX ix_content_bundles_status ON content_bundles(status);
CREATE INDEX ix_content_bundles_created_at ON content_bundles(created_at);
```

### 15.2 Alter Table: campaign_content

```sql
ALTER TABLE campaign_content ADD COLUMN bundle_id VARCHAR REFERENCES content_bundles(id) ON DELETE SET NULL;
CREATE INDEX ix_campaign_content_bundle_id ON campaign_content(bundle_id);
CREATE INDEX ix_campaign_content_quality_score ON campaign_content(quality_score);
CREATE INDEX ix_campaign_content_created_at ON campaign_content(created_at);
CREATE INDEX ix_campaign_content_user_type ON campaign_content(user_id, content_type);
CREATE INDEX ix_campaign_content_campaign_type ON campaign_content(campaign_id, content_type);
```

### 15.3 constants.py Update

```python
AGENT_COSTS = {
    # Existing (Sprint 3.1A)
    "campaign_manager": 50,
    "content_strategist": 10,
    "creative_studio": 30,
    "growth_intelligence": 5,
    "media_buyer": 10,
    "distribution_engine": 15,
    "market_research": 5,
    "persona": 5,
    "hook": 5,
    "full_analysis": 15,
    # Sprint 3.1C agents
    "caption": 5,
    "hashtag": 3,
    "adcopy": 8,
    "seo": 10,
    "cta": 3,
    "full_content_bundle": 44,
}
```

---

## 16. File Structure

```
backend/app/
├── core/
│   └── constants.py                         # MODIFIED: New agent costs
├── models/
│   ├── __init__.py                          # MODIFIED: Import ContentBundle
│   ├── content_bundle.py                    # NEW: ContentBundle model
│   └── marketing.py                         # MODIFIED: bundle_id on CampaignContent
├── routers/
│   └── marketing.py                         # MODIFIED: 6 new endpoints
├── schemas/
│   └── marketing.py                         # MODIFIED: New request/response schemas
├── services/
│   ├── agents/
│   │   ├── base.py                          # UNCHANGED
│   │   ├── runner.py                        # UNCHANGED
│   │   ├── market_research_agent.py         # UNCHANGED
│   │   ├── persona_agent.py                 # UNCHANGED
│   │   ├── hook_agent.py                    # UNCHANGED
│   │   ├── caption_agent.py                 # NEW
│   │   ├── hashtag_agent.py                 # NEW
│   │   ├── adcopy_agent.py                  # NEW
│   │   ├── seo_agent.py                     # NEW
│   │   ├── cta_agent.py                     # NEW
│   │   ├── content_bundle_orchestrator.py   # NEW
│   │   └── validation.py                    # MODIFIED: 5-dimension scoring
│   └── llm/
│       ├── bedrock_provider.py              # UNCHANGED
│       ├── provider_registry.py             # UNCHANGED
│       └── prompt_registry.py               # NEW
```

---

## 17. Future Compatibility Review

### 17.1 Sprint 3.2: Creative Intelligence

| Risk | Mitigation |
|------|-----------|
| Schema breaking changes | Schemas are versioned via generation_metadata.prompt_version |
| Creative Studio needs additional fields | content_json is schemaless JSON — new fields can be added without migration |
| Video scripts need longer content | max_tokens is per-agent configurable in PromptTemplate |
| UGC Generator needs hook + caption combo | ContentBundle groups all related content by bundle_id |

**Verdict:** No architectural risks. Content schemas are additive-only.

### 17.2 Sprint 4: Growth Intelligence

| Risk | Mitigation |
|------|-----------|
| Quality analytics needs historical data | quality_score, validation_json already persisted per content |
| A/B testing needs prompt tracking | generation_metadata.prompt_version already in schema |
| Growth metrics need content correlation | source_content_id on SocialPost enables attribution |
| Dashboard needs bundle aggregation | ContentBundle.quality_breakdown provides pre-computed metrics |

**Verdict:** No architectural risks. Analytics data points are already embedded.

### 17.3 Sprint 5: Distribution Engine

| Risk | Mitigation |
|------|-----------|
| Multi-platform scheduling needs platform-keyed content | CaptionAgent already keys by platform |
| Scheduling needs hashtag limits per platform | HashtagAgent outputs per-platform hashtag sets |
| Distribution needs content versioning | CampaignContent is immutable; new generations = new records |
| Bulk scheduling needs bundle reference | ContentBundle.id enables "publish all from this bundle" |

**Verdict:** No architectural risks. Platform-keyed structure supports distribution natively.

### 17.4 Sprint 6: Media Buyer AI

| Risk | Mitigation |
|------|-----------|
| Ad platforms need specific format compliance | AdCopyAgent already enforces Meta/Google character limits |
| Budget allocation needs performance data | Analytics compatibility (Section 10) provides CTR/CPC correlation |
| A/B creative testing needs variant tracking | Each AdCopyAgent call creates new CampaignContent (versioned by timestamp) |
| Media Buyer needs competitor context | CompetitorSnapshot is independently queryable via MarketIntelligenceService |

**Verdict:** No architectural risks. Ad copy schemas are platform-compliant from day one.

### 17.5 Multi-Tenant SaaS Scalability

| Concern | Mitigation |
|---------|-----------|
| Data isolation | All tables have user_id FK; queries always filter by user_id |
| Query performance at scale | Composite indexes (user_type, campaign_type, bundle_type) |
| Storage growth | content_json is JSON column; PostgreSQL TOAST handles large values |
| Concurrent bundle execution | Each AgentRunner instance operates within a single DB session |
| Rate limiting Bedrock | Per-user credit system naturally throttles API calls |

### 17.6 AWS-Native Deployment

| Component | AWS Service | Notes |
|-----------|-------------|-------|
| LLM Generation | AWS Bedrock (Claude) | Already integrated via BedrockProvider |
| Database | RDS PostgreSQL | Existing; supports JSONB natively |
| Compute | ECS/Fargate | Existing FastAPI deployment |
| Cache (future) | ElastiCache Redis | For session/rate-limit; not needed Sprint 3.1C |
| Search (future) | OpenSearch | For full-text content search; not needed Sprint 3.1C |

---

## 18. Design Constraints and Invariants

1. **No SocialPost writes**: Generated content is NEVER stored in SocialPost. Only CampaignContent.
2. **No AgentRunner modifications**: All new agents use the existing lifecycle unchanged.
3. **No existing agent modifications**: PersonaAgent, HookAgent, MarketResearchAgent untouched.
4. **No credit logic modifications**: CreditService reserve/commit/refund unchanged.
5. **Idempotent agent calls**: Each call creates a new CampaignContent record. No upserts.
6. **Stateless agents**: No state between calls beyond what's in the payload.
7. **Prompt isolation**: All LLM prompts live in PromptRegistry, not hardcoded in agents.
8. **Validation non-blocking**: Haiku API failure → persist with default passing score.
9. **Bundle non-atomic**: Each agent's CampaignContent is committed independently.
10. **Immutable content**: CampaignContent records are never updated after creation.

---

## Error Handling

### Agent-Level Errors

| Error Type              | Handling                                                   |
|-------------------------|-----------------------------------------------------------|
| CreditReservationError  | HTTP 402, no job created, no side effects                  |
| Bedrock API failure     | AgentRunner catches, refunds credits, marks job failed     |
| JSON parse failure      | BedrockProvider retries extraction (3-stage), then raises  |
| Validation API failure  | Default pass (score=75), log warning, continue pipeline    |
| Quality score < 80      | Regenerate once, if still < 80 persist with warnings       |

### Bundle-Level Errors

| Error Type                    | Handling                                                 |
|-------------------------------|----------------------------------------------------------|
| First agent (Research) fails  | Bundle status="failed", return error response            |
| Agent N>1 fails               | Bundle status="partial", return partial results          |
| Credit exhaustion mid-bundle  | Agent N raises CreditReservationError, bundle goes partial|
| Database commit failure       | Log critical, agent already handles via AgentRunner      |

### Error Propagation Rules

1. AgentRunner handles all per-agent error recovery (refund + failure event)
2. ContentBundleOrchestrator catches AgentRunner exceptions to manage bundle state
3. Individual endpoints let AgentRunner exceptions propagate to HTTP 500
4. CreditReservationError always surfaces as HTTP 402

---

## Testing Strategy

### Unit Tests

- Each agent's `run()` method with mocked BedrockProvider
- PromptRegistry registration and retrieval
- ValidationLayer dimension scoring logic
- ContentBundleOrchestrator payload building logic

### Integration Tests

- Full agent lifecycle through AgentRunner (with mocked Bedrock)
- ContentBundle creation and state transitions
- API endpoint request/response validation
- Credit reservation and commit flow

### Property-Based Tests

- Caption deduplication: No two platform captions are identical
- Score range: All quality_scores in [0, 100]
- Hashtag scoring: All relevance_score and trend_score in [0, 100]
- Bundle credit conservation: sum(agent credits) = bundle total
- Content type consistency: Agent always persists correct content_type

---

## Correctness Properties

### Property 1: Credit Conservation
For any full-content-bundle execution, the sum of all committed credits across the bundle's CampaignContent records equals ContentBundle.total_credits_committed.
**Validates: Requirements 7.3**

### Property 2: No Duplicate Platforms
CaptionAgent output contains exactly 5 unique platform keys in content_json.captions (instagram, linkedin, facebook, tiktok, youtube_shorts).
**Validates: Requirements 1.1, 1.3**

### Property 3: Score Range Invariant
All quality_score values persisted in CampaignContent and ContentBundle are integers in [0, 100].
**Validates: Requirements 6.2**

### Property 4: Bundle Completeness
If ContentBundle.status == "completed", then ContentBundle.completed_agents contains exactly 8 entries.
**Validates: Requirements 7.1**

### Property 5: Bundle Partial Consistency
If ContentBundle.status == "partial", then ContentBundle.failed_agent is not null AND len(completed_agents) < 8.
**Validates: Requirements 7.5**

### Property 6: Content Type Consistency
Each agent always persists CampaignContent with its designated content_type string (caption, hashtags, adcopy, seo, cta).
**Validates: Requirements 9.3**

### Property 7: Event Emission Guarantee
Every successful agent execution results in exactly one ActivityEvent with the correct event name.
**Validates: Requirements 10.1**

### Property 8: Regeneration Limit
No agent calls run() more than twice per execution (initial generation + one retry on validation failure).
**Validates: Requirements 6.3**

### Property 9: SEO Word Count Minimum
SEOAgent content_json.word_count is always ≥ 1500.
**Validates: Requirements 4.2**

### Property 10: Hashtag Scoring Range
Every hashtag object produced by HashtagAgent has relevance_score and trend_score in [0, 100].
**Validates: Requirements 2.2**

### Property 11: Ad Copy Character Limits
All AdCopyAgent outputs satisfy: headline ≤ 40 chars, primary_text ≤ 125 chars, description ≤ 90 chars.
**Validates: Requirements 3.2**

### Property 12: CTA Minimum Count
CTAAgent produces ≥ 2 CTAs per category (≥ 10 total across 5 categories).
**Validates: Requirements 5.1**

### Property 13: Bundle Quality Calculation
ContentBundle.avg_quality_score equals the arithmetic mean of all agent quality_scores in the bundle.
**Validates: Requirements 7.1**

### Property 14: Content Immutability
No UPDATE queries are issued on campaign_content rows after the initial INSERT by persist().
**Validates: Requirements 9.3**
