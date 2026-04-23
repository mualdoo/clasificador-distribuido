import React, { useState } from 'react';
import {
  Folder, FolderOpen, ChevronRight, ChevronDown,
  Plus, Trash2, Circle
} from 'lucide-react';
import { Category } from '../types';

interface Props {
  categories: Category[];
  selectedCategoryId: string | null;
  selectedSubCategoryId: string | null;
  onSelectCategory: (catId: string) => void;
  onSelectSubCategory: (catId: string, subId: string) => void;
  onAddCategory: (name: string) => void;
  onDeleteCategory: (catId: string) => void;
  onAddSubCategory: (catId: string, name: string) => void;
  onDeleteSubCategory: (catId: string, subId: string) => void;
  isAdmin: boolean;
}

export default function Sidebar({
  categories, selectedCategoryId, selectedSubCategoryId,
  onSelectCategory, onSelectSubCategory,
  onAddCategory, onDeleteCategory, onAddSubCategory, onDeleteSubCategory,
  isAdmin,
}: Props) {
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [addingCat, setAddingCat] = useState(false);
  const [newCatName, setNewCatName] = useState('');
  const [addingSubFor, setAddingSubFor] = useState<string | null>(null);
  const [newSubName, setNewSubName] = useState('');
  const [hoveredCat, setHoveredCat] = useState<string | null>(null);
  const [hoveredSub, setHoveredSub] = useState<string | null>(null);

  const toggleExpand = (id: string) => {
    setExpanded(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const handleAddCat = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && newCatName.trim()) {
      onAddCategory(newCatName.trim());
      setNewCatName('');
      setAddingCat(false);
    }
    if (e.key === 'Escape') { setAddingCat(false); setNewCatName(''); }
  };

  const handleAddSub = (e: React.KeyboardEvent, catId: string) => {
    if (e.key === 'Enter' && newSubName.trim()) {
      onAddSubCategory(catId, newSubName.trim());
      setNewSubName('');
      setAddingSubFor(null);
    }
    if (e.key === 'Escape') { setAddingSubFor(null); setNewSubName(''); }
  };

  const isGeneralSelected = selectedCategoryId === 'general' && !selectedSubCategoryId;

  return (
    <aside
      className="flex flex-col h-full"
      style={{ width: 230, background: '#111113', borderRight: '1px solid #1e1e22' }}
    >
      {/* Logo */}
      <div className="px-4 py-4" style={{ borderBottom: '1px solid #1e1e22' }}>
        <h1 className="text-white font-semibold text-base">Gestor PDF</h1>
      </div>

      {/* Temáticas header */}
      <div className="flex items-center justify-between px-4 pt-4 pb-2">
        <span className="text-xs font-semibold uppercase tracking-widest" style={{ color: '#555' }}>
          Temáticas
        </span>
        <button
          onClick={() => setAddingCat(true)}
          className="p-0.5 rounded transition-colors hover:bg-white/10 text-gray-500 hover:text-gray-300"
        >
          <Plus size={14} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-2 pb-4">
        {/* Add category input */}
        {addingCat && (
          <input
            autoFocus
            value={newCatName}
            onChange={e => setNewCatName(e.target.value)}
            onKeyDown={handleAddCat}
            onBlur={() => { setAddingCat(false); setNewCatName(''); }}
            placeholder="Nombre del tema…"
            className="w-full px-3 py-1.5 rounded-lg text-sm text-white placeholder-gray-600 mb-1 outline-none"
            style={{ background: '#2a2a2e', border: '1px solid #3a3a3e' }}
          />
        )}

        {/* General folder */}
        <button
          onClick={() => onSelectCategory('general')}
          className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors mb-0.5"
          style={{
            background: isGeneralSelected ? '#1e2a3a' : 'transparent',
            color: isGeneralSelected ? '#60a5fa' : '#ccc',
          }}
        >
          <Folder size={15} style={{ color: isGeneralSelected ? '#60a5fa' : '#888' }} />
          General
        </button>

        {/* Categories */}
        {categories.map(cat => {
          const isExp = expanded.has(cat.id);
          const isCatSelected = selectedCategoryId === cat.id && !selectedSubCategoryId;
          const hasFiles = cat.subCategories.length > 0; // simplified

          return (
            <div key={cat.id}>
              <div
                className="group relative"
                onMouseEnter={() => setHoveredCat(cat.id)}
                onMouseLeave={() => setHoveredCat(null)}
              >
                <button
                  onClick={() => {
                    toggleExpand(cat.id);
                    onSelectCategory(cat.id);
                  }}
                  className="w-full flex items-center gap-1.5 px-2 py-2 rounded-lg text-sm transition-colors"
                  style={{
                    background: isCatSelected ? '#1e2a3a' : 'transparent',
                    color: isCatSelected ? '#60a5fa' : '#ccc',
                  }}
                >
                  {isExp
                    ? <ChevronDown size={13} className="text-gray-500 shrink-0" />
                    : <ChevronRight size={13} className="text-gray-500 shrink-0" />
                  }
                  {isExp
                    ? <FolderOpen size={15} style={{ color: isCatSelected ? '#60a5fa' : '#888' }} className="shrink-0" />
                    : <Folder size={15} style={{ color: isCatSelected ? '#60a5fa' : '#888' }} className="shrink-0" />
                  }
                  <span className="flex-1 text-left truncate">{cat.name}</span>
                </button>

                {/* Hover actions for category */}
                {hoveredCat === cat.id && (
                  <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setAddingSubFor(cat.id);
                        if (!expanded.has(cat.id)) toggleExpand(cat.id);
                      }}
                      className="p-1 rounded text-gray-500 hover:text-gray-200 hover:bg-white/10 transition-colors"
                    >
                      <Plus size={12} />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        if (!hasFiles || isAdmin) onDeleteCategory(cat.id);
                      }}
                      className={`p-1 rounded transition-colors ${
                        !hasFiles || isAdmin
                          ? 'text-gray-500 hover:text-red-400 hover:bg-red-500/10'
                          : 'text-gray-700 cursor-not-allowed'
                      }`}
                      title={hasFiles && !isAdmin ? 'La carpeta no está vacía' : 'Eliminar'}
                    >
                      <Trash2 size={12} />
                    </button>
                  </div>
                )}
              </div>

              {/* Subcategories */}
              {isExp && (
                <div className="ml-5">
                  {cat.subCategories.map(sub => {
                    const isSubSelected = selectedCategoryId === cat.id && selectedSubCategoryId === sub.id;
                    const subKey = `${cat.id}-${sub.id}`;

                    return (
                      <div
                        key={sub.id}
                        className="group relative"
                        onMouseEnter={() => setHoveredSub(subKey)}
                        onMouseLeave={() => setHoveredSub(null)}
                      >
                        <button
                          onClick={() => onSelectSubCategory(cat.id, sub.id)}
                          className="w-full flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm transition-colors"
                          style={{
                            background: isSubSelected ? '#1e2a3a' : 'transparent',
                            color: isSubSelected ? '#60a5fa' : '#aaa',
                          }}
                        >
                          <Circle size={5} className="shrink-0" style={{ color: '#555' }} />
                          <span className="truncate">{sub.name}</span>
                        </button>
                        {hoveredSub === subKey && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              onDeleteSubCategory(cat.id, sub.id);
                            }}
                            className="absolute right-2 top-1/2 -translate-y-1/2 p-1 rounded text-gray-600 hover:text-red-400 hover:bg-red-500/10 transition-colors"
                          >
                            <Trash2 size={11} />
                          </button>
                        )}
                      </div>
                    );
                  })}

                  {/* Add subcategory input */}
                  {addingSubFor === cat.id && (
                    <input
                      autoFocus
                      value={newSubName}
                      onChange={e => setNewSubName(e.target.value)}
                      onKeyDown={e => handleAddSub(e, cat.id)}
                      onBlur={() => { setAddingSubFor(null); setNewSubName(''); }}
                      placeholder="Nombre del subtema…"
                      className="w-full px-3 py-1.5 rounded-lg text-xs text-white placeholder-gray-600 mt-0.5 outline-none"
                      style={{ background: '#2a2a2e', border: '1px solid #3a3a3e' }}
                    />
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </aside>
  );
}
