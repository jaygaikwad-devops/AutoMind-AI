import { createFileRoute } from '@tanstack/react-router';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { Video, Plus, Loader2, Play } from 'lucide-react';

export const Route = createFileRoute('/studio')({
  component: StudioDashboard,
});

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

type VideoType = {
  id: string;
  prompt: string;
  status: string;
  url: string | null;
  created_at: string;
};

function StudioDashboard() {
  const queryClient = useQueryClient();
  const [prompt, setPrompt] = useState('');

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

  // Redirect if not authenticated
  if (authError) {
    window.location.href = '/login';
  }

  // Fetch videos
  const { data: videos = [], isLoading } = useQuery<VideoType[]>({
    queryKey: ['videos'],
    queryFn: async () => {
      const res = await fetch(`${API_URL}/videos`, { credentials: 'include' });
      if (!res.ok) throw new Error('Failed to fetch videos');
      return res.json();
    },
    refetchInterval: 2000,
    enabled: !!user,
  });

  // Create video mutation
  const createMutation = useMutation({
    mutationFn: async (newPrompt: string) => {
      const res = await fetch(`${API_URL}/videos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ prompt: newPrompt, duration_s: 15 }),
      });
      if (!res.ok) throw new Error('Failed to create video');
      return res.json();
    },
    onSuccess: () => {
      setPrompt('');
      queryClient.invalidateQueries({ queryKey: ['videos'] });
    },
  });

  return (
    <div className="min-h-screen bg-background text-foreground p-8">
      <div className="max-w-5xl mx-auto space-y-8">
        
        {/* Header */}
        <header className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-display font-bold">AutoMind Studio</h1>
            <p className="text-muted-foreground mt-1">Manage your autonomous AI generations.</p>
          </div>
          {user && (
            <div className="flex items-center gap-4">
              <span className="text-sm text-muted-foreground">{user.email}</span>
              <button
                onClick={async () => {
                  await fetch(`${API_URL}/auth/logout`, { method: 'POST', credentials: 'include' });
                  window.location.href = '/login';
                }}
                className="text-sm px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 transition"
              >
                Log Out
              </button>
            </div>
          )}
        </header>

        {/* Generate New */}
        <div className="glass-strong rounded-2xl p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Video className="w-5 h-5 text-[var(--neon-violet)]" />
            Generate New Video
          </h2>
          <form 
            className="flex gap-3"
            onSubmit={(e) => {
              e.preventDefault();
              if (prompt.trim()) createMutation.mutate(prompt);
            }}
          >
            <input
              type="text"
              placeholder="e.g. A cinematic shot of a futuristic city..."
              className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-2 text-sm focus:outline-none focus:border-[var(--neon-cyan)] transition"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              disabled={createMutation.isPending}
            />
            <button
              type="submit"
              disabled={createMutation.isPending || !prompt.trim()}
              className="bg-gradient-to-r from-[var(--neon-violet)] to-[var(--neon-cyan)] text-background font-semibold px-6 py-2 rounded-xl flex items-center gap-2 hover:opacity-90 disabled:opacity-50 transition"
            >
              {createMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
              Generate
            </button>
          </form>
        </div>

        {/* Video List */}
        <div>
          <h2 className="text-lg font-semibold mb-4">Your Videos</h2>
          {isLoading ? (
            <div className="flex justify-center p-10"><Loader2 className="w-6 h-6 animate-spin text-muted-foreground" /></div>
          ) : videos.length === 0 ? (
            <div className="glass rounded-2xl p-10 text-center text-muted-foreground">
              No videos generated yet. Create one above!
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {videos.map(video => (
                <div key={video.id} className="glass rounded-2xl p-4 flex flex-col">
                  
                  {/* Status badge */}
                  <div className="flex justify-between items-start mb-3">
                    <span className="text-xs text-muted-foreground font-mono truncate mr-2" title={video.id}>
                      {video.id.split('-')[0]}
                    </span>
                    <span className={`text-[10px] uppercase tracking-wider font-bold px-2 py-1 rounded-full ${
                      video.status === 'ready' ? 'bg-green-500/20 text-green-400' :
                      video.status === 'rendering' ? 'bg-yellow-500/20 text-yellow-400 animate-pulse' :
                      'bg-white/10 text-muted-foreground'
                    }`}>
                      {video.status}
                    </span>
                  </div>

                  <p className="text-sm font-medium mb-4 flex-1 line-clamp-3">"{video.prompt}"</p>

                  {/* Action area */}
                  <div className="mt-auto">
                    {video.status === 'ready' && video.url ? (
                      <a href={video.url} target="_blank" rel="noreferrer" className="w-full inline-flex items-center justify-center gap-2 bg-white/10 hover:bg-white/20 transition rounded-lg py-2 text-xs font-semibold">
                        <Play className="w-3 h-3" /> View Result
                      </a>
                    ) : (
                      <div className="w-full h-8 bg-white/5 rounded-lg overflow-hidden relative">
                        {video.status === 'rendering' && (
                          <div className="absolute inset-0 bg-gradient-to-r from-[var(--neon-violet)] to-[var(--neon-cyan)] opacity-30 animate-pulse" />
                        )}
                        <div className="absolute inset-0 flex items-center justify-center text-[10px] text-muted-foreground">
                          {video.status === 'rendering' ? 'Processing...' : 'In Queue'}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
