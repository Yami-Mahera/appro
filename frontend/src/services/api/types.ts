// Types pour les paramètres de requête
export interface BaseQueryParams {
  search?: string;
  sort_by?: string;
  sort_order?: string;
  limit?: number;
  skip?: number;
}

export interface UsersQueryParams extends BaseQueryParams {
  role?: string;
  active?: boolean;
}

export interface FournisseursQueryParams extends BaseQueryParams {
  ville?: string;
  pays?: string;
  active?: boolean;
}

export interface ArticlesQueryParams extends BaseQueryParams {
  famille?: string;
  fournisseur_id?: string;
  stock_bas?: boolean;
  active?: boolean;
}

export interface CommandesQueryParams extends BaseQueryParams {
  status?: string;
  fournisseur_id?: string;
  date_from?: string;
  date_to?: string;
}

export interface DateRangeParams {
  date_from?: string;
  date_to?: string;
}

export interface EcartsQueryParams {
  type_ecart?: string;
}

// Types pour les réponses API
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Types pour les entités
export interface User {
  id: string;
  email: string;
  nom: string;
  prenom: string;
  role: string;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Fournisseur {
  id: string;
  nom: string;
  email?: string;
  telephone?: string;
  adresse?: string;
  ville?: string;
  pays?: string;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Article {
  id: string;
  nom: string;
  reference: string;
  famille?: string;
  fournisseur_id: string;
  stock_actuel: number;
  stock_minimum: number;
  prix_unitaire: number;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Commande {
  id: string;
  numero: string;
  fournisseur_id: string;
  status: string;
  date_commande: string;
  date_livraison_prevue?: string;
  total: number;
  created_at: string;
  updated_at: string;
}
