import logging
from sqlalchemy.orm import Session
import json

from app.models.campaign import (
    Campaign, Persona, CompetitorInsight, Angle, Hook, Headline,
    CTA, AdCopy, CreativeConcept, VideoScript, CampaignScore
)
from app.services.campaigns.analyzer import analyze_website
from app.services.campaigns.llm import (
    generate_personas, generate_competitor_insights, generate_angles,
    generate_hooks, generate_headlines, generate_ctas, generate_ad_copy,
    generate_creative_concepts, generate_video_scripts, generate_campaign_score
)

logger = logging.getLogger(__name__)

def generate_full_campaign_sync(db: Session, campaign_id: str):
    """Executes the 12-step AI Campaign Strategist pipeline synchronously (for Celery)."""
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        logger.error(f"Campaign {campaign_id} not found.")
        return

    try:
        # Step 1: Analyze Website
        logger.info(f"[{campaign_id}] Step 1: Analyzing Website")
        campaign.status = "analyzing_website"
        db.commit()
        
        scraped_data = {}
        if campaign.website_url:
            scraped_data = analyze_website(campaign.website_url)
        
        # Build master context for LLM
        context = f"""
        Website URL: {campaign.website_url}
        Product Info: {campaign.product_description}
        Target Audience: {campaign.target_audience}
        Campaign Goal: {campaign.campaign_goal}
        Scraped Title: {scraped_data.get('title')}
        Scraped Snippet: {scraped_data.get('main_text_snippet')}
        """

        # Step 2: Generate Personas
        logger.info(f"[{campaign_id}] Step 2: Generating Personas")
        campaign.status = "generating_personas"
        db.commit()
        
        personas_data = generate_personas(context)
        for p in personas_data:
            db.add(Persona(
                campaign_id=campaign.id,
                name=p.get('name', 'Unknown'),
                demographics=p.get('demographics', ''),
                job_role=p.get('job_role', ''),
                pain_points=p.get('pain_points', []),
                goals=p.get('goals', []),
                motivations=p.get('motivations', []),
                buying_triggers=p.get('buying_triggers', []),
                objections=p.get('objections', [])
            ))
        db.commit()

        # Step 3: Competitor Analysis
        logger.info(f"[{campaign_id}] Step 3: Generating Competitor Insights")
        campaign.status = "generating_competitors"
        db.commit()
        
        comp_data = generate_competitor_insights(context)
        if comp_data:
            db.add(CompetitorInsight(
                campaign_id=campaign.id,
                competitors=comp_data.get('competitors', []),
                opportunities=comp_data.get('opportunities', []),
                positioning=comp_data.get('positioning', ''),
                messaging_gaps=comp_data.get('messaging_gaps', []),
                feature_gaps=comp_data.get('feature_gaps', [])
            ))
        db.commit()

        # Step 4: Ad Angles
        logger.info(f"[{campaign_id}] Step 4: Generating Angles")
        campaign.status = "generating_angles"
        db.commit()
        
        angles_data = generate_angles(context)
        for a in angles_data:
            db.add(Angle(campaign_id=campaign.id, name=a.get('name',''), description=a.get('description','')))
        db.commit()

        # Step 5: Hooks
        logger.info(f"[{campaign_id}] Step 5: Generating Hooks")
        campaign.status = "generating_hooks"
        db.commit()
        
        hooks_data = generate_hooks(context)
        for h in hooks_data:
            db.add(Hook(campaign_id=campaign.id, type=h.get('type',''), content=h.get('content',''), score=h.get('score', 50)))
        db.commit()

        # Step 6: Headlines
        logger.info(f"[{campaign_id}] Step 6: Generating Headlines")
        campaign.status = "generating_headlines"
        db.commit()
        
        headlines_data = generate_headlines(context)
        for h in headlines_data:
            db.add(Headline(campaign_id=campaign.id, platform=h.get('platform',''), content=h.get('content','')))
        db.commit()

        # Step 7: CTAs
        logger.info(f"[{campaign_id}] Step 7: Generating CTAs")
        campaign.status = "generating_ctas"
        db.commit()
        
        ctas_data = generate_ctas(context)
        for c in ctas_data:
            db.add(CTA(campaign_id=campaign.id, type=c.get('type',''), content=c.get('content','')))
        db.commit()

        # Step 8: Ad Copy
        logger.info(f"[{campaign_id}] Step 8: Generating Ad Copy")
        campaign.status = "generating_ad_copy"
        db.commit()
        
        copy_data = generate_ad_copy(context, angles_data)
        for c in copy_data:
            db.add(AdCopy(
                campaign_id=campaign.id,
                platform=c.get('platform',''),
                problem=c.get('problem',''),
                agitation=c.get('agitation',''),
                solution=c.get('solution',''),
                benefits=c.get('benefits',''),
                cta=c.get('cta','')
            ))
        db.commit()

        # Step 9: Creative Concepts
        logger.info(f"[{campaign_id}] Step 9: Generating Creative Concepts")
        campaign.status = "generating_creative_concepts"
        db.commit()
        
        concepts_data = generate_creative_concepts(context)
        for c in concepts_data:
            db.add(CreativeConcept(
                campaign_id=campaign.id,
                concept_name=c.get('concept_name',''),
                visual_direction=c.get('visual_direction',''),
                marketing_goal=c.get('marketing_goal',''),
                storyboard=c.get('storyboard',[])
            ))
        db.commit()

        # Step 10: Video Scripts
        logger.info(f"[{campaign_id}] Step 10: Generating Video Scripts")
        campaign.status = "generating_video_scripts"
        db.commit()
        
        scripts_data = generate_video_scripts(context)
        for s in scripts_data:
            db.add(VideoScript(
                campaign_id=campaign.id,
                platform=s.get('platform',''),
                hook=s.get('hook',''),
                body=s.get('body',''),
                cta=s.get('cta',''),
                timestamps=s.get('timestamps',[])
            ))
        db.commit()

        # Step 11: Campaign Score
        logger.info(f"[{campaign_id}] Step 11: Generating Campaign Score")
        campaign.status = "generating_campaign_score"
        db.commit()
        
        score_data = generate_campaign_score(context, copy_data, scripts_data)
        if score_data:
            db.add(CampaignScore(
                campaign_id=campaign.id,
                score=score_data.get('score', 0),
                strengths=score_data.get('strengths', []),
                weaknesses=score_data.get('weaknesses', []),
                recommendations=score_data.get('recommendations', [])
            ))
        db.commit()

        # Finalize
        logger.info(f"[{campaign_id}] Campaign Generation Complete!")
        campaign.status = "completed"
        db.commit()

    except Exception as e:
        logger.error(f"[{campaign_id}] Pipeline failed: {e}")
        campaign.status = "failed"
        db.commit()
