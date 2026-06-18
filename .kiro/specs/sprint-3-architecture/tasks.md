# Implementation Plan: Sprint 3.1 AWS Bedrock Intelligence Layer

## Overview

44 implementation tasks derived from the Sprint 3.0 Architecture Foundation spec. Ordered by dependency to minimise migration risk and refactoring. Tasks are grouped into 6 phases: Data Foundation → AWS Bedrock Layer → Agent Framework → Content Generation → Validation Layer → Campaign Orchestration.

**Implementation sequence principle:** Migrations before models. Models before services. Services before agents. Agents before routers. Tests before production wiring.

## Tasks

- [ ] 1. Bootstrap Alembic in the backend project
  - Run `alembic init alembic` inside `backend/`
  - Configure `alembic.ini` to read `sqlalchemy.url` from `settings.SYNC_DATABASE_URL`
  - Configure `alembic/env.py` to import `Base` from `app.models` and set `target_metadata = Base.metadata`
  - Remove `Base.metadata.create_all` from FastAPI lifespan in `app/main.py` — Alembic owns schema from this point
  - Verify `alembic current` runs without error against local Docker Postgres
  - **Complexity:** Small | **Risk:** MEDIUM — removing `create_all` changes startup behaviour; verify against Docker stack before merging
  - _Requirements: R3 (migration infrastructure prerequisite for all migrations)_

- [ ] 2. Migration 0001 — Add ondelete=CASCADE to 10 campaign child tables
  - Create `alembic/versions/0001_add_campaign_child_cascade.py`
  - `upgrade()`: for each of `personas, competitor_insights, angles, hooks, headlines, ctas, ad_copies, creative_concepts, video_scripts, campaign_scores` — drop existing FK constraint, re-add with `ON DELETE CASCADE`
  - `downgrade()`: reverse each — drop CASCADE FK, re-add without `ON DELETE` rule
  - Verify constraint names via `pg_constraint` query after applying
  - **Complexity:** Small | **Risk:** MEDIUM — alters live FK constraints; run on staging first
  - _Requirements: R3.1a, R3.6 (must be first migration; CampaignContent depends on this integrity)_


- [ ] 3. Migration 0002 — Add FK constraints to ActivityEvent.job_id, campaign_id, asset_id
  - Create `alembic/versions/0002_activity_event_fk_constraints.py`
  - `upgrade()`: nullify orphaned rows first (`UPDATE activity_events SET job_id = NULL WHERE job_id NOT IN (SELECT id FROM campaign_jobs)`), then add three FK constraints with `ON DELETE SET NULL`
  - `downgrade()`: drop all three FK constraints
  - **Complexity:** Small | **Risk:** MEDIUM — orphaned string values must be nullified before constraint applies; run row-count check first
  - _Requirements: R3.1b — resolves Gaps 4 and 5_

- [ ] 4. Migration 0003 — Create research_snapshots table
  - Create `alembic/versions/0003_create_research_snapshots.py`
  - `upgrade()`: create table with all columns per design spec — `id, campaign_id (FK CASCADE), url, scraped_at, title, meta_description, h1_list, h2_list, main_text, extracted_ctas, raw_html_s3_key`; add index on `campaign_id`
  - `downgrade()`: `DROP TABLE research_snapshots`
  - **Complexity:** Small | **Risk:** LOW — additive only
  - _Requirements: R3.1c, R2.3 — resolves Gap 11_

- [ ] 5. Migration 0004 — Create campaign_content table
  - Create `alembic/versions/0004_create_campaign_content.py`
  - `upgrade()`: create table with `id, campaign_id (FK CASCADE), job_id (FK SET NULL), asset_id (FK SET NULL), content_type, content_ref_id, created_at`; indexes on `campaign_id` and `job_id`
  - `downgrade()`: `DROP TABLE campaign_content`
  - **Complexity:** Small | **Risk:** LOW — additive only
  - _Requirements: R3.1d, R2.4_

- [ ] 6. Migration 0005 — Create campaign_metrics table
  - Create `alembic/versions/0005_create_campaign_metrics.py`
  - `upgrade()`: create table with compound unique index on `(campaign_id, metric_date, platform)`
  - `downgrade()`: `DROP TABLE campaign_metrics`
  - **Complexity:** Small | **Risk:** LOW — additive; Sprint 4 consumer
  - _Requirements: R3.1e, R2.3_

- [ ] 7. Migration 0006 — Create publish_results table
  - Create `alembic/versions/0006_create_publish_results.py`
  - `upgrade()`: create table with `id, post_id (FK → social_posts.id CASCADE), platform, provider_post_id, http_status_code, response_body, published_at, error_message`; index on `post_id`
  - `downgrade()`: `DROP TABLE publish_results`
  - **Complexity:** Small | **Risk:** LOW — additive; Sprint 5 consumer
  - _Requirements: R3.1f, R2.6_


- [ ] 8. Migration 0007 — Create trend_snapshots table
  - Create `alembic/versions/0007_create_trend_snapshots.py`
  - `upgrade()`: create table with `id, captured_at (tz-aware index), platform, region, keyword (index), rank, volume_score, source, metadata_json`
  - `downgrade()`: `DROP TABLE trend_snapshots`
  - **Complexity:** Small | **Risk:** LOW — additive; Sprint 3.2 consumer
  - _Requirements: R3.1g, R2.5_

- [ ] 9. Migration 0008 — Create brand_profiles table
  - Create `alembic/versions/0008_create_brand_profiles.py`
  - `upgrade()`: create table with `id, user_id (FK CASCADE), brand_name, tagline, tone_of_voice, color_palette, logo_asset_id (FK → assets.id SET NULL), is_default, created_at, updated_at`; index on `user_id`
  - `downgrade()`: `DROP TABLE brand_profiles`
  - **Complexity:** Small | **Risk:** LOW — additive
  - _Requirements: R3.1h, R2.8_

- [ ] 10. Migration 0009 — Create lead_magnets and leads tables
  - Create `alembic/versions/0009_create_leads_and_magnets.py`
  - `upgrade()`: create `lead_magnets` first (FK → campaigns.id CASCADE, FK → assets.id SET NULL), then `leads` (FK → campaigns.id CASCADE, FK → lead_magnets.id SET NULL); indexes on `campaign_id` and `leads.email`
  - `downgrade()`: drop `leads` first, then `lead_magnets` (ordering is critical)
  - **Complexity:** Small | **Risk:** LOW — additive; table ordering matters in downgrade
  - _Requirements: R3.1i, R2.10, R2.11_

- [ ] 11. Migration 0010 — Create social_accounts table
  - Create `alembic/versions/0010_create_social_accounts.py`
  - `upgrade()`: create table with `id, user_id (FK CASCADE), platform, provider_account_id, access_token_encrypted, refresh_token_encrypted, token_expires_at, scopes, is_active`; unique index on `(user_id, platform, provider_account_id)`; index on `user_id`
  - Note: token columns hold AES-256-GCM ciphertext — encryption is application-layer only
  - `downgrade()`: `DROP TABLE social_accounts`
  - **Complexity:** Small | **Risk:** LOW — additive; Sprint 5 consumer
  - _Requirements: R3.1j, R2.7_


- [ ] 12. Create all new SQLAlchemy model classes and extend Asset model
  - Create `app/models/research.py` → `ResearchSnapshot`
  - Create `app/models/campaign_content.py` → `CampaignContent`
  - Create `app/models/metrics.py` → `CampaignMetrics`
  - Create `app/models/publish.py` → `PublishResult`
  - Create `app/models/trend.py` → `TrendSnapshot`
  - Create `app/models/brand.py` → `BrandProfile`
  - Create `app/models/lead.py` → `Lead` + `LeadMagnet`
  - Create `app/models/social_account.py` → `SocialAccount`
  - Update `app/models/__init__.py` to import all 8 new model modules
  - Extend `app/models/asset.py`: add 8 new columns (`file_size_bytes, mime_type, width_px, height_px, frame_rate, azure_blob_url, external_job_id, parent_asset_id` self-ref FK) and `CheckConstraint` on `provider`
  - Verify: `from app.models import ResearchSnapshot, CampaignContent, BrandProfile` resolves without error
  - **Complexity:** Medium | **Risk:** LOW — purely additive; existing code unaffected
  - _Requirements: R2 (all 8 entities), R8.2, R8.3, R8.6_

- [ ] 13. Add LLM provider config keys to Settings
  - Open `app/core/config.py`
  - Add `LLM_PROVIDER: str = "openai"` (valid: openai | bedrock | gemini)
  - Add `BEDROCK_MODEL_ID: str = "anthropic.claude-3-sonnet-20240229-v1:0"`
  - Add `BEDROCK_REGION: str = "us-east-1"`
  - Add `GEMINI_API_KEY: str = ""`
  - Update `.env.example` with all four new keys and inline comments
  - **Complexity:** Small | **Risk:** LOW — additive config; defaults preserve existing behaviour
  - _Requirements: R6.3, R6.5_

- [ ] 14. Implement BaseLLMProvider abstract interface and exception classes
  - Create `app/services/llm/` directory with `__init__.py`
  - Create `app/services/llm/base.py` with abstract class `BaseLLMProvider`
  - Define abstract methods: `complete(system, user, response_schema) -> BaseModel`, `embed(text) -> list[float]`; abstract property `provider_id -> str`; abstract method `supports_structured_output() -> bool`
  - Define exception classes in same file: `LLMProviderError(Exception)`, `LLMStructuredOutputError(LLMProviderError)`, `ProviderNotRegisteredError(LLMProviderError)`
  - No implementation logic — interface contract only
  - **Complexity:** Small | **Risk:** LOW — new file; no existing code touched
  - _Requirements: R6.1, R6.6_


- [ ] 15. Implement OpenAIProvider
  - Create `app/services/llm/providers/openai_provider.py`
  - Wrap existing `_call_llm` logic from `app/services/campaigns/llm.py` into `complete()` method
  - `provider_id` property returns `"openai"`; `supports_structured_output()` returns `True`
  - `embed()`: call `client.embeddings.create(model="text-embedding-3-small", input=text)`, return `list[float]`
  - Client instantiated once at class `__init__` using `settings.OPENAI_API_KEY`
  - Error handling: catch `openai.OpenAIError`, wrap and raise as `LLMProviderError`
  - **Complexity:** Small | **Risk:** LOW — wraps existing logic; no behaviour change when `LLM_PROVIDER=openai`
  - _Requirements: R6.1, R6.2_

- [ ] 16. Implement BedrockProvider with JSON extraction fallback
  - Create `app/services/llm/providers/bedrock_provider.py`
  - `provider_id` returns `"bedrock"`; `supports_structured_output()` returns `False`
  - `complete()`: append JSON schema instruction to system prompt (Stage 1 fallback); call `boto3.client("bedrock-runtime", region_name=settings.BEDROCK_REGION).invoke_model()` with `settings.BEDROCK_MODEL_ID`
  - JSON extraction stages: (1) `json.loads(raw)`, (2) regex `{...}` extraction, (3) `response_schema.model_validate()`; on all-fail raise `LLMStructuredOutputError` with raw text preserved
  - `embed()`: call Bedrock Titan Embeddings (`amazon.titan-embed-text-v1`); return vector
  - Boto3 client instantiated once at `__init__` using existing AWS credentials from `config.py`
  - Guard: provider must NOT make any API calls if `settings.LLM_PROVIDER != "bedrock"` — registry enforces this by not calling the provider
  - **Complexity:** Medium | **Risk:** MEDIUM — external API; requires `bedrock:InvokeModel` IAM permission confirmed before Task 32
  - _Requirements: R6.1, R6.5, R6.6_

- [ ] 17. Implement GeminiProvider stub
  - Create `app/services/llm/providers/gemini_provider.py`
  - `provider_id` returns `"gemini"`; `supports_structured_output()` returns `False`
  - `complete()` and `embed()`: both raise `NotImplementedError("GeminiProvider is a Sprint 3.1 stub")`
  - Stub must be registerable — it only raises when called, not when registered
  - **Complexity:** Small | **Risk:** LOW — stub only
  - _Requirements: R6.2_


- [ ] 18. Implement LLMProviderRegistry factory
  - Create `app/services/llm/registry.py`
  - Define `LLMProviderRegistry` with class-level `_registry: dict[str, BaseLLMProvider]`
  - Implement `register(provider_id, provider)`, `get_provider(provider_id)`, `get_active_provider()`
  - `get_active_provider()` reads `settings.LLM_PROVIDER` and calls `get_provider()`; raises `ProviderNotRegisteredError` if unknown
  - In `app/main.py` lifespan: register all three providers at startup; if `settings.LLM_PROVIDER` is not registered, raise at startup and prevent server start
  - Document startup failure behaviour in `.env.example`
  - **Complexity:** Small | **Risk:** MEDIUM — misconfigured `LLM_PROVIDER` prevents app startup; document clearly
  - _Requirements: R6.2, R6.3_

- [ ] 19. Extend BaseAgent with credit_cost() and event_type_prefix() abstract methods
  - Open `app/services/agents/base.py`
  - Add abstract method `credit_cost(self) -> int` with docstring explaining flat reservation semantics
  - Add abstract method `event_type_prefix(self) -> str` with docstring explaining dot-namespace convention
  - Existing abstract methods `run()`, `status()`, `history()` remain unchanged
  - **Complexity:** Small | **Risk:** LOW — purely additive to abstract class with no concrete subclasses yet
  - _Requirements: R5.1_

- [ ] 20. Define EventEnvelope Pydantic schema and Event Registry
  - Create `app/schemas/events.py`
  - Define `AggregateType` as `Literal` with 10 valid values from design spec
  - Define `EventEnvelope(BaseModel)` with all 8 fields: `event_id` (UUID default), `event_type`, `schema_version` (default 1), `occurred_at` (ISO-8601 UTC default), `user_id`, `aggregate_type`, `aggregate_id`, `payload: dict[str, Any]`
  - Define `EVENT_REGISTRY: dict[str, dict]` mapping all 24 event type strings to `{"aggregate_type": ..., "schema_version": 1, "required_payload_fields": [...]}`
  - All 13 existing + 11 new event types from design spec must be present
  - **Complexity:** Small | **Risk:** LOW — new schema file; no existing code changed
  - _Requirements: R4.1, R4.2, R4.3, R4.4_


- [ ] 21. Implement AgentRunner with full 8-step lifecycle
  - Create `app/services/agents/runner.py`
  - Implement `AgentRunner` as a class with static method `execute(agent, db, user_id, payload) -> dict`
  - Step 1 — Payload validation: deserialise payload into agent's typed model; on `ValidationError` raise `PayloadValidationError` — do NOT reserve credits, do NOT create job
  - Step 2 — Reserve credits: call `CreditService.reserve_credits_sync(db, user_id, agent.credit_cost(), job_id=None)`; on `CreditReservationError` re-raise immediately
  - Step 3 — Create CampaignJob: insert with `status=JOB_STATUS["RESERVED"]`, `credits_reserved=agent.credit_cost()`, `job_type=agent.event_type_prefix()`; commit
  - Step 4 — Emit `{prefix}.task.started` ActivityEvent: `credits_used=0`
  - Step 5 — Set RUNNING: `job.status = JOB_STATUS["RUNNING"]`, `started_at=utcnow()`; commit
  - Step 6 — Call `agent.run(validated_payload)`
  - Step 7 — On success: call `CreditService.commit_credits_sync(db, user_id, actual_cost)` where `actual_cost = result.get("credits_used", agent.credit_cost())`; set `job.status = JOB_STATUS["COMPLETED"]`; write ActivityEvent with `credits_used=actual_cost`; commit
  - Step 8 — On failure: call `CreditService.refund_credits_sync(db, user_id, agent.credit_cost())`; set `job.status = JOB_STATUS["REFUNDED"]`, `error_message=str(e)`, `completed_at=utcnow()`; write ActivityEvent with `credits_used=0`; commit; re-raise
  - Return dict with `status, job_id, credits_committed` plus agent result keys
  - **Complexity:** Large | **Risk:** HIGH — central lifecycle coordinator; errors affect all agent executions; must be unit-tested (Task 27) before any production use
  - _Requirements: R5.2, R7.5, R7.6 — resolves Gaps 6 and 9_

- [ ] 22. Implement CampaignManagerAgent
  - Create `app/services/agents/campaign_manager.py`, subclass `BaseAgent`
  - `credit_cost()` returns `50`; `event_type_prefix()` returns `"campaign"`
  - Define `CampaignManagerPayload(BaseModel)`: fields `campaign_id: str`
  - `run(payload)`: call `generate_full_campaign_sync(self.db, payload.campaign_id)`; return `{"campaign_id": payload.campaign_id, "status": "completed"}`
  - `status(task_id)`: query `CampaignJob` by task_id; return status dict
  - `history()`: query `CampaignJob` where `user_id=self.user_id` and `job_type="campaign"`; return list
  - **Complexity:** Medium | **Risk:** MEDIUM — must not double-charge credits; orchestrator must not call `commit_credits_sync` separately (Task 36 removes this)
  - _Requirements: R5.2, R5.3_


- [ ] 23. Implement ContentStrategistAgent with real LLM call
  - Create `app/services/agents/content_strategist.py`, subclass `BaseAgent`
  - `credit_cost()` returns `10`; `event_type_prefix()` returns `"content"`
  - Define `ContentStrategistPayload(BaseModel)`: `topic: str`, `content_type: str` (caption | hook | hashtag | blog), `campaign_id: Optional[str]`
  - `run(payload)`: replace `time.sleep(3)` with real LLM call via `LLMProviderRegistry.get_active_provider().complete()`; return `{"content": generated_text, "content_type": payload.content_type}`
  - `status()` and `history()`: query `CampaignJob` by type `"content"`
  - **Complexity:** Small | **Risk:** LOW — isolated module; old `execute_agent_task` path remains until Task 34
  - _Requirements: R5.3_

- [ ] 24. Implement CreativeStudioAgent stub
  - Create `app/services/agents/creative_studio.py`, subclass `BaseAgent`
  - `credit_cost()` returns `30`; `event_type_prefix()` returns `"creative"`
  - Define `CreativeStudioPayload(BaseModel)`: `prompt: str`, `video_type: str`, `aspect_ratio: str`, `voice: str`
  - `run(payload)`: raise `NotImplementedError("CreativeStudioAgent is implemented in Sprint 3.3 via VideoIntelligenceAgent")`
  - `status()` and `history()`: query `CampaignJob` by type `"creative"`
  - **Complexity:** Small | **Risk:** LOW — stub only; NotImplementedError caught by AgentRunner → REFUNDED job, 0 credits
  - _Requirements: R5.3_

- [ ] 25. Create stubs for remaining 5 agents (Growth, MediaBuyer, Distribution, Trend, Video)
  - Create one file per agent under `app/services/agents/`:
  - `growth_intelligence.py` — cost 5, prefix `"growth"`, Sprint 4.0 note in `run()`
  - `media_buyer.py` — cost 10, prefix `"media_buyer"`, Sprint 6.0 note
  - `distribution_engine.py` — cost 15, prefix `"distribution"`, Sprint 5.0 note
  - `trend_intelligence.py` — cost 8, prefix `"trend"`, Sprint 3.2 note
  - `video_intelligence.py` — cost 40, prefix `"video"`, Sprint 3.3 note
  - Each has a typed `XPayload(BaseModel)` and `run()` raising `NotImplementedError` with sprint target
  - **Complexity:** Small | **Risk:** LOW — stubs only
  - _Requirements: R5.3_

- [ ] 26. Update AGENT_COSTS constants to match authoritative credit cost matrix
  - Open `app/core/constants.py`
  - Update all values: campaign_manager=50, content_strategist=10, creative_studio=30, growth_intelligence=5, media_buyer=10, distribution_engine=15
  - Add new keys: trend_intelligence=8, video_intelligence=40
  - Verify every key has a corresponding concrete agent class in `app/services/agents/`
  - **Complexity:** Small | **Risk:** LOW — constants only
  - _Requirements: R7.3_


- [ ] 27. Migrate llm.py to use LLMProviderRegistry (remove direct OpenAI client)
  - Open `app/services/campaigns/llm.py`
  - Remove module-level `client = OpenAI(api_key=settings.OPENAI_API_KEY)` instantiation
  - Replace `_call_llm()` body entirely: `return LLMProviderRegistry.get_active_provider().complete(system=system, user=prompt, response_schema=response_format)`
  - All 11 `generate_*` functions remain unchanged — they still call `_call_llm()` with identical signatures
  - Verify: with `LLM_PROVIDER=openai`, output is identical to before; with `LLM_PROVIDER=bedrock`, calls route to BedrockProvider
  - **Complexity:** Small | **Risk:** MEDIUM — highest-traffic code path; test both provider paths before merging
  - _Requirements: R6.4_

- [ ] 28. Implement BrandProfile Pydantic schemas and CRUD router
  - Create `app/schemas/brand.py`: `BrandProfileCreate`, `BrandProfileUpdate`, `BrandProfileOut`
  - Create `app/routers/brand.py` with routes: `POST /api/brand-profiles`, `GET /api/brand-profiles`, `GET /api/brand-profiles/{id}`, `PUT /api/brand-profiles/{id}`, `DELETE /api/brand-profiles/{id}`
  - On create/update: enforce one `is_default=True` per user (unset others when setting new default)
  - All routes require `get_current_user` dependency
  - Register router in `app/main.py` at prefix `/api/brand-profiles`
  - **Complexity:** Medium | **Risk:** LOW — standard CRUD
  - _Requirements: R2.8_

- [ ] 29. Inject BrandProfile voice into LLM system prompts in orchestrator
  - Open `app/services/campaigns/orchestrator.py`, function `generate_full_campaign_sync()`
  - After loading the campaign, query `BrandProfile` where `user_id=campaign.user_id` and `is_default=True`
  - If profile found: append to `context` string — brand name, tagline, tone of voice descriptors
  - If no profile: context is unchanged (backward-compatible)
  - **Complexity:** Small | **Risk:** LOW — additive context injection with graceful fallback
  - _Requirements: R2.8 (brand voice active in campaign pipeline)_


- [ ] 30. Add ResearchSnapshot read endpoint to campaigns router
  - Create `app/schemas/research.py`: `ResearchSnapshotOut` Pydantic model
  - Add `GET /api/campaigns/{campaign_id}/research` in `app/routers/campaigns.py`
  - Return all `ResearchSnapshot` rows for a campaign; ownership-check against `current_user.id`
  - No POST/PUT — snapshots are written only by the orchestrator
  - **Complexity:** Small | **Risk:** LOW — read-only endpoint
  - _Requirements: R2.3_

- [ ] 31. Persist ResearchSnapshot in the campaign orchestrator
  - Open `app/services/campaigns/orchestrator.py`, `generate_full_campaign_sync()`
  - After `scraped_data = analyze_website(campaign.website_url)`: create and commit a `ResearchSnapshot` row with all fields from the scrape dict
  - Only persist if `campaign.website_url` is non-null
  - On scrape failure: still persist snapshot row with `main_text` = error message (record of attempt)
  - **Complexity:** Small | **Risk:** LOW — additive DB write; failure logs and continues (does not abort campaign) — resolves Gap 11
  - _Requirements: R3.3, R2.3 — resolves Gap 11_

- [ ] 32. End-to-end Bedrock campaign generation smoke test
  - Set `LLM_PROVIDER=bedrock` in local `.env`
  - Trigger `POST /api/campaigns/analyze` with a real `website_url`
  - Verify all 12 orchestrator steps complete; all 10 child table rows created with non-empty content
  - Confirm `ResearchSnapshot` row written; confirm `ActivityEvent` row written
  - Document any JSON parsing failures from BedrockProvider fallback strategy
  - Prerequisite gate: `bedrock:InvokeModel` IAM permission must be confirmed before this task
  - **Complexity:** Medium | **Risk:** MEDIUM — first real Bedrock API call; may surface IAM/quota/JSON parsing issues
  - _Requirements: R9.3 (Sprint 3.1 exit criteria — Bedrock campaign generation works)_


- [ ] 33. Unit tests — AgentRunner credit lifecycle (all 5 JOB_STATUS transitions)
  - Create `backend/tests/test_agent_runner.py`
  - Mock `CreditService`, `CampaignJob`, `ActivityEvent`; use in-memory SQLite or pure mocks
  - Test reserve path: verify `CampaignJob.status` transitions RESERVED → RUNNING → COMPLETED; verify `commit_credits_sync` called with `agent.credit_cost()`
  - Test refund path: mock `agent.run()` to raise exception; verify RESERVED → RUNNING → REFUNDED; verify `refund_credits_sync` called; verify exception re-raised
  - Test payload validation failure: invalid payload dict; verify `PayloadValidationError` raised; NO job created; NO credits touched
  - Test credit conservation invariant: `credits + credits_reserved` unchanged on REFUNDED path; decreases by `actual_cost` on COMPLETED
  - Test minimum-charge TOKEN_SCALED: `agent.run()` returns `{"credits_used": 1}` below flat cost; verify commit amount is 1 not flat cost
  - Test stub agent `NotImplementedError`: verify it results in REFUNDED job, 0 credits used
  - Minimum: 6 passing test cases — **must pass before Task 39 is merged**
  - **Complexity:** Medium | **Risk:** LOW — pure unit tests
  - _Requirements: R5.2, R7.5, R7.6_

- [ ] 34. Unit tests — TOKEN_SCALED billing formula boundary values
  - Create `backend/tests/test_credit_formula.py`
  - Implement `token_scaled_cost(input_tokens, output_tokens)` as `max(1, ceil(input/1000) + ceil(output/500))`
  - Test: `(0,0)→1`, `(1,0)→1`, `(999,0)→1`, `(1000,0)→1`, `(1001,0)→2`, `(0,499)→1`, `(0,500)→1`, `(0,501)→2`, `(3500,800)→6`, `(100000,50000)→300`
  - If `hypothesis` available: property test that result is always `>= 1` for any non-negative inputs
  - Minimum: 10 parametrised test cases
  - **Complexity:** Small | **Risk:** LOW
  - _Requirements: R7.4_

- [ ] 35. Unit tests — EventEnvelope schema completeness
  - Create `backend/tests/test_event_envelope.py`
  - Test: constructing `EventEnvelope` with required fields produces object with all 8 fields populated
  - Test: `event_id` auto-generates UUID when not provided
  - Test: `occurred_at` auto-generates ISO-8601 UTC string when not provided
  - Test: `schema_version` defaults to 1
  - Test: all 24 event types in `EVENT_REGISTRY` have `aggregate_type` and `required_payload_fields` defined
  - Test: unknown `aggregate_type` value raises `ValidationError`
  - Minimum: 6 test cases
  - **Complexity:** Small | **Risk:** LOW
  - _Requirements: R4.1, R4.4_


- [ ] 36. Unit tests — LLMProviderRegistry resolution and provider contracts
  - Create `backend/tests/test_llm_registry.py`
  - Test: `register()` then `get_provider("openai")` returns `OpenAIProvider` instance
  - Test: `get_active_provider()` with `LLM_PROVIDER="openai"` returns `OpenAIProvider`
  - Test: `get_active_provider()` with `LLM_PROVIDER="bedrock"` returns `BedrockProvider`
  - Test: `get_provider("nonexistent")` raises `ProviderNotRegisteredError`
  - Test: `GeminiProvider.complete()` raises `NotImplementedError`
  - Test: `OpenAIProvider.supports_structured_output()` returns `True`; `BedrockProvider.supports_structured_output()` returns `False`
  - Mock all actual API calls — no real network calls in unit tests
  - Minimum: 6 test cases
  - **Complexity:** Small | **Risk:** LOW
  - _Requirements: R6.1, R6.2, R6.6_

- [ ] 37. Unit tests — BedrockProvider JSON extraction fallback paths
  - Create `backend/tests/test_bedrock_provider.py`
  - Mock `boto3.client("bedrock-runtime").invoke_model()` — no real API calls
  - Test 1: clean JSON response → `model_validate` succeeds → returns correct Pydantic instance
  - Test 2: JSON wrapped in markdown fences ` ```json ... ``` ` → regex extraction + validate succeeds
  - Test 3: prose before JSON object → regex extraction succeeds
  - Test 4: completely unparseable → `LLMStructuredOutputError` raised with raw text in `args[0]`
  - Test 5: empty string response → `LLMStructuredOutputError` raised
  - Minimum: 5 test cases; all mocked
  - **Complexity:** Small | **Risk:** LOW
  - _Requirements: R6.6_

- [ ] 38. Verify ActivityEvent FK constraints on staging database
  - Apply migration 0002 to staging DB
  - Insert `ActivityEvent` with valid `job_id` → succeeds
  - Insert `ActivityEvent` with non-existent `job_id` → FK violation confirmed
  - Delete a `CampaignJob` with `ActivityEvent` rows → verify `job_id` set to NULL (SET NULL behaviour)
  - Delete a `Campaign` with `ActivityEvent` rows → verify `campaign_id` set to NULL
  - Document results as staging verification checklist
  - **Complexity:** Small | **Risk:** LOW — read/write verification; staging only
  - _Requirements: R3.1b_


- [ ] 39. Wire CampaignManagerAgent through AgentRunner in the campaigns router
  - Open `app/routers/campaigns.py`, `POST /analyze`
  - Campaign row is created and committed FIRST (before AgentRunner is called, so it exists when `run()` reads it)
  - Replace direct `CreditService.reserve_credits()` call with: instantiate `CampaignManagerAgent(db, current_user.id)` and call `AgentRunner.execute(agent, db, current_user.id, {"campaign_id": campaign_id})`
  - Remove direct `CampaignJob` insert from router — AgentRunner owns this
  - Remove direct `CreditService.reserve_credits()` call from router — AgentRunner owns this
  - `generate_full_campaign.delay()` is still called inside `CampaignManagerAgent.run()` — the Celery task still exists
  - Verify: `POST /analyze` returns same `CampaignOut` response shape; 402 on insufficient credits still works
  - **Complexity:** Medium | **Risk:** HIGH — changes entry point of most-used API endpoint; test success path and 402 path before deploying
  - _Requirements: R5.2, R5.4_

- [ ] 40. Refactor execute_agent_task Celery task to dispatch through AgentRunner
  - Open `app/workers/celery_app.py`, `execute_agent_task(kind, job_id, payload)`
  - Build agent registry dict mapping kind strings to agent classes
  - Look up agent class, instantiate with `db` and `user_id` (retrieved from pre-existing `CampaignJob` row)
  - Call `AgentRunner.execute(agent, db, user_id, payload or {})`
  - Remove all direct `CreditService.commit/refund` calls — AgentRunner owns these
  - Remove all direct `CampaignJob.status` mutations — AgentRunner owns these
  - Remove all `time.sleep()` placeholders — agent `run()` methods replace them
  - Handle `NotImplementedError` from stub agents gracefully — log warning, do not crash worker
  - **Complexity:** Medium | **Risk:** MEDIUM — refactors live Celery task; must handle stub agent exceptions without crashing worker
  - _Requirements: R5.2, R5.4_

- [ ] 41. Refactor execute_workflow_task to credit-gate through AgentRunner
  - Open `app/workers/celery_app.py`, `execute_workflow_task(workflow_id)`
  - Use `CreativeStudioAgent.credit_cost()` (30) as the proxy cost for workflow execution
  - Wrap the existing render_video call to dispatch through `AgentRunner` with `CreativeStudioAgent`
  - Add `CampaignJob` creation at workflow start (via AgentRunner)
  - Add `ActivityEvent` write on workflow completion and failure (via AgentRunner)
  - Social post creation and `publish_post.delay()` remain as workflow node logic (outside AgentRunner)
  - **Complexity:** Medium | **Risk:** MEDIUM — changes execution path for workflow canvas; prevent double-charge with Task 42
  - _Requirements: R5.4 — resolves Gap 6_


- [ ] 42. Remove double-charge risk from generate_full_campaign Celery task
  - Open `app/workers/celery_app.py`, `generate_full_campaign(campaign_id, job_id)`
  - Remove direct `CreditService.commit_credits_sync()` call — owned by AgentRunner
  - Remove direct `CreditService.refund_credits_sync()` call — owned by AgentRunner
  - Remove direct `CampaignJob.status = "running"` mutation — owned by AgentRunner
  - Remove direct `ActivityEvent` insert at end of task — owned by AgentRunner
  - Task body becomes: load job record → call `generate_full_campaign_sync(db, campaign_id)` → return result dict
  - Error handling: catch exception, log, re-raise — AgentRunner's handler writes failure state
  - Must be deployed atomically with Task 39 to avoid a window where credits are committed twice
  - **Complexity:** Small | **Risk:** MEDIUM — removing credit logic from live task; deploy together with Task 39
  - _Requirements: R7.6 — resolves double-charge risk_

- [ ] 43. Redesign WebSocket gateway to emit real EventEnvelope data
  - Open `app/routers/ws.py`
  - Add JWT auth to WebSocket handshake: read `access_token` cookie or `token` query param; decode via `security.decode_token()`; reject unauthenticated connections with `ws.close(code=4001)`
  - Replace random tick loop: every 2 seconds, query `ActivityEvent` for 20 most recent rows where `user_id = authenticated_user_id`, ordered by `timestamp DESC`
  - Map each `ActivityEvent` row to `EventEnvelope`: `event` → `event_type`, derive `aggregate_type` from event prefix, `aggregate_id` = `campaign_id or job_id or asset_id or user_id`, `payload = {"agent": row.agent, "credits_used": row.credits_used, "metadata": row.metadata_json}`
  - Emit as `json.dumps([envelope.model_dump() for envelope in envelopes])`
  - Support `since=<event_id>` query param — only return events newer than that ID
  - Use `AsyncSession` for DB access
  - **Complexity:** Medium | **Risk:** MEDIUM — changes WebSocket payload shape; frontend must be updated simultaneously (Task 44)
  - _Requirements: R4.5 — resolves Gap 10_

- [ ] 44. Frontend — Update WebSocket consumer to handle EventEnvelope array
  - Search `src/` for all WebSocket usage (`/ws/live`)
  - Update message handler: expect `JSON.parse(event.data)` to be an array of `EventEnvelope` objects
  - Map `event_type` to human-readable labels (e.g. `"campaign.generation.completed"` → "Campaign generated")
  - Display `payload.credits_used` if non-zero
  - Remove references to old `engagement` and `leads` random fields
  - Activity feed now shows real per-user events
  - **Complexity:** Small | **Risk:** LOW — frontend only; server-side WS is the source of truth
  - _Requirements: R4.5_


## Task Dependency Graph

```json
{
  "waves": [
    {
      "wave": 1,
      "label": "Data Foundation — Migrations",
      "tasks": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    },
    {
      "wave": 2,
      "label": "AWS Bedrock Layer + Agent Contracts",
      "tasks": [13, 14, 15, 16, 17, 18, 19, 20]
    },
    {
      "wave": 3,
      "label": "AgentRunner + Concrete Agents",
      "tasks": [21, 22, 23, 24, 25, 26]
    },
    {
      "wave": 4,
      "label": "Content Generation + BrandProfile",
      "tasks": [27, 28, 29, 30, 31, 32]
    },
    {
      "wave": 5,
      "label": "Validation Layer — All Tests",
      "tasks": [33, 34, 35, 36, 37, 38]
    },
    {
      "wave": 6,
      "label": "Campaign Orchestration Wire-Up",
      "tasks": [39, 40, 41, 42, 43, 44]
    }
  ]
}
```

```
Phase 1 — Data Foundation
─────────────────────────
Task 1 (Alembic bootstrap)
  ├─► Task 2  (0001 campaign CASCADE)
  ├─► Task 3  (0002 ActivityEvent FKs)
  ├─► Task 4  (0003 research_snapshots)    ─► Task 5 (0004 campaign_content)
  ├─► Task 6  (0005 campaign_metrics)
  ├─► Task 7  (0006 publish_results)
  ├─► Task 8  (0007 trend_snapshots)
  ├─► Task 9  (0008 brand_profiles)
  ├─► Task 10 (0009 leads/magnets)
  └─► Task 11 (0010 social_accounts)
Tasks 2–11 ─► Task 12 (all model classes)
Task 12    ─► Tasks 28, 30 (BrandProfile/ResearchSnapshot CRUD)

Phase 2 — AWS Bedrock Layer
────────────────────────────
Task 13 (config keys)
  └─► Task 14 (BaseLLMProvider interface)
        ├─► Task 15 (OpenAIProvider)
        ├─► Task 16 (BedrockProvider)    ← requires AWS IAM confirmed
        └─► Task 17 (GeminiProvider stub)
Tasks 15+16+17 ─► Task 18 (LLMProviderRegistry)
Task 18        ─► Task 27 (llm.py migration)

Phase 3 — Agent Framework
──────────────────────────
Task 19 (BaseAgent extension) + Task 20 (EventEnvelope)
  └─► Task 21 (AgentRunner)  ◄── CRITICAL PATH
        ├─► Task 22 (CampaignManagerAgent)
        ├─► Task 23 (ContentStrategistAgent)
        ├─► Task 24 (CreativeStudioAgent stub)
        └─► Task 25 (5 more agent stubs)
Tasks 22–25 ─► Task 26 (constants sync)

Phase 4 — Content Generation
─────────────────────────────
Task 27 (llm.py → registry) ─► Task 29 (brand voice injection)
Task 9 + Task 12             ─► Task 28 (BrandProfile CRUD)
Task 4 + Task 12             ─► Task 30 (ResearchSnapshot endpoint)
Tasks 4+12+30                ─► Task 31 (orchestrator writes snapshot)
Tasks 27+29+31               ─► Task 32 (Bedrock smoke test) ◄── IAM gate

Phase 5 — Validation Layer
───────────────────────────
Task 21  ─► Task 33 (AgentRunner unit tests) ◄── MUST PASS before Task 39
Task 16  ─► Task 37 (BedrockProvider JSON fallback tests)
Task 20  ─► Task 35 (EventEnvelope schema tests)
Task 18  ─► Task 36 (LLM registry tests)
Task 3   ─► Task 38 (ActivityEvent FK staging verification)
(none)   ─► Task 34 (TOKEN_SCALED formula tests — pure math)

Phase 6 — Campaign Orchestration
──────────────────────────────────
Task 33 (tests passing)     ─► Task 39 (campaign router wire-up)  ← HIGH RISK
Task 21 + Tasks 22–25       ─► Task 40 (execute_agent_task refactor)
Task 21 + Task 24           ─► Task 41 (workflow credit gating)
Task 39                     ─► Task 42 (remove double-charge)  ← deploy atomically with 39
Task 3 + Task 20            ─► Task 43 (WebSocket redesign)
Task 43                     ─► Task 44 (frontend WS consumer update)
```

## Notes

**Parallel workstreams available:**
- Phase 1 (Tasks 1–12) and Phase 2 (Tasks 13–18) have no cross-dependencies and can run in parallel once Task 1 is complete and `BEDROCK_MODEL_ID` config is confirmed
- Phase 3 (Tasks 19–26) can begin as soon as Task 14 is complete — does not require Phase 1
- Tasks 33–38 (Phase 5 validation) can be written in parallel with Phase 4 content tasks

**Hard sequential gates:**
- Task 33 (AgentRunner unit tests) MUST PASS before Task 39 (router wire-up) is merged
- Tasks 39 and 42 MUST BE DEPLOYED ATOMICALLY — deploying 39 without 42 creates a double-charge window
- Tasks 43 and 44 MUST BE DEPLOYED TOGETHER — payload shape change breaks frontend if deployed independently
- Task 32 (Bedrock smoke test) REQUIRES AWS IAM `bedrock:InvokeModel` permission confirmed in advance

**Deferred to Sprint 3.3 (do not attempt in Sprint 3.1):**
- Migration 0011 (Video → Asset backfill and DROP TABLE) — high-risk; Sprint 3.3 entry criterion
- Migration 0012 (parent_asset_id self-ref FK for thumbnails) — depends on 0011
- VideoIntelligenceAgent full implementation (stub in Task 25 is sufficient for Sprint 3.1)
- `render_video` refactor to write Asset rows — Sprint 3.3 scope

**Audit gaps fully resolved by Sprint 3.1 tasks:**
- Gap 3 (BaseAgent no concrete implementations) → Tasks 22–25
- Gap 5 (ActivityEvent FK strings) → Task 3
- Gap 6 (workflow no credit gating) → Task 41
- Gap 9 (RESERVED/REFUNDED never written) → Task 21
- Gap 10 (WebSocket mock data) → Task 43
- Gap 11 (scrape output discarded) → Task 31

**Audit gaps deferred to Sprint 3.3:**
- Gap 1 (render_video bypasses credit/job/activity) → Sprint 3.3
- Gap 2 (Asset model never written) → Sprint 3.3
- Gap 4 (ActivityEvent.asset_id always NULL) → Sprint 3.3 (Asset rows must exist first)
