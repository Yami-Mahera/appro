export interface User {
  id: string;
  email: string;
  nom: string;
  prenom: string;
  role: UserRole;
  active: boolean;
  created_at: string;
  last_login?: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface UserCreate {
  email: string;
  password: string;
  nom: string;
  prenom: string;
  role?: UserRole;
}

export enum UserRole {
  ADMIN = "administrateur",
  MANAGER = "manager", 
  USER = "utilisateur"
}

export interface Token {
  access_token: string;
  token_type: string;
  user: User;
}

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

export interface FournisseurCreate {
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
  contacts?: Contact[];
}

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

export interface ArticleCreate {
  reference: string;
  nom: string;
  description?: string;
  famille?: string;
  fournisseur_id: string;
  prix_unitaire: number;
  unite: string;
  seuil_min?: number;
  seuil_max?: number;
  stock_actuel?: number;
  duree_vie?: number;
  emplacement_stockage?: string;
}

export interface LigneCommande {
  article_id: string;
  quantite: number;
  prix_unitaire: number;
  total: number;
}

export enum CommandeStatus {
  DRAFT = "brouillon",
  PENDING = "en_attente",
  APPROVED = "approuvee",
  ORDERED = "commandee",
  DELIVERED = "livree",
  CANCELLED = "annulee"
}

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

export interface CommandeCreate {
  fournisseur_id: string;
  lignes: LigneCommande[];
  date_livraison_prevue?: string;
  notes?: string;
}

export enum AlerteType {
  STOCK_BAS = "stock_bas",
  RETARD_LIVRAISON = "retard_livraison", 
  SEUIL_ATTEINT = "seuil_atteint",
  COMMANDE_URGENTE = "commande_urgente"
}

export enum AlertePriorite {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  CRITICAL = "critical"
}

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

export interface DashboardStats {
  total_fournisseurs: number;
  total_articles: number;
  total_commandes: number;
  alertes_non_lues: number;
  articles_stock_bas: number;
  commandes_en_cours: number;
}