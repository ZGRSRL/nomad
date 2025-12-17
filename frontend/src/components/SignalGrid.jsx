import React from 'react';
import NewsCard from './NewsCard';
import { Loader } from 'lucide-react';

const SignalGrid = ({ articles, loading, onArticleClick }) => {
    if (loading) {
        return (
            <div className="h-full flex items-center justify-center">
                <Loader className="animate-spin text-cyber-primary w-8 h-8" />
                <span className="ml-3 font-mono text-cyber-text text-sm">SCANNING FREQUENCIES...</span>
            </div>
        );
    }

    if (!articles || articles.length === 0) {
        return (
            <div className="h-full flex flex-col items-center justify-center text-cyber-text/30">
                <div className="text-4xl mb-4 opacity-20">📡</div>
                <p className="font-mono text-sm tracking-widest">NO SIGNAL DETECTED</p>
            </div>
        );
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-4 p-6 overflow-y-auto h-full scroll-smooth custom-scrollbar pb-20">
            {articles.map((item) => (
                <NewsCard
                    key={item.id || item.link}
                    data={item}
                    onClick={onArticleClick}
                />
            ))}
        </div>
    );
};

export default SignalGrid;
