export interface Category {
  id: string;
  name: string;
  subCategories: SubCategory[];
}

export interface SubCategory {
  id: string;
  name: string;
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

export type Role = 'admin' | 'user';

export interface User {
  id: string;
  username: string;
  role: Role;
  folders: number;
}