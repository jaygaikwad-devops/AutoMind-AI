# Requirements Document

## Introduction

The Content Intelligence Layer extends the AutoMind AI marketing pipeline beyond hooks into full marketing deliverables. After the existing Research → Persona → Hooks pipeline completes, the system generates platform-specific captions, hashtags, ad copy, SEO content, and calls-to-action. All generated content is persisted in the CampaignContent model, quality-scored via Claude Haiku, and emitted as activity events. A full-content-bundle orchestrator endpoint sequences all eight agents in a single request.

## Glossary

- **Content_Intelligence_Layer**: The set of five new agents (CaptionAgent, HashtagAgent, AdCopyAgent, SEOAgent, CTAAgent) that produce marketing deliverables from upstream research and persona data.
- **CaptionAgent**: An agent that generates platform-specific social media captions for Instagram, LinkedIn, Facebook, TikTok, and YouTube Shorts.
- **HashtagAgent**: An agent that generates categorized hashtags (viral, niche, brand) with relevance and trend scores.
- **AdCopyAgent**: An agent that produces advertising copy using five proven copywriting frameworks (PAS, AIDA, Problem-Aware, Solution-Aware, Offer-Focused).
- **SEOAgent**: An agent that generates search-engine-optimized content including titles, meta descriptions, outlines, keywords, and full blog drafts.
- **CTAAgent**: An agent that generates categorized calls-to-action (Urgency, Scarcity, Authority, Curiosity, Offer).
- **ValidationLayer**: The existing Claude Haiku quality-scoring service that evaluates marketing content and returns a quality score with issues and recommendations.
- **AgentRunner**: The existing orchestration component that manages the agent lifecycle (reserve credits → create job → run → validate → persist → emit → commit).
- **CampaignContent**: The existing database model that stores all agent-produced content as JSON with quality scores and validation results.
- **BrandProfile**: A user-scoped brand identity record containing tone, target audience, and brand voice that is injected into generation prompts.
- **TrendSnapshot**: A cached intelligence record containing trending keywords, hashtags, content formats, and CTA styles per industry.
- **CompetitorSnapshot**: A cached intelligence record containing competitor positioning, strengths, weaknesses, and messaging angles per industry.
- **ResearchSnapshot**: A record containing market research data including company summary, core benefits, keywords, and target audience.
- **ActivityEvent**: A database record emitted when an agent completes or fails, containing user_id, job_id, campaign_id, and metadata.
- **ContentBundleOrchestrator**: The orchestration logic that sequences all eight agents (Research → Persona → Hooks → Captions → Hashtags → Ad Copy → SEO → CTA) in a single request.
- **Platform**: One of the five supported social media platforms: Instagram, LinkedIn, Facebook, TikTok, or YouTube Shorts.
- **Quality_Score**: An integer value from 0 to 100 representing the overall quality rating assigned by the ValidationLayer.

## Requirements

### Requirement 1: Caption Generation

**User Story:** As a marketer, I want platform-specific social media captions generated from my research and brand profile, so that I can post tailored content on each platform without manual rewriting.

#### Acceptance Criteria

1. WHEN a caption generation request is received with a valid ResearchSnapshot, Persona output, Hooks, and BrandProfile, THE CaptionAgent SHALL generate one distinct caption per Platform (Instagram, LinkedIn, Facebook, TikTok, YouTube Shorts).
2. THE CaptionAgent SHALL tailor each caption to the norms of the target Platform (character limits, tone conventions, formatting expectations).
3. THE CaptionAgent SHALL ensure no two platform captions contain identical text.
4. THE CaptionAgent SHALL inject the BrandProfile tone and voice into all generated captions.
5. WHEN caption generation completes, THE CaptionAgent SHALL persist the output as a CampaignContent record with content_type set to "caption".
6. THE CaptionAgent SHALL consume exactly 5 credits per execution.
7. WHEN caption generation completes, THE CaptionAgent SHALL emit a "captions_generated" ActivityEvent containing user_id, job_id, campaign_id, and metadata with content_id and quality_score.

### Requirement 2: Hashtag Generation

**User Story:** As a marketer, I want trending and relevant hashtags categorized by type, so that I can maximize content discoverability on social platforms.

#### Acceptance Criteria

1. WHEN a hashtag generation request is received with a valid TrendSnapshot, ResearchSnapshot, and platform identifier, THE HashtagAgent SHALL generate hashtags categorized into three groups: viral hashtags, niche hashtags, and brand hashtags.
2. THE HashtagAgent SHALL produce each hashtag with a relevance_score (0 to 100) and a trend_score (0 to 100).
3. THE HashtagAgent SHALL inject TrendSnapshot data (trending keywords, hashtags) into the generation prompt.
4. WHEN hashtag generation completes, THE HashtagAgent SHALL persist the output as a CampaignContent record with content_type set to "hashtags".
5. THE HashtagAgent SHALL consume exactly 3 credits per execution.
6. WHEN hashtag generation completes, THE HashtagAgent SHALL emit a "hashtags_generated" ActivityEvent containing user_id, job_id, campaign_id, and metadata with content_id and quality_score.

### Requirement 3: Ad Copy Generation

**User Story:** As a marketer, I want ad copy generated using multiple proven copywriting frameworks, so that I can test different messaging approaches for paid advertising.

#### Acceptance Criteria

1. WHEN an ad copy generation request is received with a valid ResearchSnapshot, Persona output, Hooks, and CompetitorSnapshot, THE AdCopyAgent SHALL generate ad copy using all five frameworks: PAS, AIDA, Problem-Aware, Solution-Aware, and Offer-Focused.
2. THE AdCopyAgent SHALL produce Headlines, Primary Text, and Descriptions for each framework.
3. THE AdCopyAgent SHALL inject CompetitorSnapshot data (positioning, weaknesses, messaging angles) into the generation prompt.
4. WHEN ad copy generation completes, THE AdCopyAgent SHALL persist the output as a CampaignContent record with content_type set to "adcopy".
5. THE AdCopyAgent SHALL consume exactly 8 credits per execution.
6. WHEN ad copy generation completes, THE AdCopyAgent SHALL emit an "adcopy_generated" ActivityEvent containing user_id, job_id, campaign_id, and metadata with content_id and quality_score.

### Requirement 4: SEO Content Generation

**User Story:** As a marketer, I want comprehensive SEO content generated from market research and trend data, so that I can publish search-optimized blog posts that drive organic traffic.

#### Acceptance Criteria

1. WHEN an SEO content generation request is received with a valid ResearchSnapshot, TrendSnapshot, and CompetitorSnapshot, THE SEOAgent SHALL generate an SEO Title, Meta Description, Content Outline, Target Keywords list, and a Full Blog Draft.
2. THE SEOAgent SHALL generate a Full Blog Draft of at least 1500 words.
3. THE SEOAgent SHALL inject TrendSnapshot keywords and CompetitorSnapshot data into the generation prompt.
4. WHEN SEO content generation completes, THE SEOAgent SHALL persist the output as a CampaignContent record with content_type set to "seo".
5. THE SEOAgent SHALL consume exactly 10 credits per execution.
6. WHEN SEO content generation completes, THE SEOAgent SHALL emit an "seo_generated" ActivityEvent containing user_id, job_id, campaign_id, and metadata with content_id and quality_score.

### Requirement 5: CTA Generation

**User Story:** As a marketer, I want categorized calls-to-action generated from my persona and brand profile, so that I can use targeted CTAs across my marketing materials.

#### Acceptance Criteria

1. WHEN a CTA generation request is received with a valid Persona output, BrandProfile, and Ad Copy output, THE CTAAgent SHALL generate CTAs categorized into five types: Urgency, Scarcity, Authority, Curiosity, and Offer.
2. THE CTAAgent SHALL inject the BrandProfile tone and voice into all generated CTAs.
3. WHEN CTA generation completes, THE CTAAgent SHALL persist the output as a CampaignContent record with content_type set to "cta".
4. THE CTAAgent SHALL consume exactly 3 credits per execution.
5. WHEN CTA generation completes, THE CTAAgent SHALL emit a "cta_generated" ActivityEvent containing user_id, job_id, campaign_id, and metadata with content_id and quality_score.

### Requirement 6: Enhanced Quality Validation

**User Story:** As a platform operator, I want all generated content validated against expanded marketing quality criteria, so that only high-quality content reaches users.

#### Acceptance Criteria

1. THE ValidationLayer SHALL evaluate all content outputs against five criteria: Readability, Marketing Strength, Clarity, Platform Fit, and CTA Presence.
2. THE ValidationLayer SHALL return a validation result containing a quality_score (0 to 100), an issues list, and a recommendations list.
3. IF a content output receives a quality_score below 80, THEN THE agent SHALL regenerate the content once.
4. IF the regenerated content still receives a quality_score below 80, THEN THE agent SHALL persist the content with validation warnings attached.
5. THE ValidationLayer SHALL use Claude Haiku for all quality scoring evaluations.

### Requirement 7: Full Content Bundle Orchestration

**User Story:** As a marketer, I want to generate a complete content bundle (research through CTAs) in a single request, so that I can produce all marketing assets without managing individual agent calls.

#### Acceptance Criteria

1. WHEN a full-content-bundle request is received, THE ContentBundleOrchestrator SHALL execute all eight agents in sequence: Research, Persona, Hooks, Captions, Hashtags, Ad Copy, SEO, and CTA.
2. THE ContentBundleOrchestrator SHALL pass the output of each agent as input to subsequent agents that depend on it.
3. THE ContentBundleOrchestrator SHALL consume exactly 44 credits total (5 + 5 + 5 + 5 + 3 + 8 + 10 + 3).
4. WHEN the full content bundle completes, THE ContentBundleOrchestrator SHALL emit a "content_bundle_completed" ActivityEvent containing user_id, job_id, campaign_id, and metadata.
5. IF any agent in the sequence fails, THEN THE ContentBundleOrchestrator SHALL halt execution, refund unreserved credits for remaining agents, and return the partial results from completed agents.
6. THE ContentBundleOrchestrator SHALL persist each agent output as a separate CampaignContent record as each agent completes.

### Requirement 8: Individual Content API Endpoints

**User Story:** As a developer, I want individual API endpoints for each content agent, so that I can invoke specific content generation independently of the full bundle.

#### Acceptance Criteria

1. THE System SHALL expose POST /api/v1/marketing/captions to invoke the CaptionAgent independently.
2. THE System SHALL expose POST /api/v1/marketing/hashtags to invoke the HashtagAgent independently.
3. THE System SHALL expose POST /api/v1/marketing/adcopy to invoke the AdCopyAgent independently.
4. THE System SHALL expose POST /api/v1/marketing/seo to invoke the SEOAgent independently.
5. THE System SHALL expose POST /api/v1/marketing/cta to invoke the CTAAgent independently.
6. THE System SHALL expose POST /api/v1/marketing/full-content-bundle to invoke the ContentBundleOrchestrator.
7. IF credit reservation fails for any endpoint, THEN THE System SHALL return HTTP 402 with an error message.
8. IF agent execution fails for any endpoint, THEN THE System SHALL return HTTP 500 with a descriptive error message.

### Requirement 9: Agent Contract Compliance

**User Story:** As a platform architect, I want all new agents to follow the existing BaseAgent contract, so that the system remains consistent and maintainable.

#### Acceptance Criteria

1. THE CaptionAgent, HashtagAgent, AdCopyAgent, SEOAgent, and CTAAgent SHALL each implement the BaseAgent interface with run(), validate(), persist(), and emit_event() methods.
2. THE AgentRunner SHALL execute each new agent through the existing lifecycle without modification (reserve credits → create job → run → validate → persist → emit → commit).
3. THE System SHALL store all generated content exclusively in CampaignContent records, never in SocialPost.
4. THE System SHALL not modify the existing PersonaAgent, HookAgent, MarketResearchAgent, or AgentRunner implementations.
5. THE System SHALL reuse the existing BedrockProvider, LLMProviderRegistry, and ValidationLayer without modification to their interfaces.

### Requirement 10: Activity Event Emission

**User Story:** As a platform operator, I want all content generation activities tracked as events, so that I can monitor usage, debug issues, and provide activity feeds to users.

#### Acceptance Criteria

1. WHEN any content agent completes, THE agent SHALL emit an ActivityEvent with event set to the agent-specific event name (captions_generated, hashtags_generated, adcopy_generated, seo_generated, or cta_generated).
2. THE ActivityEvent SHALL include user_id, job_id, campaign_id, and metadata_json containing content_id and quality_score.
3. WHEN the full content bundle completes, THE ContentBundleOrchestrator SHALL emit a "content_bundle_completed" ActivityEvent in addition to the individual agent events.
4. IF an agent fails during execution, THEN THE AgentRunner SHALL emit a failure ActivityEvent with the event name suffixed by "_failed" and error details in metadata_json.
