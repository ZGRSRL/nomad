import React, { useState, useEffect, useRef, useMemo } from 'react';
import { Rss, Globe, Zap, Database, Shield, Sparkles, Cpu, ChevronRight, Loader, Plus, Save, Send, Share2, Search, Filter } from 'lucide-react';
import ForceGraph2D from 'react-force-graph-2d';
import * as d3 from 'd3';

// --- RENK PALETİ (Siberpunk Teması) ---
const TAG_COLORS = {
  "AI": "#06b6d4",          // Neon Cyan
  "CYBERSEC": "#f43f5e",    // Neon Red
  "TECH": "#a855f7",        // Neon Purple
  "SCIENCE": "#22c55e",     // Neon Green
  "CRYPTO": "#f59e0b",      // Neon Orange
  "DEV": "#3b82f6",         // Neon Blue
  "DEFAULT": "#64748b"      // Slate Gray
};

const App = () => {
  // --- STATE ---
  const [view, setView] = useState('feed');
  const [articles, setArticles] = useState([]);
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [categories, setCategories] = useState(['ALL']);
  const [activeTab, setActiveTab] = useState('ALL');

  // Loading States
  const [loadingFeeds, setLoadingFeeds] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);

  // Graph Data & Filters
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [filterTag, setFilterTag] = useState('ALL'); // Hangi tag seçili?
  const [searchQuery, setSearchQuery] = useState(''); // Arama metni
  const [selectedNode, setSelectedNode] = useState(null); // Tıklanan Düğüm
  const [hoverNode, setHoverNode] = useState(null); // Üzerine gelinen Düğüm

  // Chat States
  const [chatHistory, setChatHistory] = useState([
    { role: 'ai', content: 'Nomad OS v2.2 Online. Advanced Neural Network Active.' }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef(null);

  // Modal States
  const [showModal, setShowModal] = useState(false);
  const [newFeed, setNewFeed] = useState({ url: '', category: '', name: '' });

  const API_URL = 'http://localhost:8001';

  // Graph Refs & D3 Tuning
  const graphRef = useRef();
  const containerRef = useRef();
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  useEffect(() => {
    // Canvas boyutunu container'a uydur
    if (containerRef.current) {
      setDimensions({
        width: containerRef.current.offsetWidth,
        height: containerRef.current.offsetHeight
      });

      const ro = new ResizeObserver(entries => {
        for (let entry of entries) {
          setDimensions({
            width: entry.contentRect.width,
            height: entry.contentRect.height
          });
        }
      });
      ro.observe(containerRef.current);
      return () => ro.disconnect();
    }
  }, [view, selectedNode]); // selectedNode panel açınca boyutu etkiler

  useEffect(() => {
    // Fizik Motoru Ayarları
    if (graphRef.current) {
      graphRef.current.d3Force('charge').strength(-400);
      graphRef.current.d3Force('link').distance(70);
      graphRef.current.d3Force('collide',
        // eslint-disable-next-line no-undef
        d3.forceCollide().radius(node => 10).strength(1)
      );
    }
  }, [graphData, view]);

  useEffect(() => {
    fetchCategories();
    if (view === 'feed') fetchNews();
    if (view === 'graph') fetchGraphData();
  }, [activeTab, view]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory, view]);

  const fetchCategories = async () => {
    try {
      const res = await fetch(`${API_URL}/categories`);
      const data = await res.json();
      setCategories(data);
    } catch (e) { console.error("Cat Err", e); }
  };

  const fetchNews = async () => {
    setLoadingFeeds(true);
    try {
      const res = await fetch(`${API_URL}/feeds?category=${activeTab}`);
      const data = await res.json();
      setArticles(data);
    } catch (error) { console.error("RSS Err:", error); }
    finally { setLoadingFeeds(false); }
  };

  const fetchGraphData = async () => {
    try {
      const res = await fetch(`${API_URL}/graph-data`);
      const data = await res.json();
      setGraphData(data);
    } catch (e) { console.error("Graph Err", e); }
  };

  const handleArticleClick = async (article) => {
    setSelectedArticle(article);
    setAnalysis(null);
    setAnalyzing(true);
    try {
      const res = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: article.title, content: article.summary })
      });
      const result = await res.json();
      setAnalysis(result);
    } catch (error) { console.error("Analysis Err:", error); }
    finally { setAnalyzing(false); }
  };

  const handleSaveToMemory = async () => {
    if (!analysis) return;
    const tagString = analysis.tags ? analysis.tags.join(", ") : "GENERAL";
    const textToSave = `${selectedArticle.title} | Tags: ${tagString} | Insight: ${analysis.aiInsight} | Link: ${selectedArticle.link}`;

    try {
      await fetch(`${API_URL}/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: textToSave })
      });
      alert("Memory Block Encrypted & Saved.");
      if (view === 'graph') fetchGraphData();
    } catch (e) { alert("Save failed."); }
  };

  const handleAddFeed = async () => {
    if (!newFeed.url || !newFeed.category) return;
    try {
      await fetch(`${API_URL}/feeds/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: newFeed.url,
          category: newFeed.category,
          source_name: newFeed.name || "CUSTOM"
        })
      });
      setShowModal(false);
      setNewFeed({ url: '', category: '', name: '' });
      fetchCategories();
      alert("Uplink Established.");
    } catch (e) { alert("Feed connection failed."); }
  };

  const handleChatSend = async () => {
    if (!chatInput.trim()) return;
    const userMsg = chatInput;
    setChatHistory(prev => [...prev, { role: 'user', content: userMsg }]);
    setChatInput('');
    setChatLoading(true);

    try {
      const res = await fetch(`${API_URL}/ask`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: userMsg })
      });
      const data = await res.json();
      setChatHistory(prev => [...prev, { role: 'ai', content: data.answer }]);
    } catch (e) {
      setChatHistory(prev => [...prev, { role: 'ai', content: "Connection lost." }]);
    } finally {
      setChatLoading(false);
    }
  };

  // --- GRAPH MANTIKLARI (Filtreleme & Renk) ---

  // 1. Düğüm Rengi Belirle
  const getNodeColor = (node) => {
    if (!node.tags || node.tags.length === 0) return TAG_COLORS.DEFAULT;
    // İlk tag'e göre renk ver, yoksa varsayılan
    const firstTag = node.tags[0].toUpperCase();
    return TAG_COLORS[firstTag] || TAG_COLORS.DEFAULT;
  };

  // 2. Grafikteki tüm benzersiz tag'leri bul (Filtre menüsü için)
  const uniqueTags = useMemo(() => {
    const tags = new Set(['ALL']);
    graphData.nodes.forEach(node => {
      if (node.tags) node.tags.forEach(t => tags.add(t));
    });
    return Array.from(tags);
  }, [graphData]);

  // 3. Veriyi Filtrele (Hem Tag hem Arama Sorgusu)
  const filteredGraphData = useMemo(() => {
    let { nodes, links } = graphData;

    // A. Tag Filtresi
    if (filterTag !== 'ALL') {
      nodes = nodes.filter(node => node.tags && node.tags.includes(filterTag));
    }

    // B. Arama Sorgusu (Başlık içinde ara)
    if (searchQuery.trim() !== '') {
      const lowerQuery = searchQuery.toLowerCase();
      nodes = nodes.filter(node => node.label.toLowerCase().includes(lowerQuery));
    }

    // C. Yetim Linkleri Temizle (Filtrelenmiş node'lara bağlı olmayan linkleri at)
    const activeNodeIds = new Set(nodes.map(n => n.id));
    links = links.filter(l =>
      (activeNodeIds.has(l.source.id) || activeNodeIds.has(l.source)) &&
      (activeNodeIds.has(l.target.id) || activeNodeIds.has(l.target))
    );

    return { nodes, links };
  }, [graphData, filterTag, searchQuery]);

  // Helper to extract insight for hover
  const getHoverLabel = (node) => {
    const insight = node.full_content.split('| Insight: ')[1]?.split('|')[0] || '';
    return `${node.label}\n\n${insight.substring(0, 100)}${insight.length > 100 ? '...' : ''}`;
  };


  return (
    <div className="flex h-screen bg-cyber-bg text-cyber-text font-sans overflow-hidden selection:bg-cyber-primary selection:text-black">

      {/* SIDEBAR */}
      <div className="w-16 border-r border-cyber-border flex flex-col items-center py-6 gap-8 bg-cyber-bg/50 backdrop-blur-sm z-20">
        <div className="p-2 bg-cyber-primary/10 rounded-lg border border-cyber-primary/20 text-cyber-primary">
          <Globe size={24} />
        </div>
        <nav className="flex flex-col gap-6 w-full items-center">
          <NavIcon icon={<Rss size={20} />} active={view === 'feed'} onClick={() => setView('feed')} />
          <NavIcon icon={<Database size={20} />} active={view === 'chat'} onClick={() => setView('chat')} />
          <NavIcon icon={<Share2 size={20} />} active={view === 'graph'} onClick={() => setView('graph')} />
        </nav>
      </div>

      {/* VIEW: FEED */}
      {view === 'feed' && (
        <div className="flex-1 flex flex-col md:flex-row overflow-hidden relative">
          <div className="w-full md:w-[450px] flex flex-col border-r border-cyber-border bg-cyber-bg/30 backdrop-blur-md z-10">
            <div className="h-16 border-b border-cyber-border flex items-center justify-between px-6">
              <span className="font-bold text-cyber-textLight tracking-wider text-sm">SIGNAL STREAM</span>
              <button onClick={() => setShowModal(true)} className="p-1 hover:text-white hover:bg-cyber-border rounded"><Plus size={18} /></button>
            </div>
            <div className="p-4 flex gap-2 overflow-x-auto no-scrollbar">
              {categories.map(tab => (
                <button key={tab} onClick={() => setActiveTab(tab)} className={`px-4 py-1.5 rounded-full text-[10px] font-mono border transition-all whitespace-nowrap ${activeTab === tab ? 'border-cyber-primary bg-cyber-primary/10 text-cyber-primary' : 'border-cyber-border text-cyber-text'}`}>{tab}</button>
              ))}
            </div>
            <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
              {loadingFeeds ? <div className="text-center p-10"><Loader className="animate-spin mx-auto" /></div> :
                articles.map((item) => (
                  <div key={item.id} onClick={() => handleArticleClick(item)} className={`p-4 rounded-xl border cursor-pointer transition-all ${selectedArticle?.id === item.id ? 'bg-cyber-panel border-cyber-primary/50' : 'bg-cyber-panel/40 border-cyber-border hover:border-cyber-text/30'}`}>
                    <div className="flex justify-between items-start mb-2">
                      <span className="text-[10px] font-mono text-cyber-primary uppercase">{item.source}</span>
                      <span className="text-[10px] font-mono text-cyber-text/60">{item.time}</span>
                    </div>
                    <h3 className={`font-medium text-sm leading-snug ${selectedArticle?.id === item.id ? 'text-white' : 'text-cyber-textLight'}`}>{item.title}</h3>
                  </div>
                ))}
            </div>
          </div>

          <div className="flex-1 bg-cyber-bg/40 p-8 overflow-y-auto relative flex flex-col gap-6">
            {selectedArticle ? (
              <div className="max-w-3xl mt-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                <div className="mb-6">
                  <span className="px-2 py-1 rounded bg-cyber-primary/10 border border-cyber-primary/20 text-cyber-primary text-[10px] font-mono uppercase">{selectedArticle.category}</span>
                  <h1 className="text-2xl font-bold text-white mt-4 mb-4 glow-text">{selectedArticle.title}</h1>
                  <a href={selectedArticle.link} target="_blank" className="text-xs text-cyber-text hover:text-cyber-primary font-mono">SOURCE LINK</a>
                </div>
                {analyzing ? (
                  <div className="h-64 border border-cyber-border border-dashed rounded-xl flex items-center justify-center text-cyber-primary/50 animate-pulse">DECRYPTING...</div>
                ) : analysis ? (
                  <div className="grid grid-cols-1 gap-6">
                    <div className="grid grid-cols-2 gap-6">
                      <div className="bg-cyber-panel/60 border border-cyber-border rounded-xl p-6">
                        <h3 className="text-cyber-primary font-mono text-xs uppercase mb-4 flex items-center gap-2"><Sparkles size={14} /> AI Synthesis</h3>
                        <p className="text-cyber-textLight text-sm">{analysis.summary}</p>
                        <div className="mt-4 flex gap-2 flex-wrap">
                          {analysis.tags?.map(t => <span key={t} className="px-2 py-1 bg-cyber-bg border border-cyber-border text-[10px] rounded text-cyber-textLight" style={{ color: TAG_COLORS[t] || TAG_COLORS.DEFAULT, borderColor: (TAG_COLORS[t] || TAG_COLORS.DEFAULT) + '40' }}>{t}</span>)}
                        </div>
                      </div>
                      <div className="bg-cyber-panel/60 border border-cyber-border rounded-xl p-6 relative">
                        <button onClick={handleSaveToMemory} className="absolute top-4 right-4 text-cyber-accent hover:text-white" title="Save to Memory"><Save size={16} /></button>
                        <h3 className="text-cyber-accent font-mono text-xs uppercase mb-4 flex items-center gap-2"><Zap size={14} /> Strategic Insight</h3>
                        <p className="text-cyber-textLight text-sm">{analysis.aiInsight}</p>
                      </div>
                    </div>
                    <div className="bg-cyber-primary/10 border border-cyber-primary/20 rounded-xl p-5">
                      <h4 className="text-cyber-primary text-xs font-mono uppercase mb-1">Action</h4>
                      <p className="text-white text-sm font-medium">{analysis.action}</p>
                    </div>
                  </div>
                ) : <div className="p-6 border border-cyber-border rounded-xl text-center text-cyber-text/50">// WAITING ANALYSIS...</div>}
              </div>
            ) : <div className="flex h-full items-center justify-center text-cyber-text/30 font-mono">SELECT A SIGNAL</div>}
          </div>
        </div>
      )}

      {/* VIEW: CHAT */}
      {view === 'chat' && (
        <div className="flex-1 flex flex-col relative bg-cyber-bg/40">
          <div className="flex-1 overflow-y-auto p-8 custom-scrollbar">
            <div className="max-w-3xl mx-auto space-y-6">
              {chatHistory.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] p-4 rounded-xl border ${msg.role === 'user' ? 'bg-cyber-primary/10 border-cyber-primary/30 text-white' : 'bg-cyber-panel border-cyber-border text-cyber-textLight'}`}>
                    <div className="text-[10px] font-mono opacity-50 mb-1 uppercase">{msg.role === 'user' ? 'OPERATOR' : 'NOMAD AI'}</div>
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                  </div>
                </div>
              ))}
              {chatLoading && <div className="flex justify-start"><div className="bg-cyber-panel p-4 rounded-xl border border-cyber-border text-cyber-primary animate-pulse text-xs font-mono">TYPING...</div></div>}
              <div ref={chatEndRef} />
            </div>
          </div>
          <div className="p-6 border-t border-cyber-border bg-cyber-bg/80 backdrop-blur">
            <div className="max-w-3xl mx-auto flex gap-4">
              <input value={chatInput} onChange={(e) => setChatInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleChatSend()} placeholder="Query the database..." className="flex-1 bg-cyber-panel border border-cyber-border rounded-lg px-4 py-3 text-white focus:border-cyber-primary focus:outline-none font-mono text-sm" />
              <button onClick={handleChatSend} className="bg-cyber-primary text-black px-6 rounded-lg font-bold hover:bg-cyan-300 transition-colors"><Send size={20} /></button>
            </div>
          </div>
        </div>
      )}

      {/* VIEW: GRAPH (ADVANCED) */}
      {view === 'graph' && (
        <div className="flex-1 bg-[#020617] relative overflow-hidden flex flex-row">

          <div className="flex-1 relative flex flex-col h-full" ref={containerRef}>
            {/* GRAPH HUD / CONTROLS */}
            <div className="absolute top-4 left-6 z-10 flex flex-col gap-4 w-72 animate-in fade-in slide-in-from-left-4 duration-500">
              <div className="bg-cyber-panel/90 p-4 rounded-xl border border-cyber-border backdrop-blur shadow-xl">
                <h2 className="text-sm font-bold text-white glow-text flex items-center gap-2 mb-3">
                  <Share2 size={16} className="text-cyber-primary" /> NEURAL NET CONTROL
                </h2>

                {/* Arama Inputu */}
                <div className="relative mb-4">
                  <Search className="absolute left-3 top-2.5 text-cyber-text" size={14} />
                  <input
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full bg-cyber-bg border border-cyber-border rounded py-2 pl-9 pr-2 text-xs text-white focus:border-cyber-primary outline-none"
                    placeholder="Search nodes..."
                  />
                </div>

                {/* Tag Filtreleri */}
                <div className="space-y-2">
                  <div className="text-[10px] text-cyber-text/60 font-mono uppercase flex items-center gap-1"><Filter size={10} /> Filter by Tag</div>
                  <div className="flex flex-wrap gap-2 max-h-40 overflow-y-auto custom-scrollbar">
                    {uniqueTags.map(tag => (
                      <button
                        key={tag}
                        onClick={() => setFilterTag(tag)}
                        className={`px-2 py-1 text-[10px] rounded border transition-all ${filterTag === tag ? 'bg-cyber-primary text-black border-cyber-primary' : 'bg-cyber-bg text-cyber-text border-cyber-border hover:border-white'}`}
                        style={filterTag === tag ? {} : { borderColor: (TAG_COLORS[tag] || TAG_COLORS.DEFAULT) + '40', color: (TAG_COLORS[tag] || TAG_COLORS.DEFAULT) }}
                      >
                        {tag}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* GRAPH CANVAS */}
            <div className="w-full h-full">
              <ForceGraph2D
                ref={graphRef}
                width={dimensions.width}
                height={dimensions.height}
                graphData={filteredGraphData}
                nodeLabel={getHoverLabel} // Rich Tooltip (Native)
                nodeColor={getNodeColor}
                linkColor={() => "#1e293b"}
                backgroundColor="#020617"
                nodeRelSize={8}
                linkWidth={1.5}
                linkDirectionalParticles={2}
                linkDirectionalParticleSpeed={0.005}
                onNodeClick={node => {
                  console.log("Clicked:", node);
                  setSelectedNode(node);
                  if (graphRef.current) {
                    graphRef.current.centerAt(node.x, node.y, 1000);
                    graphRef.current.zoom(3, 2000);
                  }
                }}
                onNodeHover={setHoverNode}
                d3AlphaDecay={0.02}
                d3VelocityDecay={0.3}
                cooldownTicks={100}
                onEngineStop={() => {
                  // Initial Zoom Loop fix
                }}
              />
            </div>
          </div>

          {/* SIDE DETAIL PANEL (WIDER) */}
          {selectedNode && (
            <div className="absolute right-0 top-0 h-full w-[500px] bg-cyber-panel/95 backdrop-blur-xl border-l border-cyber-border shadow-2xl z-50 overflow-y-auto animate-in slide-in-from-right duration-500">
              <div className="p-8 space-y-6">
                <div className="flex items-start justify-between">
                  <span className="px-2 py-1 bg-cyber-primary/10 text-cyber-primary rounded text-[10px] font-mono border border-cyber-primary/20">
                    MEMORY NODE #{selectedNode.id}
                  </span>
                  <button onClick={() => setSelectedNode(null)} className="text-cyber-text hover:text-white transition-colors">
                    <Plus className="rotate-45" size={24} />
                  </button>
                </div>

                <div>
                  <h2 className="text-2xl font-bold text-white leading-tight glow-text mb-4">
                    {selectedNode.label}
                  </h2>
                  <div className="flex flex-wrap gap-2 mb-6">
                    {selectedNode.tags?.map(t => (
                      <span key={t} className="text-[10px] px-2 py-0.5 rounded border" style={{ color: (TAG_COLORS[t] || TAG_COLORS.DEFAULT), borderColor: (TAG_COLORS[t] || TAG_COLORS.DEFAULT) + '40' }}>
                        {t}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="space-y-6">
                  <div className="bg-cyber-bg/50 p-6 rounded-xl border border-cyber-border">
                    <h3 className="text-xs font-mono text-cyber-text/50 uppercase mb-3 flex items-center gap-2"><Sparkles size={12} /> Analysis & Insight</h3>
                    <p className="text-sm text-cyber-textLight whitespace-pre-wrap leading-relaxed">
                      {(selectedNode.full_content?.split('| Insight: ')[1]?.split('|')[0] || selectedNode.full_content?.split('|')[0]) || "No details available."}
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <button className="py-3 bg-cyber-panel border border-cyber-primary/30 text-cyber-primary font-bold rounded-lg hover:bg-cyber-primary/10 transition-colors text-xs flex items-center justify-center gap-2">
                      <Zap size={14} /> RE-ANALYZE
                    </button>

                    {selectedNode.full_content.includes('| Link:') && (
                      <a
                        href={selectedNode.full_content.split('| Link: ')[1]?.trim()}
                        target="_blank"
                        rel="noreferrer"
                        className="py-3 bg-cyber-primary text-black font-bold rounded-lg hover:bg-cyan-300 transition-colors text-xs flex items-center justify-center gap-2"
                      >
                        <Share2 size={14} /> GO TO SOURCE
                      </a>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* MODAL: ADD RSS */}
      {showModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-cyber-panel border border-cyber-border rounded-2xl p-8 w-full max-w-md shadow-[0_0_50px_rgba(6,182,212,0.1)]">
            <h2 className="text-xl font-bold text-white mb-6 glow-text">ADD NEW SIGNAL SOURCE</h2>
            <div className="space-y-4">
              <div>
                <label className="text-xs font-mono text-cyber-text/70 block mb-2">RSS URL</label>
                <input value={newFeed.url} onChange={e => setNewFeed({ ...newFeed, url: e.target.value })} className="w-full bg-cyber-bg border border-cyber-border rounded p-3 text-white text-sm focus:border-cyber-primary outline-none" placeholder="https://..." />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-mono text-cyber-text/70 block mb-2">CATEGORY</label>
                  <input value={newFeed.category} onChange={e => setNewFeed({ ...newFeed, category: e.target.value })} className="w-full bg-cyber-bg border border-cyber-border rounded p-3 text-white text-sm focus:border-cyber-primary outline-none" placeholder="TECH" />
                </div>
                <div>
                  <label className="text-xs font-mono text-cyber-text/70 block mb-2">NAME</label>
                  <input value={newFeed.name} onChange={e => setNewFeed({ ...newFeed, name: e.target.value })} className="w-full bg-cyber-bg border border-cyber-border rounded p-3 text-white text-sm focus:border-cyber-primary outline-none" placeholder="WIRED" />
                </div>
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button onClick={() => setShowModal(false)} className="px-4 py-2 text-xs font-mono text-cyber-text hover:text-white">CANCEL</button>
                <button onClick={handleAddFeed} className="px-6 py-2 bg-cyber-primary text-black font-bold rounded text-xs hover:bg-cyan-300">ESTABLISH LINK</button>
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

const NavIcon = ({ icon, active, onClick }) => (
  <button onClick={onClick} className={`p-3 rounded-xl transition-all ${active ? 'bg-cyber-primary text-black shadow-[0_0_15px_#06b6d4]' : 'text-cyber-text hover:text-white hover:bg-cyber-panel'}`}>
    {icon}
  </button>
);

export default App;
