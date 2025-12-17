import React from 'react';
import { ExternalLink, Zap, Clock, Share2 } from 'lucide-react';

const NewsCard = ({ data, onClick }) => {
    return (
        <div
            onClick={() => onClick(data)}
            className="group relative bg-gray-900 border border-gray-800 hover:border-neon-blue rounded-lg overflow-hidden transition-all cursor-pointer h-full flex flex-col hover:shadow-[0_0_20px_rgba(6,182,212,0.2)]"
        >
            {/* 1. VISUAL INTEL (Image Area) */}
            <div className="h-40 w-full relative overflow-hidden bg-black">
                {data.image_url ? (
                    <img
                        src={data.image_url}
                        alt={data.title}
                        className="object-cover w-full h-full opacity-80 group-hover:opacity-100 group-hover:scale-105 transition-transform duration-700"
                        onError={(e) => { e.target.style.display = 'none'; }}
                    />
                ) : (
                    // Fallback Cyber Texture
                    <div className="w-full h-full bg-[url('https://www.transparenttextures.com/patterns/dark-matter.png')] opacity-20 group-hover:opacity-40 transition-opacity"></div>
                )}

                {/* Source Badge (Overlay) */}
                <div className="absolute top-2 right-2 bg-black/80 backdrop-blur px-2 py-1 text-[10px] font-mono text-neon-blue border border-neon-blue/30 rounded uppercase tracking-wider shadow-lg">
                    {data.source}
                </div>

                {/* Scanline Effect Overlay */}
                <div className="absolute inset-0 bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] z-10 pointer-events-none bg-[length:100%_4px,3px_100%] opacity-20"></div>
            </div>

            {/* 2. DATA HEADER */}
            <div className="p-4 flex-1 flex flex-col relative">
                {/* Category Tint Line */}
                <div className="absolute top-0 left-0 right-0 h-[1px] bg-gradient-to-r from-transparent via-cyber-primary/50 to-transparent"></div>

                <div className="flex justify-between items-center mb-2">
                    <span className="text-[10px] text-gray-500 font-mono flex items-center gap-1">
                        <Clock size={10} /> {data.time}
                    </span>
                    {/* Impact/Share Signal */}
                    <span className="flex items-center gap-1 text-[10px] font-bold text-orange-400">
                        <Zap size={10} className="fill-orange-400 animate-pulse" />
                        {data.impact_score ? `IMPACT ${data.impact_score}` : 'ACTIVE'}
                    </span>
                </div>

                <h3 className="font-bold text-gray-200 text-sm mb-3 leading-snug line-clamp-2 font-sans group-hover:text-cyber-primary transition-colors">
                    {data.title}
                </h3>

                {/* Summary Snippet */}
                <p className="text-xs text-gray-500 line-clamp-3 mb-4 flex-1">
                    {data.summary.replace(/<[^>]+>/g, '')}
                </p>

                {/* Footer Actions */}
                <div className="flex justify-between items-center pt-3 border-t border-gray-800">
                    <div className="flex gap-2">
                        {/* Mock Tags */}
                        <span className="text-[9px] px-1 py-0.5 border border-gray-700 rounded text-gray-500">#{data.category}</span>
                    </div>
                    <ExternalLink size={12} className="text-gray-600 group-hover:text-white transition-colors" />
                </div>
            </div>
        </div>
    );
};

export default NewsCard;
