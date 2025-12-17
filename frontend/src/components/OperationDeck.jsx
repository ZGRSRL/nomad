import React from 'react';
import { ExternalLink, Zap, Save, HardDrive, Shield, Filter, Copy, Maximize2, X } from 'lucide-react';

const OperationDeck = ({ article, analysis, analyzing, onClose, onSaveMemory, onArchive }) => {
    if (!article) return null;

    return (
        <div className="h-full flex flex-col bg-cyber-bg border-l border-cyber-border/50 relative shadow-[-20px_0_50px_rgba(0,0,0,0.5)]">
            {/* 1. HEADER: WIDE COVER IMAGE */}
            <div className="relative h-64 w-full shrink-0 group">
                {article.image_url ? (
                    <img src={article.image_url} className="w-full h-full object-cover opacity-60 group-hover:opacity-80 transition-opacity" />
                ) : (
                    <div className="w-full h-full bg-gradient-to-b from-gray-900 to-black pattern-grid-lg opacity-50"></div>
                )}

                {/* Overlay Gradient */}
                <div className="absolute inset-0 bg-gradient-to-t from-cyber-bg via-cyber-bg/50 to-transparent"></div>

                {/* Top Controls */}
                <div className="absolute top-4 right-4 flex gap-2">
                    <button onClick={onClose} className="p-2 bg-black/50 hover:bg-red-500/20 text-white rounded-full backdrop-blur border border-white/10 transition-all">
                        <X size={18} />
                    </button>
                </div>

                {/* Title Area (Overlapping Image) */}
                <div className="absolute bottom-6 left-6 right-6">
                    <div className="flex items-center gap-3 mb-2">
                        <span className="bg-cyber-primary/20 text-cyber-primary border border-cyber-primary/50 text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider backdrop-blur-md">
                            {article.category}
                        </span>
                        <span className="text-gray-400 text-xs font-mono">{article.time}</span>
                    </div>
                    <h1 className="text-2xl md:text-3xl font-bold text-white leading-tight glow-text font-display drop-shadow-lg">
                        {article.title}
                    </h1>
                </div>
            </div>

            {/* 2. ACTION BAR */}
            <div className="px-6 py-4 flex justify-between items-center border-b border-cyber-border/50 bg-cyber-bg/95 backdrop-blur z-10">
                <div className="flex gap-3">
                    <a href={article.link} target="_blank" className="flex items-center gap-2 px-4 py-2 bg-cyber-panel border border-cyber-border rounded hover:border-cyber-primary hover:text-white text-cyber-text text-xs font-bold tracking-wider transition-all">
                        <ExternalLink size={14} /> SOURCE
                    </a>
                    <button onClick={onArchive} className="flex items-center gap-2 px-4 py-2 bg-cyber-panel border border-cyber-border rounded hover:border-green-500 hover:text-green-400 text-cyber-text text-xs font-bold tracking-wider transition-all">
                        <HardDrive size={14} /> ARCHIVE
                    </button>
                </div>
                <button onClick={onSaveMemory} className="flex items-center gap-2 px-5 py-2 bg-cyber-primary text-black rounded font-bold hover:shadow-[0_0_20px_#06b6d4] hover:bg-cyan-300 transition-all text-xs tracking-wider">
                    <Save size={14} /> MEMORY
                </button>
            </div>

            {/* 3. SCROLLABLE CONTENT AREA */}
            <div className="flex-1 overflow-y-auto custom-scrollbar p-0">

                {/* A. AI ANALYSIS SECTION */}
                <div className="p-6 md:p-8 space-y-6">

                    {analyzing ? (
                        <div className="p-10 border border-cyber-primary/30 border-dashed rounded-xl bg-cyber-primary/5 flex flex-col items-center justify-center animate-pulse">
                            <Zap className="text-cyber-primary mb-3" size={24} />
                            <span className="font-mono text-cyber-primary text-xs tracking-widest">DECRYPTING INTELLIGENCE...</span>
                        </div>
                    ) : analysis ? (
                        <div className="grid grid-cols-1 gap-6 animate-in slide-in-from-bottom-4 duration-500">
                            {/* Impact Hook */}
                            {analysis.one_line_hook && (
                                <div className="p-4 border-l-4 border-cyber-primary bg-gradient-to-r from-cyber-primary/10 to-transparent">
                                    <p className="text-cyber-primary font-medium italic text-sm">"{analysis.one_line_hook}"</p>
                                </div>
                            )}

                            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                {/* Summary Block */}
                                <div className="bg-cyber-panel/40 p-5 rounded-xl border border-cyber-border hover:border-cyber-primary/30 transition-colors">
                                    <div className="flex items-center gap-2 mb-3 text-cyber-textLight text-[10px] font-bold uppercase tracking-wider">
                                        <Filter size={12} /> Exec Summary
                                    </div>
                                    <p className="text-sm text-gray-300 leading-relaxed font-light">{analysis.summary}</p>
                                </div>

                                {/* Insight Block */}
                                <div className="bg-cyber-panel/40 p-5 rounded-xl border border-cyber-border hover:border-cyber-primary/30 transition-colors">
                                    <div className="flex items-center gap-2 mb-3 text-cyber-textLight text-[10px] font-bold uppercase tracking-wider">
                                        <Zap size={12} /> Strategic Insight
                                    </div>
                                    <p className="text-sm text-gray-300 leading-relaxed font-light">{analysis.aiInsight}</p>
                                </div>
                            </div>

                            {/* Protocol / Tags */}
                            <div className="flex flex-wrap gap-2 mt-2">
                                {analysis.tags?.map(tag => (
                                    <span key={tag} className="px-3 py-1 bg-black border border-gray-800 text-gray-400 text-xs font-mono rounded-full hover:border-cyber-primary hover:text-cyber-primary transition-colors cursor-default">
                                        #{tag}
                                    </span>
                                ))}
                            </div>
                        </div>
                    ) : (
                        <div className="text-center py-10 opacity-50 font-mono text-xs">Analysis Pending...</div>
                    )}

                </div>

                {/* Divider */}
                <div className="h-px bg-cyber-border/50 mx-8"></div>

                {/* B. ORIGINAL CONTENT PREVIEW */}
                <div className="p-6 md:p-8 opacity-70 hover:opacity-100 transition-opacity">
                    <h3 className="text-xs font-bold text-gray-500 uppercase tracking-widest mb-4">Original Signal Data</h3>
                    <div className="prose prose-invert prose-sm max-w-none text-gray-400 font-serif leading-7">
                        {article.summary}
                    </div>
                </div>

            </div>
        </div>
    );
};

export default OperationDeck;
