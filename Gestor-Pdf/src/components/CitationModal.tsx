import React, { useState } from 'react';
import { X, Copy, Check } from 'lucide-react';
import { PDFFile } from '../types';

interface Props {
  files: PDFFile[];
  onClose: () => void;
}

function generateAPA(file: PDFFile): string {
  const year = file.date.split('/')[2] || '2026';
  const title = file.name.replace('.pdf', '');
  return `Autor, A. A. (${year}). ${title}. Repositorio Gestor PDF. Recuperado de https://gestor-pdf.app/docs/${file.id}`;
}

export default function CitationModal({ files, onClose }: Props) {
  const [copied, setCopied] = useState(false);

  const citations = files.map(generateAPA).join('\n\n');

  const handleCopy = () => {
    navigator.clipboard.writeText(citations).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50" style={{ background: 'rgba(0,0,0,0.7)' }}>
      <div
        className="rounded-2xl w-full max-w-lg"
        style={{ background: '#1c1c1e', border: '1px solid #2a2a2e' }}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4" style={{ borderBottom: '1px solid #2a2a2e' }}>
          <div>
            <h3 className="text-white font-semibold">Citas en Formato APA 7</h3>
            <p className="text-xs text-gray-500 mt-0.5">{files.length} documento{files.length !== 1 ? 's' : ''} seleccionado{files.length !== 1 ? 's' : ''}</p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-gray-500 hover:text-white hover:bg-white/10 transition-colors"
          >
            <X size={16} />
          </button>
        </div>

        {/* Citations */}
        <div className="p-5">
          <div
            className="rounded-xl p-4 text-sm leading-relaxed"
            style={{ background: '#141416', border: '1px solid #2a2a2e', color: '#ccc', fontFamily: 'monospace', maxHeight: 300, overflowY: 'auto' }}
          >
            {files.map((file, i) => (
              <p key={file.id} className={i > 0 ? 'mt-4' : ''}>
                {generateAPA(file)}
              </p>
            ))}
          </div>

          <button
            onClick={handleCopy}
            className="mt-4 w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-semibold transition-all"
            style={{
              background: copied ? 'rgba(34,197,94,0.15)' : '#2563eb',
              color: copied ? '#4ade80' : '#fff',
            }}
          >
            {copied ? <Check size={15} /> : <Copy size={15} />}
            {copied ? '¡Copiado al portapapeles!' : 'Copiar al portapapeles'}
          </button>
        </div>
      </div>
    </div>
  );
}
