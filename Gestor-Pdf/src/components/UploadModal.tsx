import React, { useState, useRef } from 'react';
import { X, Upload, CheckCircle } from 'lucide-react';

interface Props {
  onClose: () => void;
  onUpload: (fileName: string, category: string) => void;
}

type Stage = 'idle' | 'uploading' | 'done';

export default function UploadModal({ onClose, onUpload }: Props) {
  const [stage, setStage] = useState<Stage>('idle');
  const [progress, setProgress] = useState(0);
  const [assignedCat, setAssignedCat] = useState('');
  const [dragging, setDragging] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  const mockCategories = ['JavaScript', 'Python', 'React', 'Matemáticas', 'Diseño', 'General'];

  const startUpload = (name: string) => {
    setStage('uploading');
    setProgress(0);
    const cat = mockCategories[Math.floor(Math.random() * mockCategories.length)];

    const interval = setInterval(() => {
      setProgress(p => {
        if (p >= 100) {
          clearInterval(interval);
          setAssignedCat(cat);
          setStage('done');
          onUpload(name, cat);
          return 100;
        }
        return p + 5;
      });
    }, 80);
  };

  const handleFile = (f: File) => {
    if (f.type === 'application/pdf' || f.name.endsWith('.pdf')) {
      startUpload(f.name);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) handleFile(f);
  };

  return (
    <div className="fixed inset-0 flex items-center justify-center z-50" style={{ background: 'rgba(0,0,0,0.7)' }}>
      <div
        className="rounded-2xl w-full max-w-md relative"
        style={{ background: '#1c1c1e', border: '1px solid #2a2a2e' }}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4" style={{ borderBottom: '1px solid #2a2a2e' }}>
          <h3 className="text-white font-semibold">Cargar y Clasificar Documentos</h3>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-gray-500 hover:text-white hover:bg-white/10 transition-colors"
          >
            <X size={16} />
          </button>
        </div>

        <div className="p-5">
          {stage === 'idle' && (
            <div
              onDragOver={e => { e.preventDefault(); setDragging(true); }}
              onDragLeave={() => setDragging(false)}
              onDrop={handleDrop}
              onClick={() => fileRef.current?.click()}
              className="flex flex-col items-center justify-center rounded-xl py-12 px-6 text-center cursor-pointer transition-all"
              style={{
                border: `2px dashed ${dragging ? '#3b82f6' : '#2a2a2e'}`,
                background: dragging ? 'rgba(59,130,246,0.05)' : 'transparent',
              }}
            >
              <div
                className="w-14 h-14 rounded-xl flex items-center justify-center mb-4"
                style={{ background: '#2a2a2e' }}
              >
                <Upload size={26} style={{ color: '#666' }} />
              </div>
              <p className="text-white font-medium mb-1">Arrastra tus archivos PDF aquí</p>
              <p className="text-sm mb-4" style={{ color: '#666' }}>o haz clic para seleccionar</p>
              <button
                className="px-5 py-2 rounded-lg text-sm font-semibold text-white transition-opacity hover:opacity-90"
                style={{ background: '#2563eb' }}
              >
                Seleccionar archivos
              </button>
              <input
                ref={fileRef}
                type="file"
                accept="application/pdf"
                className="hidden"
                onChange={handleInputChange}
              />
            </div>
          )}

          {stage === 'uploading' && (
            <div className="py-8 text-center">
              <div className="mb-5">
                <div
                  className="h-2 rounded-full overflow-hidden"
                  style={{ background: '#2a2a2e' }}
                >
                  <div
                    className="h-full rounded-full transition-all duration-100"
                    style={{ width: `${progress}%`, background: '#2563eb' }}
                  />
                </div>
                <p className="text-sm mt-3 text-gray-400">
                  {progress < 60 ? 'Subiendo archivo...' : 'Analizando palabras clave...'}
                </p>
              </div>
              <p className="text-2xl font-bold text-white">{progress}%</p>
            </div>
          )}

          {stage === 'done' && (
            <div className="py-8 text-center">
              <div
                className="w-14 h-14 rounded-full flex items-center justify-center mx-auto mb-4"
                style={{ background: 'rgba(34,197,94,0.15)' }}
              >
                <CheckCircle size={28} className="text-green-400" />
              </div>
              <h4 className="text-white font-semibold text-lg mb-1">¡Documento clasificado!</h4>
              <p className="text-sm text-gray-400 mb-3">
                El archivo fue asignado automáticamente a:
              </p>
              <span
                className="px-3 py-1 rounded-full text-sm font-semibold"
                style={{ background: 'rgba(37,99,235,0.2)', color: '#60a5fa' }}
              >
                {assignedCat}
              </span>
              <div className="mt-5">
                <button
                  onClick={onClose}
                  className="px-6 py-2 rounded-lg text-sm font-semibold text-white transition-opacity hover:opacity-90"
                  style={{ background: '#2563eb' }}
                >
                  Cerrar
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
