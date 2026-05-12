import React, { useState, useEffect } from 'react';

import { FileText } from 'lucide-react';
import LoginModal from './components/LoginModal';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import FileGrid from './components/FileGrid';
import UploadModal from './components/UploadModal';
import CitationModal from './components/CitationModal';
import AdminView from './components/AdminView';
import NodesIndicator from './components/NodesIndicator';
import { Category, PDFFile, Role, User } from './types';

//el coso del api Xd
import { getFiles, logout as apiLogout, getProfile, deleteFile } from './api'


// ─── Seed data ───────────────────────────────────────────────────────────────
const INITIAL_CATEGORIES: Category[] = [
  {
    id: 'prog', name: 'Programación',
    subCategories: [
      { id: 'js', name: 'JavaScript' },
      { id: 'py', name: 'Python' },
      { id: 'react', name: 'React' },
    ],
  },
  {
    id: 'math', name: 'Matemáticas',
    subCategories: [
      { id: 'calc', name: 'Cálculo' },
      { id: 'alg', name: 'Álgebra' },
    ],
  },
  {
    id: 'design', name: 'Diseño',
    subCategories: [
      { id: 'ui', name: 'UI/UX' },
      { id: 'brand', name: 'Branding' },
    ],
  },
  {
    id: 'biz', name: 'Negocios',
    subCategories: [
      { id: 'mkt', name: 'Marketing' },
      { id: 'fin', name: 'Finanzas' },
    ],
  },
];



// ─── App ─────────────────────────────────────────────────────────────────────
export default function App() {
  // Auth
  const [loggedIn, setLoggedIn]     = useState(false);
  const [username, setUsername]     = useState('');
const [role, setRole]             = useState<Role>('user'); 
const [actualRole, setActualRole] = useState<Role>('user'); 

  // Data
  const [categories, setCategories] = useState<Category[]>(INITIAL_CATEGORIES);
  const [files, setFiles]           = useState<PDFFile[]>([]);
  const [users, setUsers]           = useState<User[]>([]);

  // Navigation
  const [selCatId, setSelCatId]     = useState<string | null>(null);
  const [selSubId, setSelSubId]     = useState<string | null>(null);

  // Selection
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  // Modals
  const [showUpload,   setShowUpload]   = useState(false);
  const [showCitation, setShowCitation] = useState(false);

  // ── Auth handlers ──────────────────────────────────────────────────────────
  const handleLogin = (uname: string, r: Role) => {
    setUsername(uname);
    setActualRole(r);
    setRole(r);
    setLoggedIn(true);
    setSelCatId(null);
    setSelSubId(null);
  };

  const handleLogout = async () => {
  try {
    await apiLogout();
  } catch (error) {
    console.error('Error al cerrar sesión:', error);
  }
  setLoggedIn(false);
  setUsername('');
  setRole('user');
  setSelectedIds(new Set());
  setFiles([]);
};

  // ── Navigation ─────────────────────────────────────────────────────────────
  const handleSelectCategory = (catId: string) => {
    setSelCatId(catId);
    setSelSubId(null);
    setSelectedIds(new Set());
  };

  const handleSelectSubCategory = (catId: string, subId: string) => {
    setSelCatId(catId);
    setSelSubId(subId);
    setSelectedIds(new Set());
  };

  // ── Category CRUD ──────────────────────────────────────────────────────────
  const handleAddCategory = (name: string) => {
    const id = name.toLowerCase().replace(/\s+/g, '-') + '-' + Date.now();
    setCategories(prev => [...prev, { id, name, subCategories: [] }]);
  };

  const handleDeleteCategory = (catId: string) => {
    setCategories(prev => prev.filter(c => c.id !== catId));
    if (selCatId === catId) { setSelCatId(null); setSelSubId(null); }
  };

  const handleAddSubCategory = (catId: string, name: string) => {
    const id = name.toLowerCase().replace(/\s+/g, '-') + '-' + Date.now();
    setCategories(prev =>
      prev.map(c => c.id === catId
        ? { ...c, subCategories: [...c.subCategories, { id, name }] }
        : c
      )
    );
  };

  const handleDeleteSubCategory = (catId: string, subId: string) => {
    setCategories(prev =>
      prev.map(c => c.id === catId
        ? { ...c, subCategories: c.subCategories.filter(s => s.id !== subId) }
        : c
      )
    );
    if (selSubId === subId) setSelSubId(null);
  };

  // ── File CRUD ──────────────────────────────────────────────────────────────
 const handleDeleteFile = async (fileId: string) => {
  try {
    await deleteFile(fileId);
    setFiles(prev => prev.filter(f => f.id !== fileId));
    setSelectedIds(prev => { const s = new Set(prev); s.delete(fileId); return s; });
  } catch (error) {
    console.error('Error al eliminar archivo:', error);
    alert('Error al eliminar el archivo');
  }
  };
  const handleToggleSelect = (fileId: string) => {
    setSelectedIds(prev => {
      const s = new Set(prev);
      s.has(fileId) ? s.delete(fileId) : s.add(fileId);
      return s;
    });
  };

  // ── Upload ─────────────────────────────────────────────────────────────────
 const handleUpload = async (fileName: string, _category: string) => {
  // Esta función se llamará desde UploadModal después de subir el archivo
  await loadFiles(); // Recargar la lista de archivos
};

  // ── User management ────────────────────────────────────────────────────────
  const handleDeleteUser = (userId: string) => {
    setUsers(prev => prev.filter(u => u.id !== userId));
  };

  // ── Derived: visible files ─────────────────────────────────────────────────
  const visibleFiles = (() => {
    if (!selCatId) return [];
    if (selSubId) return files.filter(f => f.categoryId === selCatId && f.subCategoryId === selSubId);
    return files.filter(f => f.categoryId === selCatId);
  })();

  const selectedFiles = visibleFiles.filter(f => selectedIds.has(f.id));

  // ── Current view title ─────────────────────────────────────────────────────
  const currentTitle = (() => {
    if (!selCatId) return null;
    if (selCatId === 'general') return 'General';
    const cat = categories.find(c => c.id === selCatId);
    if (!cat) return null;
    if (selSubId) {
      const sub = cat.subCategories.find(s => s.id === selSubId);
      return sub ? `${cat.name} › ${sub.name}` : cat.name;
    }
    return cat.name;
  })();

  // ─────────────────────────────────────────────────────────────────────────

    useEffect(() => {
    if (loggedIn) {
      loadFiles();
    }
  }, [loggedIn]);

  const loadFiles = async () => {
    try {
      const data = await getFiles();
      // Transformar los datos del backend al formato de la UI
      const transformedFiles = data.archivos.map((file: any) => ({
        id: file.id,
        name: file.nombre,
        size: `${(file.tamano / 1024 / 1024).toFixed(1)} MB`,
        date: new Date(file.fecha_subida).toLocaleDateString('es-MX', { 
          day: '2-digit', 
          month: '2-digit', 
          year: 'numeric' 
        }),
        categoryId: file.categoria || 'general',
        subCategoryId: file.subcategoria || '',
        subCategoryName: file.subcategoria || 'General',
      }));
      setFiles(transformedFiles);
    } catch (error) {
      console.error('Error al cargar archivos:', error);
    }
  };

  if (!loggedIn) return <LoginModal onLogin={handleLogin} />;

  const isAdmin = role === 'admin';

  return (
    <div className="flex flex-col h-screen" style={{ background: '#0a0a0c' }}>
      {/* Header */}
      <Header
        username={username}
        role={role}
        actualRole={actualRole} 
        onRoleChange={setRole}
        onLogout={handleLogout}
      />

      {/* Body */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <Sidebar
          categories={categories}
          selectedCategoryId={selCatId}
          selectedSubCategoryId={selSubId}
          onSelectCategory={handleSelectCategory}
          onSelectSubCategory={handleSelectSubCategory}
          onAddCategory={handleAddCategory}
          onDeleteCategory={handleDeleteCategory}
          onAddSubCategory={handleAddSubCategory}
          onDeleteSubCategory={handleDeleteSubCategory}
          isAdmin={isAdmin}
        />

        {/* Main content */}
        <main className="flex-1 flex flex-col overflow-hidden">
          {isAdmin ? (
            /* ── Admin Dashboard ── */
            <AdminView users={users} onDeleteUser={handleDeleteUser} />
          ) : (
            /* ── Standard user view ── */
            <>
              {/* Selection bar */}
              {selectedIds.size > 0 && (
                <div
                  className="flex items-center justify-between px-6 py-3 shrink-0"
                  style={{ background: '#0f1929', borderBottom: '1px solid #1e3a5f' }}
                >
                  <div className="flex items-center gap-2">
                    <FileText size={16} className="text-blue-400" />
                    <span className="text-sm text-blue-300 font-medium">
                      {selectedIds.size} documento{selectedIds.size !== 1 ? 's' : ''} seleccionado{selectedIds.size !== 1 ? 's' : ''}
                    </span>
                  </div>
                  <button
                    onClick={() => setShowCitation(true)}
                    className="px-4 py-1.5 rounded-lg text-sm font-semibold text-white transition-opacity hover:opacity-90"
                    style={{ background: '#2563eb' }}
                  >
                    Generar Citas (APA 7)
                  </button>
                </div>
              )}

              {/* Subheader */}
              {selCatId ? (
                <div
                  className="flex items-center justify-between px-6 py-4 shrink-0"
                  style={{ borderBottom: '1px solid #1e1e22' }}
                >
                  <div>
                    <h2 className="text-white font-semibold text-lg">{currentTitle}</h2>
                    <p className="text-sm text-gray-500 mt-0.5">
                      {visibleFiles.length} archivo{visibleFiles.length !== 1 ? 's' : ''} PDF
                    </p>
                  </div>
                  <button
                    onClick={() => setShowUpload(true)}
                    className="px-4 py-2 rounded-xl text-sm font-semibold text-white transition-opacity hover:opacity-90"
                    style={{ background: '#1e1e22', border: '1px solid #2a2a2e' }}
                  >
                    Cargar y clasificar
                  </button>
                </div>
              ) : (
                <div className="flex-1 flex items-center justify-center">
                  <div className="text-center">
                    <FileText size={56} className="mx-auto mb-4" style={{ color: '#222' }} />
                    <p className="text-gray-600 text-sm">Selecciona una categoría del sidebar</p>
                  </div>
                </div>
              )}

              {/* File grid */}
              {selCatId && (
                <FileGrid
                  files={visibleFiles}
                  selectedIds={selectedIds}
                  onToggleSelect={handleToggleSelect}
                  onDelete={handleDeleteFile}
                />
              )}
            </>
          )}
        </main>
      </div>

      {/* Footer */}
      <NodesIndicator  actualRole={actualRole}/>

      {/* Modals */}
      {showUpload && (
        <UploadModal
          onClose={() => setShowUpload(false)}
          onUpload={handleUpload}
        />
      )}
      {showCitation && (
        <CitationModal
          files={selectedFiles}
          onClose={() => setShowCitation(false)}
        />
      )}
    </div>
  );
}
