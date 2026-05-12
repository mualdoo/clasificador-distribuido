import React, { useEffect, useState } from 'react';
import { getNodes } from '../api';
import { Role } from '../types';


interface Props {
  actualRole: Role;
}


export default function NodesIndicator({ actualRole }: Props) {

  const [nodes, setNodes] = useState<Array<{ id: string; nombre: string; estado: string }>>([]);

  useEffect(() => {

    if (actualRole === 'admin') {
      loadNodes();
      // Actualizar cada 30 segundos
      const interval = setInterval(loadNodes, 30000);
      return () => clearInterval(interval);
    }
    }, [actualRole]);

    const loadNodes = async () => {
    try {
      const data = await getNodes();
      //  Extraemos el arreglo nodos del json
      setNodes(data.nodos || []);
    } catch (error) {
      console.error('Error al cargar nodos:', error);
    }
  };

  //Si no es admin 
  if (actualRole !== 'admin') {
    return (
      <footer
        className="flex items-center gap-5 px-5 py-2.5"
        style={{ background: '#0d0d0f', borderTop: '1px solid #1a1a1e' }}
      >
        <span className="text-xs font-medium" style={{ color: '#444' }}>
          Gestor de archivos UwU - Benemérita Universidad Autónoma de Puebla
        </span>
      </footer>
    );
  }

// Si es admin pero no cargan los nodos
  if (nodes.length === 0) {
    return (
      <footer
        className="flex items-center gap-5 px-5 py-2.5"
        style={{ background: '#0d0d0f', borderTop: '1px solid #1a1a1e' }}
      >
        <span className="text-xs font-medium" style={{ color: '#444' }}>
          Estado del Clúster: Cargando...
        </span>
      </footer>
    );
  }

   // Si es admin y ya cargaron los nodos
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
              background: node.estado === 'activo' ? '#22c55e' : '#ef4444',
              boxShadow: node.estado === 'activo' 
                ? '0 0 6px rgba(34,197,94,0.6)' 
                : '0 0 6px rgba(239,68,68,0.6)',
            }}
          />
          <span className="text-xs" style={{ color: '#666' }}>
            {node.nombre}: {node.estado}
          </span>
        </div>
      ))}
    </footer>
  );

}