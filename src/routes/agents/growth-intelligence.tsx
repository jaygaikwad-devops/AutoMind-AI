import { createFileRoute } from '@tanstack/react-router';
import { BarChart3, TrendingUp, AlertTriangle, Lightbulb, Activity, ArrowRight } from 'lucide-react';

export const Route = createFileRoute('/agents/growth-intelligence')({
  component: GrowthIntelligence,
});

function GrowthIntelligence() {
  return (
    <div className="space-y-8 animate-in fade-in duration-500 max-w-5xl mx-auto">
      <div>
        <div className="flex items-center gap-3 mb-2">
          <div className="grid h-10 w-10 place-items-center rounded-xl glass-strong" style={{ boxShadow: `0 4px 20px -5px var(--neon-lime)` }}>
            <BarChart3 className="h-5 w-5 text-[var(--neon-lime)]" />
          </div>
          <h1 className="text-3xl font-display font-bold text-foreground">Growth Intelligence</h1>
        </div>
        <p className="text-muted-foreground mt-2">
          Stop looking at charts. AutoMind constantly analyzes your data to give you actionable, predictive insights that drive revenue.
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {/* Core Metric */}
        <div className="glass-strong rounded-2xl p-6 relative overflow-hidden border border-[var(--neon-lime)]/20">
          <div className="absolute top-0 right-0 w-32 h-32 bg-[var(--neon-lime)]/10 rounded-full blur-[50px] -z-10 pointer-events-none" />
          <h3 className="text-sm font-medium text-muted-foreground mb-4 flex items-center gap-2">
            <Activity className="w-4 h-4 text-[var(--neon-lime)]" /> Viral Predictor Score
          </h3>
          <div className="text-5xl font-display font-bold text-white mb-2">84.2</div>
          <div className="text-sm text-[var(--neon-lime)] font-medium flex items-center gap-1">
            <TrendingUp className="w-4 h-4" /> Top 15% in your niche
          </div>
        </div>

        {/* AI Insight 1 */}
        <div className="md:col-span-2 glass rounded-2xl p-6 border border-white/5 flex flex-col justify-center">
          <div className="flex items-start gap-4">
            <div className="grid h-12 w-12 shrink-0 place-items-center rounded-xl bg-[var(--neon-cyan)]/20 text-[var(--neon-cyan)]">
              <Lightbulb className="h-6 w-6" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white mb-1">Timing Optimization Detected</h3>
              <p className="text-sm text-muted-foreground mb-3 leading-relaxed">
                Your LinkedIn posts perform <strong className="text-white">37% better</strong> on Tuesdays between 9:00 AM and 11:30 AM EST. Your current schedule is heavily biased towards Thursdays.
              </p>
              <button className="bg-white/5 hover:bg-white/10 px-4 py-2 rounded-lg text-xs font-semibold transition flex items-center gap-2">
                Apply to Distribution Engine <ArrowRight className="w-3 h-3" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* AI Insight 2 */}
        <div className="glass rounded-2xl p-6 border border-[var(--neon-violet)]/20">
          <div className="flex items-start gap-4">
            <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-[var(--neon-violet)]/20 text-[var(--neon-violet)]">
              <TrendingUp className="h-5 w-5" />
            </div>
            <div>
              <h3 className="font-bold text-white mb-2">Creative Format Winner</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Your best-performing hook style over the last 14 days is the <strong className="text-white">"Problem → Solution"</strong> pattern on 9:16 Reels.
              </p>
              <div className="bg-white/5 rounded-lg p-3 border border-white/5">
                <div className="text-xs font-mono uppercase text-muted-foreground mb-1">AI Recommendation</div>
                <div className="text-sm">Create 5 more Video Ads using this exact hook structure to lower CPA.</div>
              </div>
            </div>
          </div>
        </div>

        {/* AI Insight 3 */}
        <div className="glass rounded-2xl p-6 border border-[var(--neon-pink)]/20">
          <div className="flex items-start gap-4">
            <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-[var(--neon-pink)]/20 text-[var(--neon-pink)]">
              <AlertTriangle className="h-5 w-5" />
            </div>
            <div>
              <h3 className="font-bold text-white mb-2">Ad Fatigue Warning</h3>
              <p className="text-sm text-muted-foreground mb-4">
                "Campaign Alpha" has seen a <strong className="text-[var(--neon-pink)]">22% drop</strong> in CTR over the last 48 hours. Frequency is above 3.5.
              </p>
              <div className="bg-white/5 rounded-lg p-3 border border-white/5">
                <div className="text-xs font-mono uppercase text-muted-foreground mb-1">AI Recommendation</div>
                <div className="text-sm">Rotate 3 new AI-generated CTAs into the ad set immediately.</div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}
