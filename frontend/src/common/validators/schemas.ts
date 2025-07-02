import { z } from 'zod';

// Auth schemas
export const loginSchema = z.object({
  email: z.string().email('Email invalide'),
  password: z.string().min(6, 'Le mot de passe doit contenir au moins 6 caractères')
});

export const registerSchema = z.object({
  email: z.string().email('Email invalide'),
  password: z.string().min(6, 'Le mot de passe doit contenir au moins 6 caractères'),
  nom: z.string().min(2, 'Le nom doit contenir au moins 2 caractères'),
  prenom: z.string().min(2, 'Le prénom doit contenir au moins 2 caractères'),
  role: z.enum(['administrateur', 'manager', 'utilisateur']).default('utilisateur')
});

// Fournisseur schemas
export const contactSchema = z.object({
  nom: z.string().min(2, 'Le nom doit contenir au moins 2 caractères'),
  prenom: z.string().min(2, 'Le prénom doit contenir au moins 2 caractères'),
  telephone: z.string().optional(),
  email: z.string().email('Email invalide').optional(),
  poste: z.string().optional()
});

export const fournisseurSchema = z.object({
  nom: z.string().min(2, 'Le nom doit contenir au moins 2 caractères'),
  code_fournisseur: z.string().min(2, 'Le code fournisseur est requis'),
  adresse: z.string().min(5, 'L\'adresse doit contenir au moins 5 caractères'),
  ville: z.string().min(2, 'La ville est requise'),
  code_postal: z.string().regex(/^\d{5}$/, 'Code postal invalide'),
  pays: z.string().min(2, 'Le pays est requis'),
  telephone: z.string().optional(),
  email: z.string().email('Email invalide').optional(),
  site_web: z.string().url('URL invalide').optional(),
  conditions_paiement: z.string().optional(),
  delai_livraison_moyen: z.number().positive().optional(),
  contacts: z.array(contactSchema).default([])
});

// Article schemas
export const articleSchema = z.object({
  reference: z.string().min(2, 'La référence est requise'),
  nom: z.string().min(2, 'Le nom doit contenir au moins 2 caractères'),
  description: z.string().optional(),
  famille: z.string().optional(),
  fournisseur_id: z.string().min(1, 'Le fournisseur est requis'),
  prix_unitaire: z.number().positive('Le prix doit être positif'),
  unite: z.string().min(1, 'L\'unité est requise'),
  seuil_min: z.number().min(0, 'Le seuil minimum ne peut être négatif').default(0),
  seuil_max: z.number().min(0, 'Le seuil maximum ne peut être négatif').default(0),
  stock_actuel: z.number().min(0, 'Le stock ne peut être négatif').default(0),
  duree_vie: z.number().positive().optional(),
  emplacement_stockage: z.string().optional()
});

// Commande schemas
export const ligneCommandeSchema = z.object({
  article_id: z.string().min(1, 'L\'article est requis'),
  quantite: z.number().positive('La quantité doit être positive'),
  prix_unitaire: z.number().positive('Le prix doit être positif'),
  total: z.number().positive('Le total doit être positif')
});

export const commandeSchema = z.object({
  fournisseur_id: z.string().min(1, 'Le fournisseur est requis'),
  lignes: z.array(ligneCommandeSchema).min(1, 'Au moins une ligne est requise'),
  date_livraison_prevue: z.date().optional(),
  notes: z.string().optional()
});

export type LoginData = z.infer<typeof loginSchema>;
export type RegisterData = z.infer<typeof registerSchema>;
export type FournisseurData = z.infer<typeof fournisseurSchema>;
export type ArticleData = z.infer<typeof articleSchema>;
export type CommandeData = z.infer<typeof commandeSchema>;