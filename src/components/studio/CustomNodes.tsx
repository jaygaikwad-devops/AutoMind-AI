import { Handle, Position, useReactFlow } from '@xyflow/react';
import { Type, Video, Send, Settings2, Hash, PenTool, X } from 'lucide-react';

export function PromptNode({ id, data }: { id: string; data: any }) {
  const { updateNodeData, setNodes } = useReactFlow();

  const deleteNode = () => setNodes((nds) => nds.filter((n) => n.id !== id));

  return (
    <div className="glass-strong rounded-xl p-4 w-64 border border-white/10 relative shadow-xl group">
      <button onClick={deleteNode} className="absolute top-2 right-2 text-white/40 hover:text-red-400 opacity-0 group-hover:opacity-100 transition"><X className="w-4 h-4" /></button>
      <div className="flex items-center gap-2 mb-3 text-sm font-semibold text-white/90">
        <div className="p-1.5 rounded-lg bg-[var(--neon-violet)]/20 text-[var(--neon-violet)]">
          <Type className="w-4 h-4" />
        </div>
        Text Input
      </div>
      <textarea
        className="nodrag w-full bg-white/5 border border-white/10 rounded-lg p-2 text-xs focus:outline-none focus:border-[var(--neon-violet)] resize-none"
        rows={3}
        placeholder="Enter your video prompt..."
        value={data.prompt || ''}
        onChange={(e) => updateNodeData(id, { prompt: e.target.value })}
      />
      <Handle type="source" position={Position.Right} className="w-3 h-3 bg-[var(--neon-violet)] border-2 border-background" />
    </div>
  );
}

export function VideoNode({ id, data }: { id: string; data: any }) {
  const { updateNodeData, setNodes } = useReactFlow();

  const deleteNode = () => setNodes((nds) => nds.filter((n) => n.id !== id));

  return (
    <div className="glass-strong rounded-xl p-4 w-64 border border-white/10 relative shadow-xl group">
      <button onClick={deleteNode} className="absolute top-2 right-2 text-white/40 hover:text-red-400 opacity-0 group-hover:opacity-100 transition"><X className="w-4 h-4" /></button>
      <Handle type="target" position={Position.Left} className="w-3 h-3 bg-[var(--neon-cyan)] border-2 border-background" />
      <div className="flex items-center gap-2 mb-3 text-sm font-semibold text-white/90">
        <div className="p-1.5 rounded-lg bg-[var(--neon-cyan)]/20 text-[var(--neon-cyan)]">
          <Video className="w-4 h-4" />
        </div>
        Premium Generation
      </div>
      <div className="space-y-3">
        <div>
          <label className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1 block">Visual Style</label>
          <select 
            className="nodrag w-full bg-white/5 border border-white/10 rounded p-1.5 text-xs text-white/90"
            value={data.style || 'cinematic'}
            onChange={(e) => updateNodeData(id, { style: e.target.value })}
          >
            <option value="cinematic">Cinematic Reality</option>
            <option value="anime">Anime / Manga</option>
            <option value="3d">3D Animation</option>
          </select>
        </div>
        <div>
          <label className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1 block">Voice (ElevenLabs)</label>
          <select 
            className="nodrag w-full bg-white/5 border border-white/10 rounded p-1.5 text-xs text-white/90"
            value={data.voice || 'rachel'}
            onChange={(e) => updateNodeData(id, { voice: e.target.value })}
          >
            <option value="rachel">Rachel (Calm)</option>
            <option value="bella">Bella (Energetic)</option>
            <option value="elli">Elli (Emotional)</option>
          </select>
        </div>
        <div>
          <label className="text-[10px] text-muted-foreground uppercase tracking-wider mb-1 block">Language</label>
          <select 
            className="nodrag w-full bg-white/5 border border-white/10 rounded p-1.5 text-xs text-white/90"
            value={data.language || 'en'}
            onChange={(e) => updateNodeData(id, { language: e.target.value })}
          >
            <option value="en">English</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
          </select>
        </div>
      </div>
      <Handle type="source" position={Position.Right} className="w-3 h-3 bg-[var(--neon-cyan)] border-2 border-background" />
    </div>
  );
}

export function CaptionNode({ id, data }: { id: string; data: any }) {
  const { updateNodeData, setNodes } = useReactFlow();

  const deleteNode = () => setNodes((nds) => nds.filter((n) => n.id !== id));

  return (
    <div className="glass-strong rounded-xl p-4 w-64 border border-white/10 relative shadow-xl group">
      <button onClick={deleteNode} className="absolute top-2 right-2 text-white/40 hover:text-red-400 opacity-0 group-hover:opacity-100 transition"><X className="w-4 h-4" /></button>
      <Handle type="target" position={Position.Left} className="w-3 h-3 bg-[#F5A623] border-2 border-background" />
      <div className="flex items-center gap-2 mb-3 text-sm font-semibold text-white/90">
        <div className="p-1.5 rounded-lg bg-[#F5A623]/20 text-[#F5A623]">
          <PenTool className="w-4 h-4" />
        </div>
        Smart Captions
      </div>
      <select 
        className="nodrag w-full bg-white/5 border border-white/10 rounded-lg p-2 text-xs focus:outline-none focus:border-[#F5A623]"
        value={data.tone || 'engaging'}
        onChange={(e) => updateNodeData(id, { tone: e.target.value })}
      >
        <option value="engaging" className="bg-background">Engaging / Viral</option>
        <option value="professional" className="bg-background">Professional / Brand</option>
        <option value="funny" className="bg-background">Funny / Edgy</option>
      </select>
      <Handle type="source" position={Position.Right} className="w-3 h-3 bg-[#F5A623] border-2 border-background" />
    </div>
  );
}

export function HashtagNode({ id, data }: { id: string; data: any }) {
  const { updateNodeData, setNodes } = useReactFlow();

  const deleteNode = () => setNodes((nds) => nds.filter((n) => n.id !== id));

  return (
    <div className="glass-strong rounded-xl p-4 w-64 border border-white/10 relative shadow-xl group">
      <button onClick={deleteNode} className="absolute top-2 right-2 text-white/40 hover:text-red-400 opacity-0 group-hover:opacity-100 transition"><X className="w-4 h-4" /></button>
      <Handle type="target" position={Position.Left} className="w-3 h-3 bg-[#7ED321] border-2 border-background" />
      <div className="flex items-center gap-2 mb-3 text-sm font-semibold text-white/90">
        <div className="p-1.5 rounded-lg bg-[#7ED321]/20 text-[#7ED321]">
          <Hash className="w-4 h-4" />
        </div>
        Viral Hashtags
      </div>
      <input 
        type="text"
        className="nodrag w-full bg-white/5 border border-white/10 rounded-lg p-2 text-xs focus:outline-none focus:border-[#7ED321]"
        placeholder="Niche (e.g., Tech, Fitness)"
        value={data.niche || ''}
        onChange={(e) => updateNodeData(id, { niche: e.target.value })}
      />
      <Handle type="source" position={Position.Right} className="w-3 h-3 bg-[#7ED321] border-2 border-background" />
    </div>
  );
}

export function SocialNode({ id, data }: { id: string; data: any }) {
  const { updateNodeData, setNodes } = useReactFlow();

  const deleteNode = () => setNodes((nds) => nds.filter((n) => n.id !== id));

  return (
    <div className="glass-strong rounded-xl p-4 w-64 border border-white/10 relative shadow-xl group">
      <button onClick={deleteNode} className="absolute top-2 right-2 text-white/40 hover:text-red-400 opacity-0 group-hover:opacity-100 transition"><X className="w-4 h-4" /></button>
      <Handle type="target" position={Position.Left} className="w-3 h-3 bg-[#E1306C] border-2 border-background" />
      <div className="flex items-center gap-2 mb-3 text-sm font-semibold text-white/90">
        <div className="p-1.5 rounded-lg bg-[#E1306C]/20 text-[#E1306C]">
          <Send className="w-4 h-4" />
        </div>
        Social Publish
      </div>
      <select 
        className="nodrag w-full bg-white/5 border border-white/10 rounded-lg p-2 text-xs focus:outline-none focus:border-[#E1306C]"
        value={data.platform || 'instagram'}
        onChange={(e) => updateNodeData(id, { platform: e.target.value })}
      >
        <option value="instagram" className="bg-background">Instagram</option>
        <option value="facebook" className="bg-background">Facebook</option>
        <option value="shopify" className="bg-background">Shopify</option>
      </select>
    </div>
  );
}
