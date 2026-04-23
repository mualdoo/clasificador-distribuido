import React from 'react';

export default function NodesIndicator() {
  const nodes = [
    { id: 1, label: 'Nodo 1: Activo' },
    { id: 2, label: 'Nodo 2: Activo' },
    { id: 3, label: 'Nodo 3: Activo' },
  ];

  return (
    <footer
      className="flex items-center gap-5 px-5 py-2.5"
      style={{ background: '#0d0d0f', borderTop: '1px solid #1a1a1e' }}
    >
      <span className="text-xs font-medium" style={{ color: '#444' }}>
        Estado del Clúster:
      </span>
      {nodes.map(node => (
        <div key={node.id} className="flex items-center gap-1.5">
          <span
            className="w-2 h-2 rounded-full"
            style={{
              background: '#22c55e',
              boxShadow: '0 0 6px rgba(34,197,94,0.6)',
            }}
          />
          <span className="text-xs" style={{ color: '#666' }}>{node.label}</span>
        </div>
      ))}
    </footer>
  );
}
