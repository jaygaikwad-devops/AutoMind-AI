import { createFileRoute, Link } from '@tanstack/react-router';
import { useQuery } from '@tanstack/react-query';
import { Play, Settings, Share2, Heart, MessageCircle, Bookmark, CheckCircle2 } from 'lucide-react';
import { useState } from 'react';

export const Route = createFileRoute('/workflows')({
  component: WorkflowsDashboard,
});

const isLocalhost = typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
const API_URL = isLocalhost ? 'http://localhost:8000/api' : (import.meta.env.VITE_API_URL || '/api');

function WorkflowsDashboard() {
  const [selectedPostId, setSelectedPostId] = useState<string | null>(null);

  // Auth check
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
  }

  // Fetch Posts
  const { data: posts = [], isLoading } = useQuery({
    queryKey: ['posts'],
    queryFn: async () => {
      const res = await fetch(`${API_URL}/social`, { credentials: 'include' });
      if (!res.ok) throw new Error('Failed to fetch posts');
      return res.json();
    },
    enabled: !!user,
  });

  const selectedPost = posts.find((p: any) => p.id === selectedPostId) || posts[0];

  return (
    <div className="h-screen w-full flex flex-col bg-background text-foreground overflow-hidden">
      
      {/* Header */}
      <header className="h-16 border-b border-white/10 glass px-6 flex items-center justify-between shrink-0 z-10">
        <div className="flex items-center gap-6">
          <div className="text-xl font-display font-bold text-[var(--neon-violet)] flex items-center gap-2">
            <Play className="w-5 h-5 fill-current" />
            AutoMind
          </div>
          <nav className="flex items-center gap-4 text-sm font-medium">
            <Link to="/studio" className="text-muted-foreground hover:text-white transition">Studio</Link>
            <Link to="/workflows" className="text-white border-b-2 border-[var(--neon-violet)] pb-1">Workflows</Link>
          </nav>
        </div>
        
        <div className="flex items-center gap-3">
          {user && (
            <div className="text-xs text-muted-foreground bg-white/5 px-3 py-1.5 rounded-full border border-white/10">
              {user.email}
            </div>
          )}
        </div>
      </header>

      <main className="flex-1 flex overflow-hidden">
        {/* Left Sidebar: List of Workflows/Posts */}
        <div className="w-80 border-r border-white/10 bg-black/20 flex flex-col">
          <div className="p-4 border-b border-white/10 font-semibold text-sm">
            Recent Generations
          </div>
          <div className="flex-1 overflow-y-auto p-2 space-y-2">
            {isLoading && <div className="p-4 text-center text-xs text-muted-foreground">Loading...</div>}
            {!isLoading && posts.length === 0 && (
              <div className="p-4 text-center text-xs text-muted-foreground">No posts yet. Generate one in the Studio!</div>
            )}
            {posts.map((post: any) => (
              <button
                key={post.id}
                onClick={() => setSelectedPostId(post.id)}
                className={`w-full text-left p-3 rounded-xl border transition ${selectedPostId === post.id || (!selectedPostId && selectedPost?.id === post.id) ? 'border-[var(--neon-violet)] bg-[var(--neon-violet)]/10' : 'border-white/5 bg-white/5 hover:border-white/20'}`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold capitalize text-white/90">{post.platform}</span>
                  {post.status === 'published' ? (
                    <span className="text-[10px] text-green-400 bg-green-400/10 px-2 py-0.5 rounded-full flex items-center gap-1"><CheckCircle2 className="w-3 h-3"/> Published</span>
                  ) : (
                    <span className="text-[10px] text-yellow-400 bg-yellow-400/10 px-2 py-0.5 rounded-full">Scheduled</span>
                  )}
                </div>
                <div className="text-xs text-muted-foreground line-clamp-2">
                  {post.content.split('\n')[0] || 'No caption'}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Right Content: Preview Pane */}
        <div className="flex-1 bg-[#0a0a0a] flex items-center justify-center p-8 relative">
          <div className="absolute inset-0 opacity-20 pointer-events-none" style={{ backgroundImage: 'radial-gradient(circle at 50% 50%, var(--neon-violet) 0%, transparent 50%)' }} />
          
          {selectedPost ? (
            <div className="relative w-[360px] h-[720px] bg-black border-[6px] border-neutral-800 rounded-[3rem] shadow-2xl overflow-hidden flex flex-col z-10 ring-1 ring-white/10">
              {/* Fake Mobile Status Bar */}
              <div className="absolute top-0 w-full h-7 z-20 flex justify-between items-center px-6 pt-1 text-[10px] text-white/80">
                <span>9:41</span>
                <div className="flex items-center gap-1">
                  <div className="w-4 h-2.5 border border-white/50 rounded-sm" />
                </div>
              </div>

              {/* Video Player Area */}
              <div className="flex-1 relative bg-neutral-900">
                {selectedPost.content.includes('http') ? (
                  <video 
                    src={selectedPost.content.match(/https?:\/\/[^\s]+/)?.[0] || ''} 
                    className="w-full h-full object-cover"
                    autoPlay loop muted playsInline
                  />
                ) : (
                  <div className="w-full h-full flex flex-col items-center justify-center text-muted-foreground">
                    <Play className="w-12 h-12 mb-2 opacity-50" />
                    <span className="text-sm">Video Processing...</span>
                  </div>
                )}

                {/* Right Action Bar */}
                <div className="absolute bottom-32 right-4 flex flex-col items-center gap-4">
                  <button className="p-2.5 rounded-full bg-black/40 backdrop-blur-md text-white border border-white/10"><Heart className="w-6 h-6" /></button>
                  <button className="p-2.5 rounded-full bg-black/40 backdrop-blur-md text-white border border-white/10"><MessageCircle className="w-6 h-6" /></button>
                  <button className="p-2.5 rounded-full bg-black/40 backdrop-blur-md text-white border border-white/10"><Share2 className="w-6 h-6" /></button>
                </div>

                {/* Bottom Info Area */}
                <div className="absolute bottom-0 w-full p-4 bg-gradient-to-t from-black/80 via-black/40 to-transparent">
                  <div className="flex items-center gap-2 mb-2">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-[var(--neon-violet)] to-[var(--neon-cyan)] p-0.5">
                      <div className="w-full h-full bg-black rounded-full" />
                    </div>
                    <span className="text-sm font-semibold text-white">@automind_ai</span>
                    <button className="px-2 py-0.5 text-xs border border-white/30 rounded-md font-medium text-white backdrop-blur">Follow</button>
                  </div>
                  
                  <div className="text-sm text-white/90 whitespace-pre-wrap max-h-32 overflow-y-auto">
                    {selectedPost.content.replace(/Link: https?:\/\/[^\s]+/, '').trim()}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="text-muted-foreground z-10 flex flex-col items-center">
              <Share2 className="w-12 h-12 mb-4 opacity-50" />
              <span>Select a workflow to preview</span>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
