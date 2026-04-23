import React, { useState } from 'react';
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

const INITIAL_FILES: PDFFile[] = [
  { id: 'f1', name: 'JavaScript Avanzado.pdf',    size: '5.1 MB', date: '12/04/2026', categoryId: 'prog',   subCategoryId: 'js',    subCategoryName: 'JavaScript' },
  { id: 'f2', name: 'TypeScript Básico.pdf',       size: '4.5 MB', date: '05/04/2026', categoryId: 'prog',   subCategoryId: 'js',    subCategoryName: 'JavaScript' },
  { id: 'f3', name: 'Python para Data Science.pdf',size: '7.2 MB', date: '01/04/2026', categoryId: 'prog',   subCategoryId: 'py',    subCategoryName: 'Python'     },
  { id: 'f4', name: 'React Hooks en Profundidad.pdf',size:'3.8 MB',date: '20/03/2026', categoryId: 'prog',   subCategoryId: 'react', subCategoryName: 'React'      },
  { id: 'f5', name: 'Cálculo Diferencial.pdf',     size: '6.1 MB', date: '15/03/2026', categoryId: 'math',   subCategoryId: 'calc',  subCategoryName: 'Cálculo'    },
  { id: 'f6', name: 'Álgebra Lineal Moderna.pdf',  size: '5.4 MB', date: '10/03/2026', categoryId: 'math',   subCategoryId: 'alg',   subCategoryName: 'Álgebra'    },
  { id: 'f7', name: 'Fundamentos de UI.pdf',       size: '4.9 MB', date: '08/03/2026', categoryId: 'design', subCategoryId: 'ui',    subCategoryName: 'UI/UX'      },
  { id: 'f8', name: 'Guía de Branding 2026.pdf',   size: '8.3 MB', date: '02/03/2026', categoryId: 'design', subCategoryId: 'brand', subCategoryName: 'Branding'   },
  { id: 'f9', name: 'Estrategia de Marketing.pdf', size: '3.2 MB', date: '25/02/2026', categoryId: 'biz',    subCategoryId: 'mkt',   subCategoryName: 'Marketing'  },
  { id:'f10', name: 'Análisis Financiero.pdf',     size: '5.7 MB', date: '18/02/2026', categoryId: 'biz',    subCategoryId: 'fin',   subCategoryName: 'Finanzas'   },
  { id:'f11', name: 'Documento Sin Clasificar.pdf',size: '2.1 MB', date: '10/02/2026', categoryId: 'general',subCategoryId: '',      subCategoryName: 'General'    },
];

const INITIAL_USERS: User[] = [
  { id: 'u1', username: 'usuario1',   role: 'user',  folders: 5 },
  { id: 'u2', username: 'usuario2',   role: 'user',  folders: 3 },
  { id: 'u3', username: 'admin',      role: 'admin', folders: 0 },
  { id: 'u4', username: 'maria.lopez',role: 'user',  folders: 8 },
  { id: 'u5', username: 'carlos.ruiz',role: 'user',  folders: 2 },
];

// ─── App ─────────────────────────────────────────────────────────────────────
export default function App() {
  // Auth
  const [loggedIn, setLoggedIn]     = useState(false);
  const [username, setUsername]     = useState('');
  const [role, setRole]             = useState<Role>('user');

  // Data
  const [categories, setCategories] = useState<Category[]>(INITIAL_CATEGORIES);
  const [files, setFiles]           = useState<PDFFile[]>(INITIAL_FILES);
  const [users, setUsers]           = useState<User[]>(INITIAL_USERS);

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
    setRole(r);
    setLoggedIn(true);
    setSelCatId(null);
    setSelSubId(null);
  };

  const handleLogout = () => {
    setLoggedIn(false);
    setUsername('');
    setRole('user');
    setSelectedIds(new Set());
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
  const handleDeleteFile = (fileId: string) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
    setSelectedIds(prev => { const s = new Set(prev); s.delete(fileId); return s; });
  };

  const handleToggleSelect = (fileId: string) => {
    setSelectedIds(prev => {
      const s = new Set(prev);
      s.has(fileId) ? s.delete(fileId) : s.add(fileId);
      return s;
    });
  };

  // ── Upload ─────────────────────────────────────────────────────────────────
  const handleUpload = (fileName: string, _category: string) => {
    const newFile: PDFFile = {
      id: 'f-' + Date.now(),
      name: fileName,
      size: `${(Math.random() * 8 + 1).toFixed(1)} MB`,
      date: new Date().toLocaleDateString('es-MX', { day: '2-digit', month: '2-digit', year: 'numeric' }).replace(/\//g, '/'),
      categoryId: 'general',
      subCategoryId: '',
      subCategoryName: 'General',
    };
    setFiles(prev => [...prev, newFile]);
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
  if (!loggedIn) return <LoginModal onLogin={handleLogin} />;

  const isAdmin = role === 'admin';

  return (
    <div className="flex flex-col h-screen" style={{ background: '#0a0a0c' }}>
      {/* Header */}
      <Header
        username={username}
        role={role}
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
      <NodesIndicator />

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
