import { createFileRoute, useParams } from '@tanstack/react-router';
import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { Loader2, Users, Target, PenTool, Lightbulb, Video, Award } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

export const Route = createFileRoute('/campaign/$id')({
  component: CampaignViewer,
});

function CampaignViewer() {
  const { id } = Route.useParams();
  const [activeTab, setActiveTab] = useState('score');
  
  const isLocalhost = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
const API_URL = isLocalhost ? 'http://localhost:8000/api' : (import.meta.env.VITE_API_URL || '/api');

  const { data: campaign, isLoading } = useQuery({
    queryKey: ['campaign', id],
    queryFn: async () => {
      const res = await fetch(`${API_URL}/campaigns/${id}`, {
        credentials: 'include'
      });
      if (!res.ok) throw new Error('Failed to fetch campaign details');
      return res.json();
    },
    // Poll every 3 seconds if status is not completed or failed
    refetchInterval: (data) => {
      if (data && (data.status === 'completed' || data.status === 'failed')) {
        return false;
      }
      return 3000;
    }
  });

  if (isLoading || !campaign) {
    return (
      <div className="min-h-screen bg-background flex flex-col justify-center items-center">
        <Loader2 className="w-10 h-10 animate-spin text-primary mb-4" />
        <h2 className="text-xl font-medium animate-pulse">Loading Campaign...</h2>
      </div>
    );
  }

  if (campaign.status !== 'completed' && campaign.status !== 'failed') {
    return (
      <div className="min-h-screen bg-background flex flex-col justify-center items-center p-8">
        <div className="glass p-12 rounded-2xl max-w-lg w-full text-center border border-primary/20 shadow-[0_0_50px_rgba(var(--primary),0.1)]">
          <Loader2 className="w-12 h-12 animate-spin text-primary mx-auto mb-6" />
          <h2 className="text-2xl font-bold mb-2">AI is working its magic...</h2>
          <p className="text-muted-foreground mb-8">Current Phase: <span className="text-primary font-medium">{campaign.status.replace('_', ' ').toUpperCase()}</span></p>
          
          <div className="w-full bg-white/5 rounded-full h-2 overflow-hidden">
            <div className="bg-primary h-full rounded-full animate-pulse" style={{width: '60%'}}></div>
          </div>
          <p className="text-xs text-white/40 mt-4">This usually takes 1-3 minutes depending on website size.</p>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'score', label: 'Score & Analysis', icon: Award },
    { id: 'personas', label: 'Personas', icon: Users },
    { id: 'competitors', label: 'Competitors', icon: Target },
    { id: 'copy', label: 'Ad Copy', icon: PenTool },
    { id: 'concepts', label: 'Creatives', icon: Lightbulb },
    { id: 'video', label: 'Video Scripts', icon: Video },
  ];

  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="border-b border-white/10 glass sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold truncate">
              {campaign.website_url || 'Campaign Dashboard'}
            </h1>
          </div>
          <div className="flex bg-white/5 rounded-lg p-1">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-1.5 rounded-md text-sm font-medium flex items-center transition ${
                  activeTab === tab.id ? 'bg-primary text-primary-foreground shadow' : 'text-muted-foreground hover:text-white hover:bg-white/5'
                }`}
              >
                <tab.icon className="w-4 h-4 mr-2" />
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            {/* SCORE TAB */}
            {activeTab === 'score' && (
              <div className="space-y-6">
                {campaign.scores?.map((score: any) => (
                  <div key={score.id} className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="glass p-8 rounded-2xl flex flex-col justify-center items-center text-center">
                      <div className="text-6xl font-bold text-primary mb-2">{score.score}/100</div>
                      <div className="text-lg font-medium">Campaign AI Score</div>
                    </div>
                    <div className="col-span-2 glass p-6 rounded-2xl space-y-4">
                      <div>
                        <h3 className="text-green-400 font-bold mb-2">Strengths</h3>
                        <ul className="list-disc pl-5 space-y-1 text-sm text-white/80">
                          {score.strengths?.map((s: str, i: int) => <li key={i}>{s}</li>)}
                        </ul>
                      </div>
                      <div>
                        <h3 className="text-red-400 font-bold mb-2">Weaknesses</h3>
                        <ul className="list-disc pl-5 space-y-1 text-sm text-white/80">
                          {score.weaknesses?.map((w: str, i: int) => <li key={i}>{w}</li>)}
                        </ul>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* PERSONAS TAB */}
            {activeTab === 'personas' && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {campaign.personas?.map((p: any) => (
                  <div key={p.id} className="glass p-6 rounded-xl border border-white/5">
                    <h3 className="text-xl font-bold text-primary mb-1">{p.name}</h3>
                    <p className="text-sm text-white/60 mb-4">{p.job_role} • {p.demographics}</p>
                    
                    <div className="space-y-3 text-sm">
                      <div>
                        <span className="font-semibold text-white/90">Pain Points:</span>
                        <ul className="list-disc pl-4 text-white/70">{p.pain_points?.map((x:any,i:int)=><li key={i}>{x}</li>)}</ul>
                      </div>
                      <div>
                        <span className="font-semibold text-white/90">Goals:</span>
                        <ul className="list-disc pl-4 text-white/70">{p.goals?.map((x:any,i:int)=><li key={i}>{x}</li>)}</ul>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* COPY TAB */}
            {activeTab === 'copy' && (
              <div className="space-y-8">
                {campaign.ad_copies?.map((copy: any) => (
                  <div key={copy.id} className="glass p-6 rounded-xl border border-white/5">
                    <div className="inline-block px-3 py-1 bg-blue-500/20 text-blue-400 text-xs font-bold rounded mb-4">
                      {copy.platform}
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
                      <div>
                        <div className="mb-4"><span className="text-red-400 font-bold block mb-1">Problem:</span> {copy.problem}</div>
                        <div className="mb-4"><span className="text-orange-400 font-bold block mb-1">Agitation:</span> {copy.agitation}</div>
                      </div>
                      <div>
                        <div className="mb-4"><span className="text-green-400 font-bold block mb-1">Solution:</span> {copy.solution}</div>
                        <div className="mb-4"><span className="text-purple-400 font-bold block mb-1">Benefits:</span> {copy.benefits}</div>
                        <div><span className="text-primary font-bold block mb-1">CTA:</span> {copy.cta}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* CONCEPTS TAB */}
            {activeTab === 'concepts' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {campaign.creative_concepts?.map((c: any) => (
                  <div key={c.id} className="glass p-6 rounded-xl border border-white/5">
                    <h3 className="text-lg font-bold text-white mb-2">{c.concept_name}</h3>
                    <p className="text-sm text-primary mb-4">{c.marketing_goal}</p>
                    <p className="text-sm text-white/80 mb-4">{c.visual_direction}</p>
                    <div className="bg-black/30 p-4 rounded-lg">
                      <h4 className="text-xs font-bold uppercase text-white/50 mb-2">Storyboard</h4>
                      <ul className="space-y-2 text-sm text-white/70">
                        {c.storyboard?.map((s: any, i: int) => (
                          <li key={i}><span className="text-white/40 mr-2">{i+1}.</span> {s.scene || s.visual || JSON.stringify(s)}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* VIDEO SCRIPTS TAB */}
            {activeTab === 'video' && (
              <div className="space-y-6">
                {campaign.video_scripts?.map((s: any) => (
                  <div key={s.id} className="glass p-6 rounded-xl border border-white/5">
                    <div className="inline-block px-3 py-1 bg-pink-500/20 text-pink-400 text-xs font-bold rounded mb-4">
                      {s.platform}
                    </div>
                    <div className="space-y-4 text-sm">
                      <div className="bg-white/5 p-4 rounded-lg border-l-2 border-primary">
                        <span className="text-primary font-bold uppercase text-xs mb-1 block">Hook (0:00-0:03)</span>
                        <p className="text-white/90 text-lg font-medium">{s.hook}</p>
                      </div>
                      <div className="px-4">
                        <span className="text-white/50 font-bold uppercase text-xs mb-1 block">Body</span>
                        <p className="text-white/80 whitespace-pre-wrap">{s.body}</p>
                      </div>
                      <div className="bg-white/5 p-4 rounded-lg border-l-2 border-green-500">
                        <span className="text-green-500 font-bold uppercase text-xs mb-1 block">Call To Action</span>
                        <p className="text-white/90 font-bold">{s.cta}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* COMPETITORS TAB */}
            {activeTab === 'competitors' && (
              <div className="space-y-6">
                {campaign.competitor_insights?.map((c: any) => (
                  <div key={c.id} className="glass p-6 rounded-xl border border-white/5 space-y-4 text-sm">
                    <div><span className="font-bold text-white/50 uppercase block mb-1">Competitors</span> {c.competitors?.join(', ')}</div>
                    <div><span className="font-bold text-white/50 uppercase block mb-1">Positioning</span> {c.positioning}</div>
                    <div className="grid grid-cols-2 gap-4 mt-4">
                      <div className="bg-white/5 p-4 rounded-lg"><span className="font-bold text-blue-400 block mb-2">Opportunities</span> <ul className="list-disc pl-4">{c.opportunities?.map((x:any,i:int)=><li key={i}>{x}</li>)}</ul></div>
                      <div className="bg-white/5 p-4 rounded-lg"><span className="font-bold text-red-400 block mb-2">Messaging Gaps</span> <ul className="list-disc pl-4">{c.messaging_gaps?.map((x:any,i:int)=><li key={i}>{x}</li>)}</ul></div>
                    </div>
                  </div>
                ))}
              </div>
            )}

          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}
