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

// Types pour la gestion avancée des stocks

export type TypeMouvement = 'entree' | 'sortie' | 'ajustement' | 'transfert';

export interface MouvementStock {
  id: string;
  article_id: string;
  type_mouvement: TypeMouvement;
  quantite: number;
  stock_avant: number;
  stock_apres: number;
  date_mouvement: string;
  commande_id?: string;
  reference_document?: string;
  commentaire?: string;
  created_by: string;
  created_at: string;
}

export interface PrevisionConsommation {
  id: string;
  article_id: string;
  semaine: number;
  annee: number;
  date_debut_semaine: string;
  date_fin_semaine: string;
  quantite_prevue: number;
  quantite_reelle?: number;
  ecart_absolu?: number;
  ecart_relatif?: number;
  created_at: string;
  updated_at: string;
}

export interface CalculCouverture {
  id: string;
  article_id: string;
  date_calcul: string;
  variation_logistique: number;
  variation_prevision: number;
  horizon: number;
  couverture_minimale_securite: number;
  couverture_maximale_commande: number;
  quantite_maximale_commande: number;
  couverture_actuelle: number;
  date_besoin?: string;
  date_arrivee_prevue?: string;
  stock_actuel: number;
  moyenne_consommation_hebdo: number;
  duree_vie_produit: number;
  delai_acheminement: number;
  created_at: string;
}

export type NiveauAlerte = 'normal' | 'urgent' | 'critique' | 'a_suivre';

export interface AlerteAvancee {
  id: string;
  article_id: string;
  commande_id?: string;
  niveau_alerte: NiveauAlerte;
  type_alerte: string;
  date_besoin?: string;
  date_observation: string;
  delai_passation: number;
  ecart_jours?: number;
  couverture_prevue?: number;
  couverture_minimale?: number;
  pourcentage_variation?: number;
  message: string;
  recommandation: string;
  lue: boolean;
  created_at: string;
}

export interface EvolutionStockData {
  semaine: number;
  date_debut: string;
  date_fin: string;
  stock_debut: number;
  stock_fin: number;
  prevision_consommation: number;
  consommation_reelle: number;
  mouvements: number;
}

export interface EvolutionStockResponse {
  article_id: string;
  periode: string;
  evolution: EvolutionStockData[];
}

export interface CompositionTC {
  id: string;
  reference_tc: string;
  articles: any[];
  nombre_conteneurs: number;
  quantite_complement: Record<string, number>;
  quantite_alignement: Record<string, number>;
  date_besoin_groupe?: string;
  created_at: string;
}

// Types pour les graphiques avancés
export interface StockCoverageData {
  semaine: number;
  date: string;
  stock_niveau: number;
  couverture_moyenne_precedente: number;
  couverture_moyenne_actuelle: number;
  couverture_prevision_mensuelle: number;
  zone_ecartement_min: number;
  zone_ecartement_max: number;
  annotations: StockAnnotation[];
}

export interface StockAnnotation {
  semaine: number;
  type: string;
  label: string;
  value: string;
  position: 'top' | 'bottom' | 'middle';
}