import React, { useEffect, useRef, useState } from 'react';
import './InteractiveMindMap.css';

const InteractiveMindMap = ({ mindmapData, onNodeClick }) => {
  const svgRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredNodes, setFilteredNodes] = useState([]);

  useEffect(() => {
    if (mindmapData && mindmapData.nodes) {
      setFilteredNodes(mindmapData.nodes);
    }
  }, [mindmapData]);

  useEffect(() => {
    if (searchTerm) {
      const filtered = mindmapData?.nodes?.filter(node =>
        node.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
        node.description?.toLowerCase().includes(searchTerm.toLowerCase())
      ) || [];
      setFilteredNodes(filtered);
    } else {
      setFilteredNodes(mindmapData?.nodes || []);
    }
  }, [searchTerm, mindmapData]);

  const handleNodeClick = (node) => {
    setSelectedNode(node);
    if (onNodeClick) {
      onNodeClick(node);
    }
  };

  const handleZoomIn = () => {
    setZoom(prev => Math.min(prev * 1.2, 3));
  };

  const handleZoomOut = () => {
    setZoom(prev => Math.max(prev / 1.2, 0.3));
  };

  const resetView = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
    setSelectedNode(null);
  };

  const getNodeColor = (nodeType) => {
    const colors = {
      central: '#FF6B6B',
      main: '#4ECDC4',
      sub: '#45B7D1',
      author: '#82E0AA',
      concept: '#96CEB4',
      connection: '#FFEAA7'
    };
    return colors[nodeType] || '#DDA0DD';
  };

  const getConnectionColor = (connectionType) => {
    const colors = {
      main_concept: '#2C3E50',
      subconcept: '#34495E',
      authored: '#27AE60',
      related: '#3498DB',
      cites: '#9B59B6'
    };
    return colors[connectionType] || '#95A5A6';
  };

  if (!mindmapData || !mindmapData.nodes) {
    return (
      <div className="mindmap-placeholder">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Generating Interactive Mind Map...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="interactive-mindmap-container">
      <div className="mindmap-controls">
        <div className="search-controls">
          <input
            type="text"
            placeholder="Search nodes..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="mindmap-search"
          />
          <span className="search-results">{filteredNodes.length} nodes</span>
        </div>
        
        <div className="zoom-controls">
          <button onClick={handleZoomOut} className="control-btn">
            <span>🔍-</span>
          </button>
          <span className="zoom-level">{(zoom * 100).toFixed(0)}%</span>
          <button onClick={handleZoomIn} className="control-btn">
            <span>🔍+</span>
          </button>
          <button onClick={resetView} className="control-btn reset-btn">
            Reset View
          </button>
        </div>
      </div>

      <div className="mindmap-wrapper">
        <svg
          ref={svgRef}
          className="mindmap-svg"
          viewBox={`${-pan.x} ${-pan.y} ${800 / zoom} ${600 / zoom}`}
          width="100%"
          height="500"
        >
          {/* Render connections */}
          {mindmapData.connections?.map((connection, index) => {
            const fromNode = mindmapData.nodes.find(n => n.id === connection.from_id || n.id === connection.from);
            const toNode = mindmapData.nodes.find(n => n.id === connection.to_id || n.id === connection.to);
            
            if (!fromNode || !toNode) return null;

            const isVisible = filteredNodes.includes(fromNode) && filteredNodes.includes(toNode);
            if (!isVisible && searchTerm) return null;

            return (
              <g key={`connection-${index}`}>
                <line
                  x1={fromNode.x}
                  y1={fromNode.y}
                  x2={toNode.x}
                  y2={toNode.y}
                  stroke={getConnectionColor(connection.type)}
                  strokeWidth={connection.strength ? connection.strength * 2 : 2}
                  strokeDasharray={connection.type === 'authored' ? '5,5' : 'none'}
                  opacity={0.7}
                />
                {connection.label && (
                  <text
                    x={(fromNode.x + toNode.x) / 2}
                    y={(fromNode.y + toNode.y) / 2}
                    textAnchor="middle"
                    fontSize="10"
                    fill="#555"
                    className="connection-label"
                  >
                    {connection.label}
                  </text>
                )}
              </g>
            );
          })}

          {/* Render nodes */}
          {filteredNodes.map((node) => {
            const isSelected = selectedNode && selectedNode.id === node.id;
            const nodeSize = node.size || 20;
            
            return (
              <g
                key={`node-${node.id}`}
                className={`mindmap-node ${node.type} ${isSelected ? 'selected' : ''}`}
                onClick={() => handleNodeClick(node)}
                style={{ cursor: 'pointer' }}
              >
                <circle
                  cx={node.x}
                  cy={node.y}
                  r={nodeSize}
                  fill={node.color || getNodeColor(node.type)}
                  stroke={isSelected ? '#2C3E50' : '#fff'}
                  strokeWidth={isSelected ? 3 : 2}
                  className="node-circle"
                />
                <text
                  x={node.x}
                  y={node.y}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fontSize={Math.max(nodeSize / 3, 8)}
                  fill="#2C3E50"
                  fontWeight={node.type === 'central' ? 'bold' : 'normal'}
                  className="node-label"
                >
                  {node.label.length > 15 ? node.label.substring(0, 15) + '...' : node.label}
                </text>
                
                {/* Connection count indicator */}
                {node.connections_count && (
                  <circle
                    cx={node.x + nodeSize - 5}
                    cy={node.y - nodeSize + 5}
                    r="8"
                    fill="#E74C3C"
                    className="connection-count"
                  />
                )}
                {node.connections_count && (
                  <text
                    x={node.x + nodeSize - 5}
                    y={node.y - nodeSize + 5}
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fontSize="10"
                    fill="white"
                    fontWeight="bold"
                  >
                    {node.connections_count}
                  </text>
                )}
              </g>
            );
          })}
        </svg>
      </div>

      {/* Node Details Panel */}
      {selectedNode && (
        <div className="node-details-panel">
          <div className="panel-header">
            <h3>{selectedNode.label}</h3>
            <button 
              onClick={() => setSelectedNode(null)}
              className="close-panel"
            >
              ×
            </button>
          </div>
          <div className="panel-content">
            <div className="node-info">
              <span className="node-type-badge">{selectedNode.type}</span>
              {selectedNode.description && (
                <p className="node-description">{selectedNode.description}</p>
              )}
              {selectedNode.references && selectedNode.references.length > 0 && (
                <div className="node-references">
                  <h4>References:</h4>
                  <ul>
                    {selectedNode.references.map((ref, index) => (
                      <li key={index}>{ref}</li>
                    ))}
                  </ul>
                </div>
              )}
              {selectedNode.connections_count && (
                <div className="connections-info">
                  <strong>Connections:</strong> {selectedNode.connections_count}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="mindmap-legend">
        <h4>Node Types</h4>
        <div className="legend-items">
          <div className="legend-item">
            <div className="legend-color central"></div>
            <span>Central Topic</span>
          </div>
          <div className="legend-item">
            <div className="legend-color main"></div>
            <span>Main Concepts</span>
          </div>
          <div className="legend-item">
            <div className="legend-color sub"></div>
            <span>Sub-concepts</span>
          </div>
          <div className="legend-item">
            <div className="legend-color author"></div>
            <span>Authors</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InteractiveMindMap;
