// Auth types
export interface User {
  id: string;
  email: string;
  nom: string;
  prenom: string;
  role: 'administrateur' | 'manager' | 'utilisateur';
  active: boolean;
  created_at: string;
  last_login?: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
}

// Fournisseur types
export interface Contact {
  nom: string;
  prenom: string;
  telephone?: string;
  email?: string;
  poste?: string;
}

export interface Fournisseur {
  id: string;
  nom: string;
  code_fournisseur: string;
  adresse: string;
  ville: string;
  code_postal: string;
  pays: string;
  telephone?: string;
  email?: string;
  site_web?: string;
  conditions_paiement?: string;
  delai_livraison_moyen?: number;
  contacts: Contact[];
  active: boolean;
  created_at: string;
  updated_at: string;
}

// Article types
export interface Article {
  id: string;
  reference: string;
  nom: string;
  description?: string;
  famille?: string;
  fournisseur_id: string;
  prix_unitaire: number;
  unite: string;
  seuil_min: number;
  seuil_max: number;
  stock_actuel: number;
  duree_vie?: number;
  emplacement_stockage?: string;
  active: boolean;
  created_at: string;
  updated_at: string;
}

// Commande types
export interface LigneCommande {
  article_id: string;
  quantite: number;
  prix_unitaire: number;
  total: number;
}

export type CommandeStatus = 
  | 'brouillon'
  | 'en_attente'
  | 'approuvee'
  | 'commandee'
  | 'livree'
  | 'annulee';

export interface Commande {
  id: string;
  numero_commande: string;
  fournisseur_id: string;
  status: CommandeStatus;
  lignes: LigneCommande[];
  total_ht: number;
  total_ttc: number;
  taux_tva: number;
  date_commande?: string;
  date_livraison_prevue?: string;
  date_livraison_reelle?: string;
  notes?: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

// Alerte types
export type AlerteType = 'stock_bas' | 'retard_livraison' | 'seuil_atteint' | 'commande_urgente';
export type AlertePriorite = 'low' | 'medium' | 'high' | 'critical';

export interface Alerte {
  id: string;
  type: AlerteType;
  priorite: AlertePriorite;
  titre: string;
  message: string;
  article_id?: string;
  commande_id?: string;
  fournisseur_id?: string;
  lue: boolean;
  created_at: string;
}

// Dashboard types
export interface DashboardStats {
  total_fournisseurs: number;
  total_articles: number;
  total_commandes: number;
  alertes_non_lues: number;
  articles_stock_bas: number;
  commandes_en_cours: number;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
}