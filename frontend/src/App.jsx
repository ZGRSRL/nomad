import React, { useState, useEffect } from 'react';
import { Radio, Rss, Globe, Zap, Database, Shield, Activity, Sparkles, Cpu, ChevronRight, Loader } from 'lucide-react';

const App = () => {
  // State Yönetimi
  const [articles, setArticles] = useState([]);
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [activeTab, setActiveTab] = useState('ALL');

  // Yükleme Durumları
  const [loadingFeeds, setLoadingFeeds] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);

  // AI Analiz Sonuçları
  const [analysis, setAnalysis] = useState(null);

  // 1. RSS Verilerini Çek (Backend'den)
  useEffect(() => {
    const fetchNews = async () => {
      setLoadingFeeds(true);
      try {
        // Backend URL'i (main.py portu 8000)
        const response = await fetch(`http://localhost:8000/feeds?category=${activeTab}`);
        const data = await response.json();
        setArticles(data);
        if (data.length > 0) {
          setSelectedArticle(data[0]); // İlk haberi seç
          // İlk haber için otomatik analiz başlatmıyoruz, kullanıcı tıklasın
        }
      } catch (error) {
        console.error("RSS Fetch Error:", error);
      } finally {
        setLoadingFeeds(false);
      }
    };

    fetchNews();
  }, [activeTab]); // Kategori değişince tekrar çek

  // 2. Habere Tıklayınca Analiz Et
  const handleArticleClick = async (article) => {
    setSelectedArticle(article);
    setAnalysis(null); // Eski analizi temizle
    setAnalyzing(true); // Yükleniyor animasyonunu başlat

    try {
      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: article.title,
          content: article.summary
        })
      });
      const result = await response.json();
      setAnalysis(result);
    } catch (error) {
      console.error("Analysis Error:", error);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="flex h-screen bg-cyber-bg text-cyber-text font-sans overflow-hidden selection:bg-cyber-primary selection:text-black">

      {/* --- SIDEBAR --- */}
      <div className="w-16 border-r border-cyber-border flex flex-col items-center py-6 gap-8 bg-cyber-bg/50 backdrop-blur-sm z-20">
        <div className="p-2 bg-cyber-primary/10 rounded-lg border border-cyber-primary/20 text-cyber-primary">
          <Globe size={24} />
        </div>
        <nav className="flex flex-col gap-6 w-full items-center">
          <NavIcon icon={<Rss size={20} />} active />
          <NavIcon icon={<Database size={20} />} />
          <NavIcon icon={<Shield size={20} />} />
        </nav>
      </div>

      {/* --- MAIN CONTENT --- */}
      <div className="flex-1 flex flex-col md:flex-row overflow-hidden relative">

        {/* Sol Panel: FEED */}
        <div className="w-full md:w-[450px] flex flex-col border-r border-cyber-border bg-cyber-bg/30 backdrop-blur-md z-10">

          {/* Header */}
          <div className="h-16 border-b border-cyber-border flex items-center justify-between px-6">
            <span className="font-bold text-cyber-textLight tracking-wider text-sm">SIGNAL STREAM // LIVE</span>
            <div className="w-2 h-2 rounded-full bg-cyber-primary animate-pulse"></div>
          </div>

          {/* Filters */}
          <div className="p-4 flex gap-2 overflow-x-auto no-scrollbar">
            {['ALL', 'AI / TECH', 'SCIENCE', 'CYBERSEC'].map(tab => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-1.5 rounded-full text-[10px] font-mono border transition-all whitespace-nowrap
                  ${activeTab === tab
                    ? 'border-cyber-primary bg-cyber-primary/10 text-cyber-primary'
                    : 'border-cyber-border text-cyber-text hover:border-cyber-text'}`}
              >
                {tab}
              </button>
            ))}
          </div>

          {/* News List */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
            {loadingFeeds ? (
              <div className="flex justify-center items-center h-40 text-cyber-primary animate-pulse">
                <Loader className="animate-spin mr-2" /> INITIALIZING FEED...
              </div>
            ) : (
              articles.map((item) => (
                <div
                  key={item.id}
                  onClick={() => handleArticleClick(item)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all group relative
                    ${selectedArticle?.id === item.id
                      ? 'bg-cyber-panel border-cyber-primary/50 shadow-[inset_0_0_20px_rgba(6,182,212,0.05)]'
                      : 'bg-cyber-panel/40 border-cyber-border hover:border-cyber-text/30'}`}
                >
                  <div className="flex justify-between items-start mb-2">
                    <span className="text-[10px] font-mono text-cyber-primary uppercase">{item.source}</span>
                    <span className="text-[10px] font-mono text-cyber-text/60">{item.time}</span>
                  </div>
                  <h3 className={`font-medium text-sm leading-snug ${selectedArticle?.id === item.id ? 'text-white' : 'text-cyber-textLight'}`}>
                    {item.title}
                  </h3>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Sağ Panel: INTELLIGENCE HUB */}
        <div className="flex-1 bg-cyber-bg/40 p-8 overflow-y-auto relative flex flex-col gap-6">

          {selectedArticle ? (
            <div className="max-w-3xl mt-6 animate-in fade-in slide-in-from-bottom-4 duration-500">

              {/* Başlık */}
              <div className="mb-8">
                <span className="px-2 py-1 rounded bg-cyber-primary/10 border border-cyber-primary/20 text-cyber-primary text-[10px] font-mono uppercase">
                  {selectedArticle.category}
                </span>
                <h1 className="text-2xl md:text-3xl font-bold text-white mt-4 mb-4 leading-tight glow-text">
                  {selectedArticle.title}
                </h1>
                <a href={selectedArticle.link} target="_blank" rel="noreferrer" className="text-xs text-cyber-text hover:text-cyber-primary flex items-center gap-1 font-mono">
                  <Globe size={12} /> SOURCE LINK
                </a>
              </div>

              {/* AI ANALIZ ALANI */}
              {analyzing ? (
                <div className="h-64 border border-cyber-border border-dashed rounded-xl flex flex-col items-center justify-center text-cyber-primary/50">
                  <div className="relative">
                    <div className="absolute inset-0 bg-cyber-primary blur-xl opacity-20 animate-pulse"></div>
                    <Cpu size={48} className="animate-bounce relative z-10" />
                  </div>
                  <span className="mt-4 font-mono text-xs animate-pulse">DECRYPTING & ANALYZING...</span>
                </div>
              ) : analysis ? (
                <div className="grid grid-cols-1 gap-6">

                  {/* Summary & Insight */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="bg-cyber-panel/60 border border-cyber-border rounded-xl p-6 relative group hover:border-cyber-primary/30 transition-colors">
                      <h3 className="text-cyber-primary font-mono text-xs uppercase tracking-widest mb-4 flex items-center gap-2">
                        <Sparkles size={14} /> AI Synthesis
                      </h3>
                      <p className="text-cyber-textLight text-sm leading-relaxed">
                        {analysis.summary}
                      </p>
                    </div>

                    <div className="bg-cyber-panel/60 border border-cyber-border rounded-xl p-6 relative group hover:border-cyber-accent/30 transition-colors">
                      <h3 className="text-cyber-accent font-mono text-xs uppercase tracking-widest mb-4 flex items-center gap-2">
                        <Zap size={14} /> Strategic Insight
                      </h3>
                      <p className="text-cyber-textLight text-sm leading-relaxed border-l-2 border-cyber-accent/50 pl-4">
                        {analysis.aiInsight}
                      </p>
                    </div>
                  </div>

                  {/* Action */}
                  <div className="bg-gradient-to-r from-cyber-primary/10 to-transparent border border-cyber-primary/20 rounded-xl p-5 flex items-center gap-4">
                    <div className="bg-cyber-primary/20 p-2 rounded-lg text-cyber-primary">
                      <ChevronRight size={20} />
                    </div>
                    <div>
                      <h4 className="text-cyber-primary text-xs font-mono uppercase mb-1">Recommended Action</h4>
                      <p className="text-white text-sm font-medium">
                        {analysis.action}
                      </p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="p-6 border border-cyber-border rounded-xl text-center text-cyber-text/50 text-sm font-mono">
                            // WAITING FOR ANALYSIS REQUEST...
                  <br />
                            // CLICK ARTICLE TO INITIALIZE AI
                </div>
              )}

            </div>
          ) : (
            <div className="flex h-full items-center justify-center text-cyber-text/30 font-mono text-sm">
              SELECT A SIGNAL TO BEGIN DECRYPTION
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const NavIcon = ({ icon, active }) => (
  <button className={`p-3 rounded-xl transition-all ${active ? 'bg-cyber-primary text-black shadow-[0_0_15px_#06b6d4]' : 'text-cyber-text hover:text-white hover:bg-cyber-panel'}`}>
    {icon}
  </button>
);

export default App;
