# Requirements Document

## Introduction

Sprint 3.0 establishes the Architecture Foundation for AutoMind AI — an autonomous AI marketing SaaS platform. Sprints 1 and 2 delivered the core credit system, CampaignJob/ActivityEvent models, Celery orchestration, the 12-step LLM campaign pipeline, AssetService (S3/CloudFront), and Stripe/Razorpay billing. A codebase audit identified 11 structural gaps (orphaned models, missing FK constraints, un-gated tasks, dead fields, mock WebSocket data) and 8 missing data models required by Sprints 3.1–6.

Sprint 3.0 produces no user-facing features. It produces a set of architecture decisions, migration plans, and interface contracts that every subsequent sprint depends on. The nine deliverables are:

1. Full dependency graph (all model relationships, orphans, missing FKs)
2. Marketing data model review (8 new/extended entities)
3. Alembic migration roadmap (sequential, risk-annotated, rollback-safe)
4. Event architecture (EventEnvelope standard + missing event inventory)
5. Agent architecture (BaseAgent → concrete agent class hierarchy)
6. LLM provider architecture (BaseLLMProvider → Bedrock, OpenAI, Gemini)
7. Credit cost matrix (all agent operations mapped to credit costs)
8. Asset architecture review (final Asset schema)
9. Sprint roadmap (3.0 through Sprint 6)

This requirements document defines what each deliverable must contain and what quality properties it must satisfy, so that implementation teams can execute Sprints 3.1–6 without ambiguity.

---

## Glossary

- **System**: The AutoMind AI backend (FastAPI + PostgreSQL + SQLAlchemy 2 + Celery + Redis)
- **Dependency_Graph**: A directed graph document enumerating all SQLAlchemy model nodes, FK edges, ondelete rules, and orphan nodes
- **Data_Model_Review**: A written decision record that, for each of the 8 target entities, specifies CREATE NEW TABLE or EXTEND EXISTING and provides the authoritative column set
- **Migration_Roadmap**: An ordered sequence of Alembic migration scripts (filenames, descriptions, up/down operations, risk level, rollback procedure)
- **EventEnvelope**: A standardised JSON wrapper for all internal domain events carrying: `event_id`, `event_type`, `schema_version`, `occurred_at`, `user_id`, `aggregate_type`, `aggregate_id`, `payload`
- **Event_Registry**: A versioned catalogue of all defined `event_type` values and their payload schemas
- **Agent_Hierarchy**: A class diagram and contract specification for BaseAgent and all concrete agent subclasses (CampaignManagerAgent, CreativeStudioAgent, ContentStrategistAgent, GrowthIntelligenceAgent, MediaBuyerAgent, DistributionEngineAgent, TrendIntelligenceAgent, VideoIntelligenceAgent)
- **BaseLLMProvider**: An abstract class defining the standard interface all LLM backend adapters must implement
- **LLM_Provider_Registry**: The factory/registry that resolves a provider name to a concrete BaseLLMProvider instance
- **Credit_Cost_Matrix**: A table mapping every agent operation to its credit cost, billing model (flat vs. token-scaled), and justification
- **Asset_Schema**: The authoritative SQLAlchemy column definition for the `assets` table, replacing the current dual Asset + Video tables
- **Sprint_Roadmap**: A document specifying scope, entry/exit criteria, and dependencies for each sprint from 3.0 through Sprint 6
- **CreditService**: The existing reserve/commit/refund credit service in `app/services/billing/credit_service.py`
- **CampaignJob**: The existing job-tracking model in `app/models/campaign.py`
- **ActivityEvent**: The existing audit log model in `app/models/activity.py`
- **Alembic**: The database migration tool used by the project
- **Celery_Worker**: The background task executor defined in `app/workers/celery_app.py`
- **ResearchSnapshot**: New table to persist web scrape output from `analyze_website()`
- **CampaignContent**: New table linking creative output (ad copy, scripts, concepts) to a campaign, job, and asset
- **CampaignMetrics**: New time-series table for campaign performance KPIs
- **PublishResult**: New table recording platform API responses from the `publish_post` task
- **TrendSnapshot**: New table for trending topic intelligence consumed by Sprint 3.2
- **BrandProfile**: New table for persistent brand voice/identity per user
- **Lead**: New table for leads captured from campaigns
- **LeadMagnet**: New table defining lead-capture offers attached to campaigns
- **SocialAccount**: New table for OAuth tokens enabling the Distribution Engine
- **AWS_Bedrock**: AWS managed LLM service targeted in Sprint 3.1

---

## Requirements

---

### Requirement 1: Dependency Graph

**User Story:** As a Principal Software Architect, I want a complete dependency graph of all current SQLAlchemy models, so that I can identify orphaned models, missing FK constraints, and missing `ondelete` rules before writing any migration.

#### Acceptance Criteria

1. THE Dependency_Graph SHALL enumerate every SQLAlchemy model class currently defined across `app/models/__init__.py`, `app/models/campaign.py`, `app/models/billing.py`, `app/models/activity.py`, and `app/models/asset.py`.

2. THE Dependency_Graph SHALL record, for each FK column, its source table, target table, target column, and the `ondelete` rule in effect (or "MISSING" if absent).

3. THE Dependency_Graph SHALL flag the `Video` model (`app/models/__init__.py`) as an orphan because the `Asset` model (`app/models/asset.py`) duplicates its purpose and the `render_video` Celery task writes to `Video` while `AssetService` is never called from that task.

4. THE Dependency_Graph SHALL flag `ActivityEvent.job_id` and `ActivityEvent.campaign_id` as untyped string columns with no FK constraint pointing to `campaign_jobs.id` and `campaigns.id` respectively.

5. THE Dependency_Graph SHALL flag `ActivityEvent.asset_id` and `ActivityEvent.metadata_json` as nullable columns that are never written by any current code path.

6. THE Dependency_Graph SHALL flag `Campaign.product_url` as a dead field — present in the schema and populated on write by `campaigns.py` router, but never read in `orchestrator.py` or any LLM call.

7. THE Dependency_Graph SHALL list all campaign child tables (`personas`, `competitor_insights`, `angles`, `hooks`, `headlines`, `ctas`, `ad_copies`, `creative_concepts`, `video_scripts`, `campaign_scores`) that declare a FK to `campaigns.id` without `ondelete=CASCADE`.

8. THE Dependency_Graph SHALL note that `JOB_STATUS["RESERVED"]` and `JOB_STATUS["REFUNDED"]` are defined in `app/core/constants.py` but are never written to any `CampaignJob.status` column in the current codebase.

9. WHEN the Dependency_Graph is complete, THE System SHALL present it in a structured format containing: a node list (model name, table name, primary key type), an edge list (source_table.column → target_table.column, ondelete), and a separate issues list cross-referencing each gap to the audit item number.

---

### Requirement 2: Marketing Data Model Review

**User Story:** As a Principal Software Architect, I want a formal decision record for each of the 8 target marketing entities, so that engineers know exactly which tables to create or extend and what columns are authoritative before any migration is written.

#### Acceptance Criteria

1. THE Data_Model_Review SHALL contain one entry per entity: `ResearchSnapshot`, `CampaignContent`, `CampaignMetrics`, `PublishResult`, `TrendSnapshot`, `BrandProfile`, `Lead`/`LeadMagnet` (may be combined), and `SocialAccount`.

2. FOR EACH entity entry, THE Data_Model_Review SHALL state the decision as exactly one of: CREATE NEW TABLE or EXTEND EXISTING TABLE, with the target table name if extending.

3. THE Data_Model_Review entry for `ResearchSnapshot` SHALL include at minimum: `id`, `campaign_id` (FK → campaigns.id CASCADE), `url`, `scraped_at` (DateTime), `title`, `meta_description`, `h1_list` (JSON), `h2_list` (JSON), `main_text` (Text), `extracted_ctas` (JSON), `raw_html_s3_key` (nullable String) — to resolve audit gap #11 (scrape output discarded).

4. THE Data_Model_Review entry for `CampaignContent` SHALL include at minimum: `id`, `campaign_id` (FK → campaigns.id CASCADE), `job_id` (FK → campaign_jobs.id SET NULL), `asset_id` (FK → assets.id SET NULL), `content_type` (String: persona | competitor | angle | hook | headline | cta | ad_copy | creative_concept | video_script | campaign_score), `content_ref_id` (String — FK to the relevant child table row), `created_at`.

5. THE Data_Model_Review entry for `CampaignMetrics` SHALL specify `campaign_id`, `metric_date` (Date), `platform` (String), `impressions` (Integer), `clicks` (Integer), `conversions` (Integer), `spend_usd` (Float), `revenue_usd` (Float), with a compound unique constraint on (`campaign_id`, `metric_date`, `platform`).

6. THE Data_Model_Review entry for `PublishResult` SHALL include: `id`, `post_id` (FK → social_posts.id CASCADE), `platform`, `provider_post_id` (String nullable), `http_status_code` (Integer), `response_body` (JSON nullable), `published_at` (DateTime nullable), `error_message` (Text nullable) — to resolve audit gap #2 (publish_post task has no result persistence beyond SocialPost.status).

7. THE Data_Model_Review entry for `SocialAccount` SHALL include: `id`, `user_id` (FK → users.id CASCADE), `platform` (String), `provider_account_id` (String), `access_token_encrypted` (String), `refresh_token_encrypted` (String nullable), `token_expires_at` (DateTime nullable), `scopes` (JSON), `is_active` (Boolean), with a unique constraint on (`user_id`, `platform`, `provider_account_id`).

8. THE Data_Model_Review entry for `BrandProfile` SHALL include: `id`, `user_id` (FK → users.id CASCADE), `brand_name` (String), `tagline` (String nullable), `tone_of_voice` (JSON), `color_palette` (JSON), `logo_asset_id` (FK → assets.id SET NULL), `is_default` (Boolean default False), `created_at`, `updated_at`.

9. THE Data_Model_Review entry for `TrendSnapshot` SHALL include: `id`, `captured_at` (DateTime), `platform` (String), `region` (String), `keyword` (String), `rank` (Integer), `volume_score` (Float nullable), `source` (String: google_trends | twitter | tiktok | manual), `metadata_json` (JSON nullable).

10. THE Data_Model_Review entry for `Lead` SHALL include: `id`, `campaign_id` (FK → campaigns.id CASCADE), `lead_magnet_id` (FK → lead_magnets.id SET NULL nullable), `email` (String), `name` (String nullable), `phone` (String nullable), `captured_at` (DateTime), `source_platform` (String nullable), `metadata_json` (JSON nullable).

11. THE Data_Model_Review entry for `LeadMagnet` SHALL include: `id`, `campaign_id` (FK → campaigns.id CASCADE), `title` (String), `magnet_type` (String: ebook | checklist | webinar | trial | coupon), `asset_id` (FK → assets.id SET NULL nullable), `is_active` (Boolean), `created_at`.

---

### Requirement 3: Alembic Migration Roadmap

**User Story:** As a Principal Software Architect, I want an ordered, risk-annotated Alembic migration roadmap, so that the engineering team can execute schema changes incrementally with clear rollback procedures.

#### Acceptance Criteria

1. THE Migration_Roadmap SHALL contain a migration entry for each of the following changes, in dependency order: (a) add FK constraints and `ondelete` rules to existing campaign child tables; (b) add FK and `ondelete` to `ActivityEvent.job_id` and `ActivityEvent.campaign_id`; (c) create `research_snapshots` table; (d) create `campaign_content` table; (e) create `campaign_metrics` table; (f) create `publish_results` table; (g) create `trend_snapshots` table; (h) create `brand_profiles` table; (i) create `leads` and `lead_magnets` tables; (j) create `social_accounts` table; (k) migrate `Video` table data into `assets` table and drop `videos` table; (l) add `is_default` and `updated_at` fields to `brand_profiles`.

2. FOR EACH migration entry, THE Migration_Roadmap SHALL specify: a sequential filename (e.g. `0001_add_campaign_child_cascade.py`), a one-sentence description, the `upgrade()` operations, the `downgrade()` operations, and a risk level of LOW | MEDIUM | HIGH.

3. THE Migration_Roadmap SHALL assign MEDIUM risk to any migration that alters an existing table's FK constraints, and HIGH risk to any migration that drops a table or migrates data between tables.

4. THE Migration_Roadmap entry for migration (k) — Video table retirement — SHALL specify a data-backfill step that inserts one `Asset` row per existing `Video` row with `type='video'`, `provider=NULL`, `s3_key` derived from `Video.url` where parseable, and `status` mapped from `Video.status`, before the DROP TABLE statement in `upgrade()`.

5. WHEN a migration carries HIGH risk, THE Migration_Roadmap SHALL include an explicit rollback procedure describing the exact steps to restore the prior state including any data that would be lost.

6. THE Migration_Roadmap SHALL order migration (a) — campaign child FK/CASCADE additions — before all other migrations, because subsequent migrations that create `CampaignContent` depend on referential integrity being in place.

---

### Requirement 4: Event Architecture

**User Story:** As a Principal Software Architect, I want a standardised EventEnvelope schema and a complete event registry, so that all current and future agent operations emit structured, version-safe events that the WebSocket gateway and audit log can consume without ad-hoc parsing.

#### Acceptance Criteria

1. THE EventEnvelope SHALL contain exactly these top-level fields: `event_id` (UUID string), `event_type` (String from Event_Registry), `schema_version` (integer, starts at 1), `occurred_at` (ISO-8601 UTC datetime string), `user_id` (String), `aggregate_type` (String: campaign | job | asset | social_post | lead | workflow), `aggregate_id` (String), `payload` (JSON object, schema varies per event_type).

2. THE Event_Registry SHALL define event types for every existing activity event string currently written in `celery_app.py` and `campaigns.py`, including at minimum: `campaign.generation.started`, `campaign.generation.completed`, `campaign.generation.failed`, `agent.task.started`, `agent.task.completed`, `agent.task.failed`, `video.render.started`, `video.render.completed`, `video.render.failed`, `post.publish.requested`, `post.publish.completed`, `workflow.execution.started`, `workflow.execution.completed`.

3. THE Event_Registry SHALL define additional event types required by Sprints 3.1–6: `research.snapshot.captured`, `trend.snapshot.captured`, `brand_profile.updated`, `lead.captured`, `social_account.connected`, `social_account.disconnected`, `asset.uploaded`, `asset.deleted`, `credit.reserved`, `credit.committed`, `credit.refunded`.

4. FOR EACH event type, THE Event_Registry SHALL specify: the event_type string, the aggregate_type it applies to, the minimum required payload fields, and the schema_version.

5. THE Event_Registry SHALL resolve audit gap #10 by specifying that THE WebSocket gateway SHALL emit only EventEnvelope-conformant messages sourced from real `ActivityEvent` rows, replacing the current `ws.py` implementation that sends random `engagement` and `leads` mock data.

6. WHEN a new event type is required by a future sprint, THE Event_Registry versioning policy SHALL require incrementing `schema_version` on the affected event type and maintaining the prior schema_version as a supported read path for at least one sprint cycle.

---

### Requirement 5: Agent Architecture

**User Story:** As a Principal Software Architect, I want a concrete agent class hierarchy derived from the existing `BaseAgent` abstract class, so that Sprint 3.1 and beyond can implement agents with a consistent interface for credit gating, job tracking, activity logging, and error handling.

#### Acceptance Criteria

1. THE Agent_Hierarchy SHALL extend the existing `BaseAgent` (`app/services/agents/base.py`) by adding two abstract methods: `credit_cost(self) -> int` (returns the flat credit cost for one execution of this agent) and `event_type_prefix(self) -> str` (returns the dot-namespaced prefix used to construct EventEnvelope `event_type` values, e.g. `"campaign"`).

2. THE Agent_Hierarchy SHALL define a concrete `AgentRunner` utility (not a subclass of BaseAgent) that accepts any `BaseAgent` instance and executes the standard lifecycle: reserve credits → create CampaignJob (status=PENDING) → call `agent.run(payload)` → on success: commit credits + set job status=COMPLETED + emit `{prefix}.task.completed` EventEnvelope → on failure: refund credits + set job status=FAILED + emit `{prefix}.task.failed` EventEnvelope. WHERE `AgentRunner` is not available, THE System SHALL allow agents to execute without credit gating or job tracking rather than blocking execution entirely.

3. THE Agent_Hierarchy SHALL list the following concrete agent classes and their `credit_cost()` return values: `CampaignManagerAgent` (50 credits), `CreativeStudioAgent` (30 credits), `ContentStrategistAgent` (10 credits), `GrowthIntelligenceAgent` (5 credits), `MediaBuyerAgent` (10 credits), `DistributionEngineAgent` (15 credits), `TrendIntelligenceAgent` (8 credits — new for Sprint 3.2), `VideoIntelligenceAgent` (40 credits — new for Sprint 3.3).

4. THE Agent_Hierarchy SHALL specify that `execute_workflow_task` in `celery_app.py` MUST be refactored to route through `AgentRunner`, resolving audit gap #6 (no credit gating on workflow execution).

5. THE Agent_Hierarchy SHALL specify that `render_video` in `celery_app.py` MUST be refactored to route through `AgentRunner` with `VideoIntelligenceAgent`, resolving audit gap #1 (render_video bypasses credit/job/activity system).

6. THE Agent_Hierarchy SHALL specify that each concrete agent's `run()` method receives a typed `AgentPayload` Pydantic model specific to that agent, validated before execution begins, so that invalid payloads are rejected before credits are reserved. IF payload validation fails, THEN THE AgentRunner SHALL refund any reserved credits and set the CampaignJob status to FAILED. IF execution fails after a valid payload has been accepted, THEN THE AgentRunner SHALL NOT refund credits.

---

### Requirement 6: LLM Provider Architecture

**User Story:** As a Principal Software Architect, I want a `BaseLLMProvider` abstract interface and a provider registry, so that the campaign pipeline and future agents can switch between OpenAI, AWS Bedrock, and Google Gemini without changes to calling code.

#### Acceptance Criteria

1. THE BaseLLMProvider SHALL define the following abstract methods: `complete(self, system: str, user: str, response_schema: type[BaseModel]) -> BaseModel` (structured output completion), `embed(self, text: str) -> list[float]` (text embedding), and `provider_id(self) -> str` (property returning a unique provider identifier string).

2. THE LLM_Provider_Registry SHALL be implemented as a factory that resolves a provider name string to a concrete `BaseLLMProvider` instance, with support for at minimum: `"openai"` (wrapping the existing `_call_llm` logic in `app/services/campaigns/llm.py`), `"bedrock"` (stub implementation for Sprint 3.1), `"gemini"` (stub implementation for Sprint 3.1).

3. THE LLM_Provider_Registry SHALL read a `LLM_PROVIDER` configuration value from `app/core/config.py` (defaulting to `"openai"`) to select the active provider, allowing provider switching via environment variable without code changes.

4. THE System SHALL migrate `app/services/campaigns/llm.py` to call `LLM_Provider_Registry.get_provider()` rather than calling `OpenAI()` directly, so that the campaign pipeline is provider-agnostic.

5. WHERE `"bedrock"` is the active provider, THE BaseLLMProvider implementation SHALL route requests to AWS Bedrock's `invoke_model` API using the `boto3` client already present in the project, with the model ID configurable via `BEDROCK_MODEL_ID` in `app/core/config.py`. THE Bedrock provider SHALL use the existing boto3 client instance rather than creating its own, and SHALL NOT make Bedrock API calls when a provider other than `"bedrock"` is active.

6. THE BaseLLMProvider SHALL define a `supports_structured_output(self) -> bool` method that returns True only for providers that natively support structured JSON output (currently only OpenAI), enabling the calling code to apply a JSON-extraction fallback for providers that do not.

---

### Requirement 7: Credit Cost Matrix

**User Story:** As a Principal Software Architect, I want a complete credit cost matrix mapping all agent operations to credit costs and billing models, so that the CreditService reserve/commit/refund cycle applies consistent, auditable charges across all current and planned operations.

#### Acceptance Criteria

1. THE Credit_Cost_Matrix SHALL contain one row per billable operation, covering all keys currently defined in `AGENT_COSTS` in `app/core/constants.py` plus all agent classes defined in Requirement 5.

2. FOR EACH row, THE Credit_Cost_Matrix SHALL specify: operation name, agent class, flat credit cost, billing model (FLAT | TOKEN_SCALED), credit cost justification, and the sprint in which the operation becomes active.

3. THE Credit_Cost_Matrix SHALL assign the following flat costs as the authoritative values that supersede any ad-hoc values in the codebase: `campaign_manager` = 50, `content_strategist` = 10, `creative_studio` = 30, `growth_intelligence` = 5, `media_buyer` = 10, `distribution_engine` = 15, `trend_intelligence` = 8, `video_intelligence` = 40.

4. THE Credit_Cost_Matrix SHALL specify that TOKEN_SCALED billing applies to Bedrock and Gemini providers, where the credit cost is computed as `ceil(input_tokens / 1000) + ceil(output_tokens / 500)` with a minimum charge of 1 credit, and that the `CreditService` reserve step SHALL use the agent's flat cost as an upper-bound reservation, with a true-up commit at task completion.

5. THE Credit_Cost_Matrix SHALL document that `JOB_STATUS["RESERVED"]` and `JOB_STATUS["REFUNDED"]` constants (currently defined but never written) MUST be used by `CreditService` to set `CampaignJob.status` during the reserve and refund lifecycle phases respectively, resolving audit gap #9.

6. THE Credit_Cost_Matrix SHALL specify that `ActivityEvent.credits_used` MUST be populated with the actual committed credit amount (post true-up for TOKEN_SCALED operations), not the reserved amount, in all Celery tasks.

---

### Requirement 8: Asset Architecture Review

**User Story:** As a Principal Software Architect, I want an authoritative Asset schema that consolidates the `Asset` and `Video` models into a single table, so that `render_video`, `AssetService`, and all future media-generation agents write to one consistent storage record.

#### Acceptance Criteria

1. THE Asset_Schema SHALL declare the `assets` table as the sole canonical storage record for all media assets (video, image, voiceover, thumbnail, campaign_export), and SHALL specify that the `videos` table is deprecated and must be retired via the Migration_Roadmap migration (k).

2. THE Asset_Schema SHALL include the following columns not currently present in `app/models/asset.py`: `file_size_bytes` (Integer nullable), `mime_type` (String nullable), `width_px` (Integer nullable), `height_px` (Integer nullable), `frame_rate` (Float nullable), `azure_blob_url` (String nullable — for backward-compat migration of existing Video.url values), `external_job_id` (String nullable — for tracking provider-side generation job IDs such as Kling or Runway job references).

3. THE Asset_Schema SHALL specify that `Asset.provider` MUST be constrained to the set of known provider identifiers registered in `ProviderFactory`: `kling`, `runway`, `azure_speech`, `elevenlabs`, `openai`, `bedrock`, `pexels`, `manual_upload`, with NULL permitted for assets not generated by an external provider.

4. THE Asset_Schema SHALL specify that the `render_video` task MUST write an `Asset` row with `type='video'` and `status='processing'` before beginning render, and update `status='ready'` with `cdn_url` populated upon successful upload, resolving audit gap #1 (render_video bypasses the Asset model entirely).

5. THE Asset_Schema SHALL specify that `ActivityEvent.asset_id` MUST be populated as a proper FK reference to `assets.id` (with `ondelete=SET NULL`) whenever an event relates to an asset, resolving audit gap #4.

6. THE Asset_Schema SHALL specify that thumbnails are stored as a separate `Asset` row with `type='thumbnail'` and a `parent_asset_id` FK column (self-referential, nullable, `ondelete=SET NULL`), rather than the current pattern of storing `thumbnail_s3_key` and `thumbnail_url` as scalar columns on the parent asset row.

---

### Requirement 9: Sprint Roadmap

**User Story:** As a Principal Software Architect, I want a sprint-by-sprint roadmap from Sprint 3.0 through Sprint 6 with scope, entry criteria, exit criteria, and inter-sprint dependencies, so that the engineering team and stakeholders have a shared execution plan.

#### Acceptance Criteria

1. THE Sprint_Roadmap SHALL contain one section per sprint: Sprint 3.0 (Architecture Foundation), Sprint 3.1 (AWS Bedrock Intelligence Layer), Sprint 3.2 (Trend Intelligence), Sprint 3.3 (Video Intelligence), Sprint 4 (Growth Intelligence), Sprint 5 (Distribution Engine), Sprint 6 (Media Buyer AI).

2. FOR EACH sprint section, THE Sprint_Roadmap SHALL specify: sprint name, primary deliverables (bullet list), entry criteria (what must be true before this sprint can begin), exit criteria (what must be true for this sprint to be considered complete), and dependencies on prior sprint deliverables.

3. THE Sprint_Roadmap entry for Sprint 3.1 SHALL specify that the entry criterion requires: all Migration_Roadmap migrations 0001 through 0003 applied successfully to staging, `BaseLLMProvider` interface implemented, and Bedrock stub provider registered in `LLM_Provider_Registry`.

4. THE Sprint_Roadmap entry for Sprint 3.2 SHALL specify that the entry criterion requires Sprint 3.1 exit criteria met plus `TrendSnapshot` table created and `TrendIntelligenceAgent` class stubbed.

5. THE Sprint_Roadmap entry for Sprint 3.3 SHALL specify that the entry criterion requires Sprint 3.1 exit criteria met plus `Asset` table consolidated (migration k complete) and `VideoIntelligenceAgent` class stubbed with `AgentRunner` integration.

6. THE Sprint_Roadmap entry for Sprint 5 (Distribution Engine) SHALL specify that `SocialAccount` table is created and at least one OAuth provider (Instagram or LinkedIn) is integrated as the entry criterion, and that the exit criterion requires `publish_post` task writing a `PublishResult` row on every execution.

7. THE Sprint_Roadmap entry for Sprint 6 (Media Buyer AI) SHALL specify that the entry criterion requires `CampaignMetrics` table populated with at least 30 days of data from at least one platform integration, and `CreditService` TOKEN_SCALED billing model implemented and tested.

8. THE Sprint_Roadmap SHALL identify the following cross-sprint blockers: (a) Migration_Roadmap completeness blocks all sprints after 3.0; (b) `BaseLLMProvider` interface blocks Sprint 3.1, 3.2, 3.3; (c) `AgentRunner` implementation blocks Sprint 3.3, 4, 5, 6; (d) `SocialAccount` model blocks Sprint 5 and 6.
