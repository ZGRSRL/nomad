import React, { useEffect, useState } from 'react';
import Graph from 'react-graph-vis';
import { Loader } from 'lucide-react';

const NeuralGraph = ({ data, onNodeClick, width, height }) => {
    const [graphData, setGraphData] = useState(null);

    useEffect(() => {
        if (data && data.nodes && data.nodes.length > 0) {
            // Transform data for vis-network
            // Backend returns { nodes: [], links: [] }
            const edges = (data.links || []).map(link => {
                const sourceId = typeof link.source === 'object' ? link.source.id : link.source;
                const targetId = typeof link.target === 'object' ? link.target.id : link.target;
                return {
                    from: sourceId,
                    to: targetId,
                    color: { color: '#06b6d4', opacity: 0.2 }
                };
            });

            const nodes = data.nodes.map(node => {
                // Get first tag for color
                const firstTag = node.tags && node.tags.length > 0 ? node.tags[0].toUpperCase() : 'DEFAULT';
                const tagColors = {
                    DEFAULT: '#06b6d4',
                    TECH: '#06b6d4',
                    SCIENCE: '#8b5cf6',
                    SPACE: '#6366f1',
                    AI: '#ec4899',
                    MEDICAL: '#10b981',
                    HISTORY: '#f59e0b',
                };
                
                return {
                    id: node.id,
                    label: node.label || node.name || `Node ${node.id}`,
                    shape: 'dot',
                    size: 15,
                    color: tagColors[firstTag] || tagColors.DEFAULT,
                    font: { color: '#fff', face: 'monospace', size: 12 },
                    title: node.full_content || node.label || node.name // Tooltip
                };
            });

            setGraphData({ nodes, edges });
        } else {
            setGraphData(null);
        }
    }, [data]);

    const options = {
        layout: {
            hierarchical: false,
            randomSeed: 42
        },
        nodes: {
            borderWidth: 1,
            borderWidthSelected: 2,
            shadow: true,
        },
        edges: {
            width: 1,
            smooth: {
                type: 'continuous'
            },
            arrows: {
                to: { enabled: false }
            }
        },
        physics: {
            enabled: true,
            barnesHut: {
                gravitationalConstant: -2000,
                centralGravity: 0.3,
                springLength: 95,
                springConstant: 0.04,
                damping: 0.09,
                avoidOverlap: 0
            },
            stabilization: {
                enabled: true,
                iterations: 1000,
                updateInterval: 100,
                onlyDynamicEdges: false,
                fit: true
            }
        },
        interaction: {
            hover: true,
            tooltipDelay: 200,
            zoomView: true,
            dragView: true
        },
        height: `${height}px`
    };

    const events = {
        select: function (event) {
            const { nodes } = event;
            if (nodes.length > 0 && onNodeClick) {
                // Find the full node object
                const nodeId = nodes[0];
                const originalNode = data.nodes.find(n => n.id === nodeId);
                if (originalNode) {
                    onNodeClick(originalNode);
                }
            }
        }
    };

    if (!graphData) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-cyber-primary">
                <Loader className="animate-spin mb-4" size={32} />
                <span className="font-mono text-sm tracking-widest animate-pulse">BUILDING NEURAL LATTICE...</span>
            </div>
        );
    }

    return (
        <div className="w-full h-full bg-[#020617] relative">
            {/* Background Grid Effect */}
            <div className="absolute inset-0 bg-[linear-gradient(rgba(6,182,212,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(6,182,212,0.05)_1px,transparent_1px)] bg-[size:20px_20px] pointer-events-none"></div>

            <Graph
                graph={graphData}
                options={options}
                events={events}
            />
        </div>
    );
};

export default NeuralGraph;
