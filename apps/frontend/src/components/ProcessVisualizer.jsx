import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import useWebSocket from '../hooks/useWebSocket.js';
import AnnotationLayer from './AnnotationLayer.jsx';

// Simple PDL example data structure
const samplePDL = {
  nodes: [
    { id: 'start', label: 'Start' },
    { id: 'task1', label: 'Task 1' },
    { id: 'task2', label: 'Task 2' },
    { id: 'end', label: 'End' }
  ],
  edges: [
    { source: 'start', target: 'task1' },
    { source: 'task1', target: 'task2' },
    { source: 'task2', target: 'end' }
  ]
};

export default function ProcessVisualizer() {
  const svgRef = useRef(null);
  const [data, setData] = useState(samplePDL);
  const [annotations, setAnnotations] = useState([]);

  // Handle real-time updates via WebSocket (status changes, etc.)
  useWebSocket('ws://localhost:8000/ws/process', (msg) => {
    if (msg.type === 'annotation') {
      setAnnotations((prev) => [...prev, msg.payload]);
    }
    if (msg.type === 'update') {
      setData(msg.payload);
    }
  });

  // Render the flowchart using D3
  useEffect(() => {
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    const width = svgRef.current.clientWidth;
    const height = svgRef.current.clientHeight;

    const simulation = d3
      .forceSimulation(data.nodes)
      .force('link', d3.forceLink(data.edges).id((d) => d.id).distance(120))
      .force('charge', d3.forceManyBody().strength(-400))
      .force('center', d3.forceCenter(width / 2, height / 2));

    const link = svg
      .append('g')
      .attr('stroke', '#555')
      .selectAll('line')
      .data(data.edges)
      .join('line');

    const node = svg
      .append('g')
      .selectAll('circle')
      .data(data.nodes)
      .join('circle')
      .attr('r', 20)
      .attr('fill', '#10a37f')
      .call(
        d3
          .drag()
          .on('start', (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on('drag', (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on('end', (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          })
      );

    const labels = svg
      .append('g')
      .selectAll('text')
      .data(data.nodes)
      .join('text')
      .text((d) => d.label)
      .attr('text-anchor', 'middle')
      .attr('dy', 4)
      .style('pointer-events', 'none')
      .style('fill', '#fff');

    simulation.on('tick', () => {
      link
        .attr('x1', (d) => d.source.x)
        .attr('y1', (d) => d.source.y)
        .attr('x2', (d) => d.target.x)
        .attr('y2', (d) => d.target.y);

      node.attr('cx', (d) => d.x).attr('cy', (d) => d.y);
      labels.attr('x', (d) => d.x).attr('y', (d) => d.y);
    });
  }, [data]);

  // Export the current SVG diagram
  const exportSVG = () => {
    const svgData = svgRef.current.outerHTML;
    const blob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'process.svg';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{ flex: 1, position: 'relative' }}>
      <svg ref={svgRef} style={{ background: '#212121' }}></svg>
      <AnnotationLayer annotations={annotations} />
      <button
        onClick={exportSVG}
        style={{
          position: 'absolute',
          top: 10,
          right: 10,
          background: '#2a2a2a',
          color: '#e0e0e0',
          border: 'none',
          padding: '6px 12px',
          borderRadius: '4px',
          cursor: 'pointer'
        }}
      >
        Export SVG
      </button>
    </div>
  );
}
