import { createFileRoute, Link } from '@tanstack/react-router';
import { 
  Video, PenTool, Share2, BarChart3, Megaphone, Target, ArrowRight 
} from 'lucide-react';

export const Route = createFileRoute('/agents/')({
  component: AgentOverview,
});

const AGENTS = [
  { name: 'Creative Studio', desc: 'AI reels, shorts, and ad creatives in 4K', icon: Video, color: 'var(--neon-violet)', href: '/agents/creative-studio', locked: false },
  { name: 'Content Strategist', desc: 'Captions, hooks, and SEO blogs', icon: PenTool, color: 'var(--neon-cyan)', href: '/agents/content-strategist', locked: false },
  { name: 'Distribution Engine', desc: 'Omnichannel scheduling and posting', icon: Share2, color: 'var(--neon-pink)', href: '/agents/distribution-engine', locked: true },
  { name: 'Growth Intelligence', desc: 'Realtime telemetry and viral scoring', icon: BarChart3, color: 'var(--neon-lime)', href: '/agents/growth-intelligence', locked: true },
  { name: 'Media Buyer AI', desc: 'Self-tuning ad campaigns on Meta & TikTok', icon: Megaphone, color: 'var(--neon-violet)', href: '/agents/media-buyer', locked: true },
  { name: 'Lead Engine', desc: 'Autonomous funnels and client capture', icon: Target, color: 'var(--neon-cyan)', href: '/agents/lead-engine', locked: true },
];

function AgentOverview() {
  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div>
        <h1 className="text-3xl font-display font-bold text-foreground">Agent Network Overview</h1>
        <p className="text-muted-foreground mt-2 max-w-2xl">
          Your autonomous marketing team is standing by. Distribute tasks to specialized AI agents or use the Campaign Manager to orchestrate them all.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {AGENTS.map((agent) => (
          <Link
            key={agent.name}
            to={agent.locked ? '#' : agent.href}
            className={`group relative glass rounded-2xl p-6 overflow-hidden transition-all duration-300 ${
              agent.locked ? 'opacity-70 cursor-not-allowed hover:bg-transparent' : 'hover:bg-white/[0.04] hover:-translate-y-1'
            }`}
          >
            {/* Background Glow */}
            {!agent.locked && (
              <div 
                className="absolute -top-12 -right-12 w-32 h-32 rounded-full blur-[60px] opacity-0 group-hover:opacity-40 transition-opacity duration-500"
                style={{ backgroundColor: agent.color }}
              />
            )}
            
            <div className="flex justify-between items-start mb-4 relative z-10">
              <span className="grid h-12 w-12 place-items-center rounded-xl glass-strong" style={{ boxShadow: `0 4px 20px -5px ${agent.color}40` }}>
                <agent.icon className="h-6 w-6" style={{ color: agent.color }} />
              </span>
              
              {agent.locked ? (
                <span className="bg-white/5 border border-white/10 px-2.5 py-1 rounded-full text-[10px] uppercase font-semibold text-muted-foreground tracking-wider">
                  Growth Plan
                </span>
              ) : (
                <span className="bg-[var(--neon-lime)]/10 text-[var(--neon-lime)] px-2.5 py-1 rounded-full text-[10px] uppercase font-bold tracking-wider flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-[var(--neon-lime)] animate-pulse" /> Active
                </span>
              )}
            </div>

            <h3 className="font-display font-bold text-lg text-foreground relative z-10">{agent.name}</h3>
            <p className="text-sm text-muted-foreground mt-1 relative z-10">{agent.desc}</p>

            {!agent.locked && (
              <div className="mt-6 flex items-center text-xs font-medium text-foreground group-hover:text-[var(--neon-cyan)] transition-colors">
                Launch Agent <ArrowRight className="ml-1.5 h-3.5 w-3.5 group-hover:translate-x-1 transition-transform" />
              </div>
            )}
          </Link>
        ))}
      </div>

      <div className="glass-strong rounded-3xl p-8 relative overflow-hidden mt-12 border border-[var(--neon-violet)]/30">
        <div className="absolute inset-0 bg-gradient-to-br from-[var(--neon-violet)]/10 to-[var(--neon-cyan)]/10 opacity-50" />
        <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full bg-white/5 px-3 py-1 text-[11px] uppercase tracking-widest text-muted-foreground mb-3">
              <span className="text-[var(--neon-pink)] font-bold">New</span> Orchestrator
            </div>
            <h2 className="text-2xl font-display font-bold text-foreground">Campaign Manager Agent</h2>
            <p className="text-muted-foreground mt-2 max-w-xl text-sm">
              Deploy all 6 agents simultaneously. The Campaign Manager automatically routes data between the Creative Studio, Content Strategist, and Distribution Engine.
            </p>
          </div>
          <Link 
            to="/agents/campaign-manager"
            className="shrink-0 bg-gradient-to-r from-[var(--neon-violet)] to-[var(--neon-cyan)] text-background font-bold px-6 py-3 rounded-full hover:opacity-90 transition shadow-lg shadow-[var(--neon-violet)]/20"
          >
            Launch Campaign
          </Link>
        </div>
      </div>
    </div>
  );
}
