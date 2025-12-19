import React, { useState, useEffect, useRef, useMemo } from 'react';
import { Rss, Globe, Zap, Database, Shield, Sparkles, Cpu, ChevronRight, Loader, Plus, Save, Send, Share2, Search, Filter, HardDrive, BarChart3, LayoutDashboard, TrendingUp, Activity } from 'lucide-react';
import ForceGraph2D from 'react-force-graph-2d';
import * as d3 from 'd3';
import SidebarTree from './components/SidebarTree';
import SignalGrid from './components/SignalGrid';
import OperationDeck from './components/OperationDeck';

import LoginScreen from './components/LoginScreen';

// --- RENK PALETİ (Siberpunk Teması) ---
// ... (Keep existing colors)

// --- CONSTANTS ---
const PRESET_FEEDS = [
  { name: 'Wired', category: 'TECH', url: 'https://www.wired.com/feed/rss' },
  { name: 'CNN', category: 'NEWS', url: 'http://rss.cnn.com/rss/cnn_topstories.rss' },
  { name: 'BBC News', category: 'NEWS', url: 'http://feeds.bbci.co.uk/news/rss.xml' },
  { name: 'NASA Breaking News', category: 'SPACE', url: 'https://www.nasa.gov/rss/dyn/breaking_news.rss' },
  { name: 'Scientific American', category: 'SCIENCE', url: 'http://rss.sciam.com/ScientificAmerican-Global' }
];

const App = () => {

  // --- ERROR BOUNDARY ---

  // --- AUTH STATE ---
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const authStatus = localStorage.getItem('nomad_auth');
    if (authStatus === 'GRANTED') {
      setIsAuthenticated(true);
    } else {
      setIsAuthenticated(false);
    }
  }, []);

  // --- MAIN STATE ---
  // v3.1 Trend Radar UI
  const [view, setView] = useState('feed');
  const [articles, setArticles] = useState([]);
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [categories, setCategories] = useState(['ALL']);
  const [activeTab, setActiveTab] = useState('ALL');
  const [trends, setTrends] = useState([]);
  const [stats, setStats] = useState({
    total_sources: 0,
    total_intel: 0,
    top_trend: 'ANALYZING...',
    recent_alerts: [],
    system_status: 'CHECKING'
  });

  // Loading States
  const [loadingFeeds, setLoadingFeeds] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState(null);

  // Scan States
  const [scanUrl, setScanUrl] = useState('');
  const [scanning, setScanning] = useState(false);
  const [scanResult, setScanResult] = useState(null);

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

  // DYNAMIC API URL STRATEGY
  const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8001'
    : 'https://nomad-backend-xxs2tligqa-ew.a.run.app';

  // Graph Refs & D3 Tuning
  const graphRef = useRef();
  const containerRef = useRef();
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  useEffect(() => {
    // Canvas boyutunu container'a uydur (ResizeObserver ile daha sağlam)
    if (!containerRef.current) return;

    const resizeObserver = new ResizeObserver(entries => {
      for (let entry of entries) {
        setDimensions({
          width: entry.contentRect.width,
          height: entry.contentRect.height
        });
      }
    });

    resizeObserver.observe(containerRef.current);

    return () => resizeObserver.disconnect();
  }, [view]); // Sadece view değişince observer'ı yeniden başlatmak yeterli

  // --- AUTH CHECK moved to end to prevent Hook Errors ---

  useEffect(() => {
    if (!isAuthenticated) return;
    fetchCategories();
    fetchTrends();
    fetchStats();
    if (view === 'feed') fetchNews();
    if (view === 'graph') fetchGraphData();
  }, [activeTab, view]);

  useEffect(() => {
    if (!isAuthenticated) return;
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory, view]);

  const fetchCategories = async () => {
    try {
      const res = await fetch(`${API_URL}/categories`);
      const data = await res.json();
      setCategories(data);
    } catch (e) { console.error("Cat Err", e); }
  };

  const fetchTrends = async () => {
    try { const res = await fetch(`${API_URL}/trends`); const data = await res.json(); setTrends(data); } catch (e) { console.error("Trend Err", e); }
  };

  const fetchStats = async () => {
    try { const res = await fetch(`${API_URL}/stats`); const data = await res.json(); setStats(data); } catch (e) { console.error("Stats Err", e); }
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
      const res = await fetch(`${API_URL}/feeds/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: newFeed.url,
          category: newFeed.category,
          source_name: newFeed.name || "CUSTOM"
        })
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || "Connection refused by target.");
      }

      setShowModal(false);
      setNewFeed({ url: '', category: '', name: '' });
      fetchCategories();
      fetchNews();
      alert(`Uplink Established: ${data.message}`);
    } catch (e) {
      console.error(e);
      alert(`FEED ERROR: ${e.message}`);
    }
  };

  const handleSendToHQ = async () => {
    if (!selectedArticle) return;

    // 1. Prepare Intelligence Report (HTML Format)
    const reportHtml = `
      <html>
      <head>
        <style>
          body { font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; }
          h1 { color: #000; border-bottom: 2px solid #06b6d4; padding-bottom: 10px; }
          .meta { color: #666; font-size: 0.9em; margin-bottom: 20px; }
          .tag { background: #eee; padding: 2px 8px; border-radius: 4px; font-size: 0.8em; margin-right: 5px; }
          .insight { background: #f0fdf4; border-left: 4px solid #22c55e; padding: 15px; margin: 20px 0; }
          .summary { background: #f8fafc; padding: 15px; border-radius: 8px; }
        </style>
      </head>
      <body>
        <h1>INTEL REPORT: ${selectedArticle.title}</h1>
        <div class="meta">
          <strong>Source:</strong> ${selectedArticle.source_name} | 
          <strong>Date:</strong> ${selectedArticle.time} | 
          <strong>Category:</strong> ${selectedArticle.category}
        </div>

        <div class="insight">
          <h3>⚡ Strategic Insight</h3>
          <p>${analysis ? analysis.aiInsight : "Analysis pending..."}</p>
        </div>

        <div class="summary">
          <h3>Exec Summary</h3>
          <p>${selectedArticle.summary}</p>
        </div>

        <h3>Original Signal Data</h3>
        <p><a href="${selectedArticle.link}">Original Source Link</a></p>
        
        <p><em>Generated by Nomad OS v4.5 "Visual Intelligence"</em></p>
      </body>
      </html>
    `;

    try {
      const res = await fetch(`${API_URL}/upload-report`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: `INTEL: ${selectedArticle.title}`,
          content: reportHtml
        })
      });

      const data = await res.json();

      if (data.status === 'success') {
        alert(`✅ HQ UPLINK SUCCESSFUL\n\nReport archived in 'Nomad Intelligence' Vault.\n\nSecure Link: ${data.link}`);
      } else {
        throw new Error(data.message);
      }
    } catch (e) {
      alert(`⚠️ UPLINK FAILED: ${e.message}\n\nCheck credentials.json in backend.`);
    }
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

  const handleDeepScan = async () => {
    if (!scanUrl) return;
    setScanning(true);
    setScanResult(null);
    try {
      const res = await fetch(`${API_URL}/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: scanUrl })
      });
      const data = await res.json();
      setScanResult(data);
    } catch (e) { alert("Scan failed. Target offline or blocking protocols active."); }
    finally { setScanning(false); }
  };

  const handleSaveScan = async () => {
    if (!scanResult) return;

    const tagString = scanResult.tags ? scanResult.tags.join(", ") : "GENERAL";
    const textToSave = `${scanResult.title} | Tags: ${tagString} | Insight: ${scanResult.aiInsight} | Link: ${scanResult.link}`;

    try {
      await fetch(`${API_URL}/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: textToSave })
      });
      alert("Intelligence Encrypted & Stored.");
      setScanUrl('');
      setScanResult(null);
      setView('graph');
    } catch (e) { alert("Save failed."); }
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



  // --- AUTH CHECK (THE GATE) ---
  if (!isAuthenticated) {
    return <LoginScreen onLogin={() => setIsAuthenticated(true)} />;
  }

  return (
    <div className="flex h-screen bg-cyber-bg text-cyber-text font-sans overflow-hidden selection:bg-cyber-primary selection:text-black relative pt-10">
      {/* THREAT CLOUD TICKER */}
      <div className="absolute top-0 left-0 right-0 h-8 bg-black/80 border-b border-cyber-primary/20 backdrop-blur z-40 flex items-center overflow-hidden pl-16">
        <div className="flex animate-marquee gap-8 whitespace-nowrap min-w-full pl-4">
          {trends.length > 0 ? trends.map((t, i) => (
            <span key={i} className={`text-xs font-mono font-bold flex items-center gap-1 ${t.is_critical ? 'text-red-500 animate-pulse' : 'text-cyber-primary'}`}>
              {t.direction === 'up' ? '▲' : '▼'} {t.topic}
              <span className="opacity-60 text-[10px]">({t.velocity}%)</span>
            </span>
          )) : <span className="text-xs font-mono text-cyber-text/50">INITIALIZING GLOBAL SENSORS...</span>}
          {/* Repeat for seamless loop */}
          {trends.map((t, i) => (
            <span key={'dup' + i} className={`text-xs font-mono font-bold flex items-center gap-1 ${t.is_critical ? 'text-red-500 animate-pulse' : 'text-cyber-primary'}`}>
              {t.direction === 'up' ? '▲' : '▼'} {t.topic}
              <span className="opacity-60 text-[10px]">({t.velocity}%)</span>
            </span>
          ))}
        </div>
      </div>

      {/* SIDEBAR */}
      <div className="w-16 border-r border-cyber-border flex flex-col items-center py-6 gap-8 bg-cyber-bg/50 backdrop-blur-sm z-20">
        <div className="p-2 bg-cyber-primary/10 rounded-lg border border-cyber-primary/20 text-cyber-primary">
          <Globe size={24} onClick={() => setView('scan')} className="cursor-pointer hover:text-white transition-colors" />
        </div>
        <nav className="flex flex-col gap-6 w-full items-center">
          <NavIcon icon={<LayoutDashboard size={20} />} active={view === 'dashboard'} onClick={() => setView('dashboard')} />
          <NavIcon icon={<Rss size={20} />} active={view === 'feed'} onClick={() => setView('feed')} />
          <NavIcon icon={<Database size={20} />} active={view === 'chat'} onClick={() => setView('chat')} />
          <NavIcon icon={<Share2 size={20} />} active={view === 'graph'} onClick={() => setView('graph')} />
        </nav>
      </div>

      {/* VIEW: DASHBOARD (TREND RADAR) */}
      {view === 'dashboard' && (
        <div className="flex-1 p-10 overflow-y-auto bg-cyber-bg relative">
          <div className="max-w-6xl mx-auto space-y-12">

            {/* Header */}
            <div className="text-center space-y-4">
              <h1 className="text-4xl font-bold text-white tracking-[0.2em] glow-text">GLOBAL PULSE // TREND RADAR</h1>
              <p className="text-cyber-text font-mono text-sm opacity-60">MONITORING {stats.total_sources} ACTIVE SIGNALS ACROSS THE VERSE</p>
            </div>

            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <StatCard icon={<Activity size={24} className="text-blue-400" />} label="SOURCES" value={stats.total_sources} sub="Active Uplinks" color="blue" />

              <StatCard icon={<Database size={24} className="text-purple-400" />} label="DATA POINTS" value={stats.total_intel} sub="Processed Units" color="purple" />

              {/* --- TREND RADAR --- */}
              <StatCard
                icon={<TrendingUp size={24} className="text-amber-400" />}
                label="DOMINANT TREND"
                value={stats.top_trend}
                sub="Highest Volume"
                color="amber"
              />

              <StatCard icon={<Cpu size={24} className="text-green-400" />} label="AI ENGINE" value="ONLINE" sub="Gemini 1.5 Flash" color="green" />
            </div>

            {/* Recent Alerts List */}
            <div className="bg-cyber-panel/30 border border-cyber-border rounded-2xl p-8 backdrop-blur-sm">
              <h3 className="text-cyber-primary font-mono text-xs uppercase mb-6 flex items-center gap-2">
                <Shield size={16} /> Latest Intercepts
              </h3>
              <div className="space-y-4">
                {stats.recent_alerts.length > 0 ? stats.recent_alerts.map((alert, i) => (
                  <div key={i} className="flex justify-between items-center p-4 bg-cyber-bg/40 rounded-xl border border-white/5 hover:border-cyber-primary/30 transition-all">
                    <span className="text-white font-medium text-sm truncate max-w-[70%]">{alert.title}</span>
                    <span className="text-[10px] font-mono text-cyber-text/50">{alert.time.substring(0, 16)}</span>
                  </div>
                )) : <div className="text-center text-cyber-text/40 py-10">NO SIGNAL HISTORY</div>}
              </div>
            </div>

          </div>
        </div>
      )}

      {/* VIEW: DEEP SCAN */}
      {view === 'scan' && (
        <div className="flex-1 flex flex-col items-center justify-center bg-cyber-bg/40 relative overflow-hidden">
          {/* Decorative Background Elements */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] border border-cyber-primary/5 rounded-full animate-spin-slow pointer-events-none"></div>
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] border border-cyber-primary/10 rounded-full animate-spin-slow-reverse pointer-events-none"></div>

          <div className="w-full max-w-2xl z-10 p-8">
            <div className="text-center mb-12">
              <Globe size={48} className="mx-auto text-cyber-primary mb-4 animate-pulse" />
              <h1 className="text-3xl font-bold text-white tracking-[0.2em] glow-text">DEEP SCAN // TARGET RECON</h1>
              <p className="text-cyber-text font-mono text-xs mt-2 opacity-70">INTERNET PROTOCOL INJECTION MODULE ACTIVE</p>
            </div>

            {!scanResult ? (
              <div className="space-y-6">
                <div className="relative group">
                  <input
                    value={scanUrl}
                    onChange={(e) => setScanUrl(e.target.value)}
                    placeholder="ENTER TARGET URL..."
                    className="w-full bg-cyber-panel/80 border border-cyber-border p-6 text-center text-xl font-mono text-white rounded-xl focus:border-cyber-primary outline-none transition-all shadow-[0_0_20px_rgba(0,0,0,0.5)] group-hover:shadow-[0_0_30px_rgba(6,182,212,0.1)]"
                  />
                  <div className="absolute right-4 top-1/2 -translate-y-1/2 text-cyber-primary/50 text-xs font-mono hidden md:block">
                    HTTP/S
                  </div>
                </div>

                <div className="flex justify-center">
                  <button
                    onClick={handleDeepScan}
                    disabled={scanning || !scanUrl}
                    className={`px-12 py-4 bg-cyber-primary text-black font-bold font-mono text-lg rounded-xl transition-all hover:scale-105 hover:shadow-[0_0_20px_#06b6d4] disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-3 ${scanning ? 'animate-pulse' : ''}`}
                  >
                    {scanning ? <><Loader className="animate-spin" /> SCANNING TARGET...</> : <><Search /> INITIATE SCAN</>}
                  </button>
                </div>
              </div>
            ) : (
              <div className="animate-in fade-in zoom-in duration-500">
                <div className="bg-cyber-panel/90 border border-cyber-border rounded-2xl p-8 shadow-2xl backdrop-blur-xl">
                  <div className="flex justify-between items-start mb-6 border-b border-cyber-border pb-6">
                    <div>
                      <span className="text-[10px] font-mono text-cyber-primary border border-cyber-primary/30 px-2 py-1 rounded">SCAN COMPLETE</span>
                      <h2 className="text-xl font-bold text-white mt-3 line-clamp-1">{scanResult.title}</h2>
                      <p className="text-xs text-cyber-text/60 font-mono mt-1">{scanResult.link}</p>
                    </div>
                    <div className="flex gap-2">
                      <button onClick={() => setScanResult(null)} className="p-2 hover:bg-white/10 rounded transition-colors text-xs text-cyber-text">RESET</button>
                    </div>
                  </div>

                  <div className="space-y-6">
                    {/* THREAT METER FOR SCAN */}
                    <div className="bg-cyber-panel/80 border border-cyber-border rounded-xl p-4 flex items-center gap-4">
                      <div className="text-xs font-mono text-cyber-textLight uppercase w-24">Threat Lvl</div>
                      <div className="flex-1 h-2 bg-cyber-bg rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-1000 ${scanResult.score >= 90 ? 'bg-red-600 shadow-[0_0_15px_#dc2626]' : scanResult.score >= 70 ? 'bg-orange-500 shadow-[0_0_10px_#f97316]' : 'bg-blue-500 shadow-[0_0_10px_#3b82f6]'}`}
                          style={{ width: `${scanResult.score || 50}%` }}
                        ></div>
                      </div>
                      <span className={`font-mono font-bold ${scanResult.score >= 90 ? 'text-red-500' : scanResult.score >= 70 ? 'text-orange-500' : 'text-blue-500'}`}>{scanResult.score || 50}/100</span>
                    </div>

                    <div className="bg-cyber-bg/50 p-6 rounded-xl border border-cyber-border">
                      <h3 className="text-xs font-mono text-cyber-text/50 uppercase mb-3 flex items-center gap-2"><Sparkles size={12} /> INTELLIGENCE REPORT</h3>
                      <p className="text-sm text-cyber-textLight leading-relaxed">{scanResult.summary}</p>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="bg-cyber-panel p-4 rounded-xl border border-cyber-border relative">
                        <div className="absolute top-2 right-2 flex gap-1">
                          <button onClick={handleSendToHQ} className="text-cyber-text hover:text-green-400 p-1 opacity-50 hover:opacity-100 transition-all" title="Export to HQ"><HardDrive size={12} /></button>
                        </div>
                        <h3 className="text-cyber-accent text-xs font-mono uppercase mb-2">Tactical Insight</h3>
                        <p className="text-white text-xs">{scanResult.aiInsight}</p>
                      </div>
                      <div className="bg-cyber-panel p-4 rounded-xl border border-cyber-border">
                        <h3 className="text-cyber-primary text-xs font-mono uppercase mb-2">Detected Concepts</h3>
                        <div className="flex flex-wrap gap-2">
                          {scanResult.tags?.map(t => (
                            <span key={t} className="px-2 py-1 bg-cyber-bg text-[10px] border rounded" style={{ borderColor: (TAG_COLORS[t] || TAG_COLORS.DEFAULT) + '40' }}>{t}</span>
                          ))}
                        </div>
                      </div>
                    </div>

                    <button onClick={handleSaveScan} className="w-full py-4 bg-cyber-primary text-black font-bold rounded-xl hover:shadow-[0_0_20px_#06b6d4] transition-all flex items-center justify-center gap-2">
                      <Save size={18} /> ENCRYPT & SAVE TO NEURAL NET
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* VIEW: FEED (Visual Intelligence v4.5) */}
      {view === 'feed' && (
        <div className="flex-1 flex flex-row overflow-hidden relative">

          {/* PANE 1: NEURAL TREE (Sidebar) */}
          <div className="w-64 border-r border-cyber-border bg-[#020617]/50 backdrop-blur-sm flex flex-col hidden md:flex">
            <div className="p-4 border-b border-cyber-border/50">
              <span className="text-[10px] font-mono text-cyber-text/50 uppercase tracking-widest">Neural Navigation</span>
            </div>
            <div className="flex-1 overflow-y-auto custom-scrollbar">
              <SidebarTree
                categories={categories}
                activeCategory={activeTab}
                onSelect={(cat) => setActiveTab(cat)}
              />
            </div>
            <div className="p-4 border-t border-cyber-border/50 text-[10px] text-cyber-text/30 font-mono text-center">
              NOMAD OS v4.5
            </div>
          </div>

          {/* PANE 2: SIGNAL GRID (Middle) */}
          <div className="flex-1 flex flex-col min-w-0 bg-[#020617]">
            {/* HEADER: TITLE + ADD FEED */}
            <div className="h-16 px-6 border-b border-cyber-border/50 flex items-center justify-between bg-cyber-bg/80 backdrop-blur z-20">
              <div className="flex items-center gap-3">
                <Activity size={16} className="text-cyber-primary" />
                <span className="text-xs font-bold text-white tracking-[0.2em]">SIGNAL GRID</span>
                <span className="px-2 py-0.5 rounded bg-white/5 text-[10px] font-mono text-gray-500">{articles.length} UNITS</span>
              </div>
              <button
                onClick={() => setShowModal(true)}
                className="p-2 rounded bg-cyber-primary/10 border border-cyber-primary/20 text-cyber-primary hover:bg-cyber-primary hover:text-black transition-all"
                title="Add New Neural Link (RSS)"
              >
                <Plus size={16} />
              </button>
            </div>

            {/* Mobile Header for Categories */}
            <div className="md:hidden p-2 overflow-x-auto border-b border-cyber-border bg-cyber-panel">
              <div className="flex gap-2">
                {categories.map(c => (
                  <button key={c} onClick={() => setActiveTab(c)} className={`px-2 py-1 text-xs rounded ${activeTab === c ? 'bg-cyber-primary text-black' : 'bg-cyber-bg text-cyber-text'}`}>{c}</button>
                ))}
              </div>
            </div>

            <div className="flex-1 relative">
              <SignalGrid
                articles={articles}
                loading={loadingFeeds}
                onArticleClick={(item) => handleArticleClick(item)}
              />
            </div>
          </div>

          {/* PANE 3: OPERATION DECK (Right - Overlay or Col) */}
          {selectedArticle && (
            <div className={`absolute inset-y-0 right-0 w-full md:w-[600px] lg:w-[700px] z-50 transition-transform duration-300 ${selectedArticle ? 'translate-x-0' : 'translate-x-full'}`}>
              <OperationDeck
                article={selectedArticle}
                analysis={analysis}
                analyzing={analyzing}
                onClose={() => setSelectedArticle(null)}
                onSaveMemory={handleSaveToMemory}
                onArchive={handleSendToHQ}
              />
            </div>
          )}

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
      {/* --- GELİŞMİŞ FEED YÖNETİCİSİ --- */}
      {showModal && (
        <FeedManagerModal
          onClose={() => setShowModal(false)}
          API_URL={API_URL}
          categories={categories}
          onUpdate={() => {
            fetchCategories();
            fetchNews();
          }}
        />
      )}

    </div>
  );
};

// --- SUB-COMPONENTS (Refactored for Cleanliness) ---

const FeedManagerModal = ({ onClose, API_URL, categories, onUpdate }) => {
  const [activeTab, setActiveTab] = useState('add'); // 'add' | 'list'
  const [newFeed, setNewFeed] = useState({ url: '', category: '', name: '' });
  const [existingFeeds, setExistingFeeds] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (activeTab === 'list') {
      fetchFeeds();
    }
  }, [activeTab]);

  const fetchFeeds = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/sources`);
      const data = await res.json();
      setExistingFeeds(data);
    } catch (e) {
      console.error("Feed Fetch Err", e);
    } finally {
      setLoading(false);
    }
  };

  const handleAddFeed = async () => {
    if (!newFeed.url || !newFeed.category) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/feeds/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          url: newFeed.url,
          category: newFeed.category,
          source_name: newFeed.name || "CUSTOM"
        })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);

      alert(`Uplink Established: ${data.message}`);
      setNewFeed({ url: '', category: '', name: '' });
      onUpdate();
    } catch (e) {
      alert(`FEED ERROR: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteFeed = async (id) => {
    if (!confirm("Are you sure you want to sever this neural link?")) return;
    try {
      const res = await fetch(`${API_URL}/feeds/${id}`, { method: 'DELETE' });
      if (res.ok) {
        setExistingFeeds(prev => prev.filter(f => f.id !== id));
        onUpdate();
      }
    } catch (e) {
      alert("Delete failed.");
    }
  };

  return (
    <div className="fixed inset-0 bg-black/90 backdrop-blur-md z-50 flex items-center justify-center p-4 animate-in fade-in duration-200">
      <div className="bg-[#0f172a] border border-cyan-500/30 rounded-2xl w-full max-w-2xl shadow-[0_0_50px_rgba(6,182,212,0.15)] overflow-hidden flex flex-col h-[600px]">

        {/* Header */}
        <div className="p-6 border-b border-white/10 flex justify-between items-center bg-white/5">
          <h2 className="text-xl font-bold text-white flex items-center gap-3">
            <Rss className="text-cyan-400" />
            <span className="tracking-widest">SIGNAL SOURCE MANAGER</span>
          </h2>
          <button onClick={onClose} className="text-white/50 hover:text-white transition-colors">✕</button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-white/10">
          <button
            onClick={() => setActiveTab('add')}
            className={`flex-1 py-3 text-xs font-mono font-bold tracking-wider transition-colors ${activeTab === 'add' ? 'bg-cyan-500/10 text-cyan-400 border-b-2 border-cyan-400' : 'text-white/40 hover:text-white hover:bg-white/5'}`}
          >
            NEW UPLINK
          </button>
          <button
            onClick={() => setActiveTab('list')}
            className={`flex-1 py-3 text-xs font-mono font-bold tracking-wider transition-colors ${activeTab === 'list' ? 'bg-cyan-500/10 text-cyan-400 border-b-2 border-cyan-400' : 'text-white/40 hover:text-white hover:bg-white/5'}`}
          >
            ACTIVE SIGNALS ({existingFeeds.length})
          </button>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-hidden relative">
          {/* VIEW: ADD NEW */}
          {activeTab === 'add' && (
            <div className="flex h-full">
              {/* Presets Sidebar */}
              <div className="w-1/3 border-r border-white/10 overflow-y-auto bg-black/20 p-4">
                <h3 className="text-xs font-mono text-cyan-500 mb-4 uppercase">Presets</h3>
                <div className="space-y-2">
                  {PRESET_FEEDS.map((feed, idx) => (
                    <button
                      key={idx}
                      onClick={() => setNewFeed({ url: feed.url, category: feed.category, name: feed.name })}
                      className="w-full text-left p-3 rounded-lg border border-white/5 hover:border-cyan-500/50 hover:bg-cyan-500/10 transition-all group"
                    >
                      <div className="text-sm text-white font-medium group-hover:text-cyan-400">{feed.name}</div>
                      <div className="text-[10px] text-white/40 mt-1">{feed.category}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Form */}
              <div className="flex-1 p-8 overflow-y-auto">
                <div className="space-y-6">
                  <div>
                    <label className="text-xs font-mono text-cyan-500/70 block mb-2 uppercase">RSS URL</label>
                    <div className="relative">
                      <Globe className="absolute left-3 top-3 text-white/30" size={16} />
                      <input
                        value={newFeed.url}
                        onChange={e => setNewFeed({ ...newFeed, url: e.target.value })}
                        className="w-full bg-white/5 border border-white/10 rounded-lg p-3 pl-10 text-white text-sm focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500"
                        placeholder="https://example.com/feed.xml"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="text-xs font-mono text-cyan-500/70 block mb-2 uppercase">Name</label>
                      <input value={newFeed.name} onChange={e => setNewFeed({ ...newFeed, name: e.target.value })} className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white text-sm focus:border-cyan-500 outline-none" />
                    </div>
                    <div>
                      <label className="text-xs font-mono text-cyan-500/70 block mb-2 uppercase">Category</label>
                      <input value={newFeed.category} onChange={e => setNewFeed({ ...newFeed, category: e.target.value.toUpperCase() })} className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-white text-sm focus:border-cyan-500 outline-none uppercase" list="cat-suggestions" />
                      <datalist id="cat-suggestions">
                        {categories.map(c => c !== 'ALL' && <option key={c} value={c} />)}
                      </datalist>
                    </div>
                  </div>

                  <div className="flex justify-end pt-4">
                    <button
                      onClick={handleAddFeed}
                      disabled={!newFeed.url || !newFeed.name || loading}
                      className="px-8 py-3 bg-cyan-500 hover:bg-cyan-400 text-black font-bold rounded-lg text-xs tracking-wider transition-all disabled:opacity-50 flex items-center gap-2"
                    >
                      {loading ? <Loader className="animate-spin" size={14} /> : <><ChevronRight size={14} /> ESTABLISH LINK</>}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* VIEW: LIST (Manage) */}
          {activeTab === 'list' && (
            <div className="p-0 h-full overflow-hidden flex flex-col">
              <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
                {loading && existingFeeds.length === 0 ? (
                  <div className="flex justify-center items-center h-40 text-cyan-500"><Loader className="animate-spin" /></div>
                ) : (
                  <table className="w-full text-left text-sm border-collapse">
                    <thead className="text-xs font-mono text-white/40 uppercase bg-white/5 sticky top-0">
                      <tr>
                        <th className="p-3">Source Name</th>
                        <th className="p-3">Category</th>
                        <th className="p-3">URL</th>
                        <th className="p-3 text-right">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/10">
                      {existingFeeds.map(feed => (
                        <tr key={feed.id} className="hover:bg-white/5 transition-colors group">
                          <td className="p-3 font-medium text-white">{feed.source_name}</td>
                          <td className="p-3 text-cyan-400">{feed.category}</td>
                          <td className="p-3 text-white/40 truncate max-w-[200px]">{feed.url}</td>
                          <td className="p-3 text-right">
                            <button
                              onClick={() => handleDeleteFeed(feed.id)}
                              className="px-3 py-1 bg-red-500/10 text-red-400 border border-red-500/30 rounded hover:bg-red-500 hover:text-black transition-all text-xs opacity-60 group-hover:opacity-100"
                            >
                              DISCONNECT
                            </button>
                          </td>
                        </tr>
                      ))}
                      {existingFeeds.length === 0 && !loading && (
                        <tr><td colSpan="4" className="p-8 text-center text-white/30 font-mono">NO ACTIVE UPLINKS FOUND</td></tr>
                      )}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
};

const NavIcon = ({ icon, active, onClick }) => (
  <button onClick={onClick} className={`p-3 rounded-xl transition-all ${active ? 'bg-cyber-primary text-black shadow-[0_0_15px_#06b6d4]' : 'text-cyber-text hover:text-white hover:bg-cyber-panel'}`}>
    {icon}
  </button>
);

// --- ERROR BOUNDARY ---
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) { return { hasError: true, error }; }
  componentDidCatch(error, errorInfo) { console.error("Uncaught error:", error, errorInfo); }
  render() {
    if (this.state.hasError) {
      return (
        <div className="h-screen flex items-center justify-center bg-black text-red-500 font-mono p-10 text-center">
          <h1 className="text-4xl mb-4">CRITICAL SYSTEM FAILURE</h1>
          <p>{this.state.error.toString()}</p>
          <button onClick={() => window.location.reload()} className="mt-8 border border-red-500 px-4 py-2 hover:bg-red-500 hover:text-black transition">SYSTEM REBOOT</button>
        </div>
      );
    }
    return this.props.children;
  }
}

export default function WrappedApp() {
  return (
    <ErrorBoundary>
      <App />
    </ErrorBoundary>
  );
}
