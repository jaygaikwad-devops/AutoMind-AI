import { createFileRoute, Link } from '@tanstack/react-router';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState, useCallback, useMemo, useEffect } from 'react';
import { Loader2, Play, Save, Workflow as WorkflowIcon, ChevronDown } from 'lucide-react';
import {
  ReactFlow,
  Background,
  Controls,
  applyNodeChanges,
  applyEdgeChanges,
  addEdge,
  Node,
  Edge,
  NodeChange,
  EdgeChange,
  Connection,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { PromptNode, VideoNode, SocialNode, CaptionNode, HashtagNode } from '../components/studio/CustomNodes';

export const Route = createFileRoute('/studio')({
  component: StudioDashboard,
});

const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const API_URL = isLocalhost ? 'http://localhost:8000/api' : (import.meta.env.VITE_API_URL || '/api');

const initialNodes: Node[] = [
  { id: '1', type: 'prompt', position: { x: 100, y: 100 }, data: { prompt: '' } },
  { id: '2', type: 'video', position: { x: 500, y: 100 }, data: {} },
];

const initialEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2', animated: true, style: { stroke: 'var(--neon-violet)' } },
];

function StudioDashboard() {
  const queryClient = useQueryClient();
  const [nodes, setNodes] = useState<Node[]>(initialNodes);
  const [edges, setEdges] = useState<Edge[]>(initialEdges);
  const [workflowName, setWorkflowName] = useState('Untitled Workflow');
  const [showDropdown, setShowDropdown] = useState(false);

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

  // Fetch workflows
  const { data: workflows = [] } = useQuery({
    queryKey: ['workflows'],
    queryFn: async () => {
      const res = await fetch(`${API_URL}/workflows`, { credentials: 'include' });
      if (!res.ok) throw new Error('Failed to fetch workflows');
      return res.json();
    },
    enabled: !!user,
  });

  const loadWorkflow = (wf: any) => {
    setWorkflowName(wf.name);
    setNodes(wf.nodes || []);
    setEdges(wf.edges || []);
    setShowDropdown(false);
  };

  const nodeTypes = useMemo(() => ({
    prompt: PromptNode,
    video: VideoNode,
    social: SocialNode,
    caption: CaptionNode,
    hashtag: HashtagNode,
  }), []);

  const onNodesChange = useCallback(
    (changes: NodeChange[]) => setNodes((nds) => applyNodeChanges(changes, nds)),
    []
  );
  const onEdgesChange = useCallback(
    (changes: EdgeChange[]) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    []
  );
  const onConnect = useCallback(
    (connection: Connection) => setEdges((eds) => addEdge({ ...connection, animated: true, style: { stroke: 'var(--neon-violet)' } }, eds)),
    []
  );

  const addNode = (type: string) => {
    const newNode: Node = {
      id: `${Date.now()}`,
      type,
      position: { x: 200, y: 300 },
      data: type === 'prompt' ? { prompt: '' } : type === 'social' ? { platform: 'instagram' } : type === 'caption' ? { tone: 'engaging' } : type === 'hashtag' ? { niche: '' } : type === 'video' ? { voice: 'rachel', language: 'en' } : {},
    };
    setNodes((nds) => [...nds, newNode]);
  };

  const saveMutation = useMutation({
    mutationFn: async () => {
      const res = await fetch(`${API_URL}/workflows`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          name: workflowName,
          nodes: nodes,
          edges: edges,
        }),
      });
      if (!res.ok) throw new Error('Failed to save workflow');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflows'] });
      alert('Workflow saved!');
    }
  });

  const runMutation = useMutation({
    mutationFn: async () => {
      // 1. Auto-save workflow before running
      const saveRes = await fetch(`${API_URL}/workflows`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          name: workflowName,
          nodes: nodes,
          edges: edges,
        }),
      });
      if (!saveRes.ok) throw new Error('Failed to auto-save workflow');
      const savedWf = await saveRes.json();

      // 2. Run workflow
      const res = await fetch(`${API_URL}/workflows/${savedWf.id}/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
      });
      if (!res.ok) throw new Error('Failed to run workflow');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflows'] });
      alert('Workflow saved and started! Check the Workflows tab to see the preview.');
    },
    onError: (err: any) => {
      alert(err.message);
    }
  });

  return (
    <div className="h-screen w-full flex flex-col bg-background text-foreground overflow-hidden">
      
      {/* Header */}
      <header className="h-16 border-b border-white/10 glass px-6 flex items-center justify-between shrink-0 z-10">
        <div className="flex items-center gap-6">
          <div className="text-xl font-display font-bold text-[var(--neon-violet)] flex items-center gap-2">
            <Play className="w-5 h-5 fill-current" />
            AutoMind
          </div>
          <nav className="flex items-center gap-4 text-sm font-medium mr-4">
            <Link to="/studio" className="text-white border-b-2 border-[var(--neon-violet)] pb-1">Studio</Link>
            <Link to="/workflows" className="text-muted-foreground hover:text-white transition">Workflows</Link>
            <Link to="/campaign-builder" className="text-muted-foreground hover:text-[var(--neon-cyan)] transition flex items-center">
              <span className="w-1.5 h-1.5 rounded-full bg-[var(--neon-cyan)] mr-2 animate-pulse" />
              AI Campaign
            </Link>
          </nav>
          
          <div className="flex items-center group relative cursor-pointer" onClick={() => setShowDropdown(!showDropdown)}>
            <input 
              value={workflowName}
              onChange={(e) => setWorkflowName(e.target.value)}
              onClick={(e) => e.stopPropagation()}
              className="bg-transparent border-none text-lg font-display font-bold focus:outline-none focus:ring-1 focus:ring-white/20 rounded px-2 -ml-2"
            />
            <ChevronDown className="w-4 h-4 text-muted-foreground ml-2 opacity-50 group-hover:opacity-100" />
          </div>
          
          {showDropdown && (
            <div className="absolute top-10 left-8 bg-[#121212] border border-white/10 rounded-xl shadow-2xl p-2 w-64 z-50">
              <div className="text-xs font-semibold text-muted-foreground px-2 py-1 mb-1">Your Workflows</div>
              {workflows.map((wf: any) => (
                <button
                  key={wf.id}
                  onClick={() => loadWorkflow(wf)}
                  className="w-full text-left px-3 py-2 rounded-lg hover:bg-white/5 text-sm transition"
                >
                  {wf.name}
                </button>
              ))}
              {workflows.length === 0 && (
                <div className="px-3 py-2 text-xs text-muted-foreground">No saved workflows</div>
              )}
            </div>
          )}
        </div>
        
        <div className="flex items-center gap-3">
          <button 
            onClick={() => addNode('prompt')}
            className="text-sm px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 transition border border-white/10 text-white/80"
          >
            + Text Input
          </button>
          <button 
            onClick={() => addNode('caption')}
            className="text-sm px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 transition border border-white/10 text-white/80"
          >
            + Smart Captions
          </button>
          <button 
            onClick={() => addNode('hashtag')}
            className="text-sm px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 transition border border-white/10 text-white/80"
          >
            + Hashtags
          </button>
          <button 
            onClick={() => addNode('video')}
            className="text-sm px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 transition border border-white/10 text-white/80"
          >
            + AI Video
          </button>
          <button 
            onClick={() => addNode('social')}
            className="text-sm px-3 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 transition border border-white/10 text-white/80"
          >
            + Social Publish
          </button>

          <div className="w-px h-6 bg-white/20 mx-2" />

          <button 
            onClick={() => saveMutation.mutate()}
            disabled={saveMutation.isPending}
            className="text-sm px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 transition flex items-center gap-2"
          >
            {saveMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            Save
          </button>
          <button 
            onClick={() => runMutation.mutate()}
            disabled={runMutation.isPending}
            className="text-sm px-4 py-2 rounded-xl bg-gradient-to-r from-[var(--neon-violet)] to-[var(--neon-cyan)] text-background font-semibold flex items-center gap-2 hover:opacity-90 transition disabled:opacity-50"
          >
            {runMutation.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />} Run
          </button>
          
          {user && (
            <div className="ml-4 pl-4 border-l border-white/10">
              <span className="text-xs text-muted-foreground">{user.email}</span>
            </div>
          )}
        </div>
      </header>

      {/* React Flow Canvas */}
      <main className="flex-1 w-full h-full relative" style={{ background: '#0a0a0a' }} onClick={() => setShowDropdown(false)}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          fitView
          className="dark"
        >
          <Background color="#ffffff" gap={20} size={1} opacity={0.05} />
          <Controls className="bg-black/50 border-white/10 fill-white" />
        </ReactFlow>
      </main>

    </div>
  );
}

