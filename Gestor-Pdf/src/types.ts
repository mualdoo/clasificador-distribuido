export interface SubCategory {
  id: string;
  name: string;
}

export interface Category {
  id: string;
  name: string;
  subCategories: SubCategory[];
}

export interface PDFFile {
  id: string;
  name: string;
  size: string;
  date: string;
  categoryId: string;
  subCategoryId: string;
  subCategoryName: string;
}

export interface User {
  id: string;
  username: string;
  role: 'admin' | 'user';
  folders: number;
}

export type Role = 'admin' | 'user';
