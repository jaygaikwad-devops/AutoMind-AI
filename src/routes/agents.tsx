import { createFileRoute, Outlet, Link, useLocation } from '@tanstack/react-router';
import { useQuery } from '@tanstack/react-query';
import {
  LayoutDashboard,
  Video,
  PenTool,
  Share2,
  BarChart3,
  Target,
  Megaphone,
  FolderOpen,
  Settings,
  BrainCircuit,
  CreditCard
} from 'lucide-react';

export const Route = createFileRoute('/agents')({
  component: AgentsLayout,
});

const isLocalhost = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
const API_URL = isLocalhost ? 'http://localhost:8000/api' : (import.meta.env.VITE_API_URL || '/api');

const NAVIGATION = [
  { group: 'Agent Network', items: [
    { name: 'Campaign Manager', href: '/agents/campaign-manager', icon: BrainCircuit },
    { name: 'Creative Studio', href: '/agents/creative-studio', icon: Video },
    { name: 'Content Strategist', href: '/agents/content-strategist', icon: PenTool },
    { name: 'Media Buyer AI', href: '/agents/media-buyer', icon: Megaphone },
    { name: 'Distribution Engine', href: '/agents/distribution-engine', icon: Share2 },
    { name: 'Growth Intelligence', href: '/agents/growth-intelligence', icon: BarChart3 },
    { name: 'Lead Engine', href: '/agents/lead-engine', icon: Target },
  ]},
  { group: 'Workspace', items: [
    { name: 'Credits & Usage', href: '/agents/credits', icon: CreditCard },
    { name: 'Assets', href: '/agents/assets', icon: LayoutDashboard },
    { name: 'Projects', href: '/agents/projects', icon: FolderOpen },
    { name: 'Settings', href: '/agents/settings', icon: Settings },
  ]}
];

function AgentsLayout() {
  const location = useLocation();

  // Auth check & User data
  const { data: user, error: authError } = useQuery({
    queryKey: ['me'],
    queryFn: async () => {
      const res = await fetch(`${API_URL}/auth/me`, { credentials: 'include' });
      if (!res.ok) throw new Error('Not authenticated');
      return res.json();
    },
    retry: false,
  });

  if (authError) {
    window.location.href = '/login';
    return null;
  }

  return (
    <div className="min-h-screen bg-background flex flex-col md:flex-row font-sans">
      
      {/* Sidebar Navigation */}
      <aside className="w-full md:w-64 glass-strong border-r border-white/10 shrink-0 flex flex-col h-screen sticky top-0">
        <div className="p-6 flex items-center gap-2 font-display font-bold text-lg border-b border-white/5">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-gradient-to-br from-[var(--neon-violet)] to-[var(--neon-cyan)] text-background">
            <BrainCircuit className="h-4 w-4" strokeWidth={2.5} />
          </span>
          AutoMind AI
        </div>
        
        <div className="flex-1 overflow-y-auto py-6 px-4 no-scrollbar">
          {NAVIGATION.map((section) => (
            <div key={section.group} className="mb-8">
              <div className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground mb-3 px-3">
                {section.group}
              </div>
              <nav className="space-y-1">
                {section.items.map((item) => {
                  const isActive = item.exact 
                    ? location.pathname === item.href 
                    : location.pathname.startsWith(item.href);
                    
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={`flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition-colors ${
                        isActive 
                          ? 'bg-white/10 text-foreground font-medium' 
                          : 'text-muted-foreground hover:bg-white/5 hover:text-foreground'
                      }`}
                    >
                      <item.icon className={`h-4 w-4 ${isActive ? 'text-[var(--neon-cyan)]' : 'opacity-70'}`} />
                      {item.name}
                    </Link>
                  );
                })}
              </nav>
            </div>
          ))}
        </div>

        {/* User Info & Credits Widget */}
        {user && (
          <div className="p-4 border-t border-white/5">
            <div className="glass rounded-xl p-3 bg-white/[0.02]">
              <div className="text-xs font-medium text-foreground truncate">{user.email}</div>
              <div className="text-[10px] text-muted-foreground uppercase tracking-wider mt-1">{user.plan} Plan</div>
              
              <div className="mt-3 flex items-center justify-between text-xs">
                <span className="flex items-center text-muted-foreground gap-1.5">
                  <CreditCard className="h-3 w-3" /> Credits
                </span>
                <span className="font-mono font-medium text-[var(--neon-lime)]">{user.credits || 0}</span>
              </div>
              <div className="mt-1.5 h-1 rounded-full bg-white/5 overflow-hidden">
                {/* Assuming max credits varies, just a visual indicator */}
                <div 
                  className="h-full bg-[var(--neon-lime)] opacity-80" 
                  style={{ width: `${Math.min(100, ((user.credits || 0) / 500) * 100)}%` }} 
                />
              </div>
            </div>
          </div>
        )}
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col h-screen overflow-y-auto bg-[#0a0a0a]">
        <div className="p-6 md:p-10 max-w-7xl mx-auto w-full">
          <Outlet />
        </div>
      </main>

    </div>
  );
}
