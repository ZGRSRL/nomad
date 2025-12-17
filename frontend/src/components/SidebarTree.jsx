import React, { useState } from 'react';
import { ChevronRight, ChevronDown, Folder, Hash, Cpu, Globe, Shield, Terminal } from 'lucide-react';

// Hardcoded hierarchy map for the "Visual Intelligence" feel
// We will try to map dynamic categories into these folders if possible,
// or just display them under a catch-all if they don't match.
const TREE_STRUCTURE = [
    {
        id: 'global_intel',
        label: 'GLOBAL INTEL',
        icon: Globe,
        children: ['NEWS', 'SCIENCE', 'HISTORY', 'Civilization']
    },
    {
        id: 'tech_ai',
        label: 'TECH & AI',
        icon: Cpu,
        children: ['AI', 'TECH', 'DEV', 'LLM Agents']
    },
    {
        id: 'cyber_ops',
        label: 'CYBER OPS',
        icon: Shield,
        children: ['CYBERSEC', 'CRYPTO', 'Hacking']
    }
];

const SidebarTree = ({ categories, activeCategory, onSelect }) => {
    // State for expanded folders
    const [expanded, setExpanded] = useState({
        global_intel: true,
        tech_ai: true,
        cyber_ops: false
    });

    const toggleExpand = (id) => {
        setExpanded(prev => ({ ...prev, [id]: !prev[id] }));
    };

    // Helper to check if a category is "active" (selected)
    const isActive = (cat) => activeCategory === cat;

    return (
        <div className="w-full flex flex-col gap-2 p-2 font-mono text-sm select-none">
            {/* "ALL" Override */}
            <div
                onClick={() => onSelect('ALL')}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-all border ${activeCategory === 'ALL' ? 'bg-cyber-primary/20 border-cyber-primary text-white shadow-[0_0_10px_rgba(6,182,212,0.3)]' : 'border-transparent text-cyber-text hover:bg-white/5 hover:text-white'}`}
            >
                <Terminal size={16} />
                <span className="tracking-wider font-bold">NET_OVERVIEW</span>
            </div>

            <div className="h-px bg-cyber-border/50 my-2 mx-2" />

            {TREE_STRUCTURE.map((folder) => (
                <div key={folder.id} className="felx flex-col">
                    {/* Folder Header */}
                    <div
                        onClick={() => toggleExpand(folder.id)}
                        className="flex items-center justify-between px-2 py-1.5 text-cyber-text/70 hover:text-white cursor-pointer group"
                    >
                        <div className="flex items-center gap-2">
                            <folder.icon size={14} className="group-hover:text-cyber-primary transition-colors" />
                            <span className="text-xs font-bold tracking-[0.1em]">{folder.label}</span>
                        </div>
                        {expanded[folder.id] ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                    </div>

                    {/* Folder Children */}
                    {expanded[folder.id] && (
                        <div className="flex flex-col ml-2 border-l border-cyber-border/30 pl-2 mt-1 gap-1">
                            {folder.children.map(child => {
                                // Only show if it matches available categories (or we can just show generic ones if we want fixed UI)
                                // For now, let's show all predefined ones + any from 'categories' that match loosely
                                // Ideally we filter 'categories' prop to place them here.

                                // Simple logic: If the child name exactly matches a category we have, render it.
                                // Or if it's a "display name" for a real category.
                                const isRealCategory = categories.includes(child);
                                const displayClass = isActive(child)
                                    ? 'text-cyber-primary bg-cyber-primary/10 border-l-2 border-cyber-primary pl-2'
                                    : 'text-cyber-textLight hover:text-white hover:pl-1';

                                return (
                                    <div
                                        key={child}
                                        onClick={() => onSelect(child)}
                                        className={`text-xs py-1.5 cursor-pointer transition-all flex items-center justify-between pr-2 rounded-r ${displayClass}`}
                                    >
                                        <span>{child}</span>
                                        {/* Mock Count - Real implementation would need counts passed in props */}
                                        {isRealCategory && <span className="text-[9px] opacity-40">12</span>}
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
};

export default SidebarTree;
