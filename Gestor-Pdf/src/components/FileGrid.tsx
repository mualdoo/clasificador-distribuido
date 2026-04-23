import React, { useState } from 'react';
import { FileText, Tag, Download, Trash2 } from 'lucide-react';
import { PDFFile } from '../types';

interface Props {
  files: PDFFile[];
  selectedIds: Set<string>;
  onToggleSelect: (id: string) => void;
  onDelete: (id: string) => void;
}

export default function FileGrid({ files, selectedIds, onToggleSelect, onDelete }: Props) {
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  if (files.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <div className="text-center">
          <FileText size={48} className="mx-auto mb-3" style={{ color: '#333' }} />
          <p style={{ color: '#555' }} className="text-sm">No hay archivos en esta categoría</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto p-6">
      <div className="grid gap-4" style={{ gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))' }}>
        {files.map(file => {
          const isSelected = selectedIds.has(file.id);
          const isHovered = hoveredId === file.id;

          return (
            <div
              key={file.id}
              onMouseEnter={() => setHoveredId(file.id)}
              onMouseLeave={() => setHoveredId(null)}
              className="relative rounded-xl overflow-hidden transition-all"
              style={{
                background: '#1a1a1e',
                border: isSelected ? '1.5px solid #3b82f6' : '1px solid #2a2a2e',
                boxShadow: isSelected ? '0 0 0 2px rgba(59,130,246,0.15)' : undefined,
              }}
            >
              {/* Checkbox */}
              <button
                onClick={() => onToggleSelect(file.id)}
                className="absolute top-2.5 left-2.5 z-10 w-5 h-5 rounded flex items-center justify-center transition-all"
                style={{
                  background: isSelected ? '#2563eb' : 'rgba(0,0,0,0.4)',
                  border: isSelected ? '1.5px solid #3b82f6' : '1.5px solid #444',
                  backdropFilter: 'blur(4px)',
                }}
              >
                {isSelected && (
                  <svg width="10" height="8" viewBox="0 0 10 8" fill="none">
                    <path d="M1 4L3.5 6.5L9 1" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                )}
              </button>

              {/* Thumbnail */}
              <div
                className="relative flex items-center justify-center"
                style={{ height: 180, background: '#1e1e22' }}
              >
                <FileText size={44} style={{ color: '#3a3a3e' }} />

                {/* Hover actions */}
                {isHovered && (
                  <div className="absolute bottom-2.5 right-2.5 flex gap-1.5">
                    <button
                      className="w-8 h-8 rounded-lg flex items-center justify-center transition-colors hover:opacity-90"
                      style={{ background: '#2563eb' }}
                      title="Descargar"
                    >
                      <Download size={14} className="text-white" />
                    </button>
                    <button
                      onClick={() => onDelete(file.id)}
                      className="w-8 h-8 rounded-lg flex items-center justify-center transition-colors"
                      style={{ background: '#2a2a2e' }}
                      title="Eliminar"
                    >
                      <Trash2 size={14} className="text-gray-400 hover:text-red-400" />
                    </button>
                  </div>
                )}
              </div>

              {/* Info */}
              <div className="p-3">
                <p className="text-sm font-medium text-white truncate mb-1.5">{file.name}</p>

                {/* Subcategory tag */}
                <div className="flex items-center gap-1.5 mb-2">
                  <Tag size={11} style={{ color: '#60a5fa' }} />
                  <span
                    className="text-xs px-2 py-0.5 rounded-full font-medium"
                    style={{ background: 'rgba(37,99,235,0.2)', color: '#60a5fa' }}
                  >
                    {file.subCategoryName}
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-xs" style={{ color: '#666' }}>{file.size}</span>
                  <span className="text-xs" style={{ color: '#666' }}>{file.date}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
