from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum
import uuid

# Enums pour les différents états et types
class EtatCommande(str, Enum):
    BROUILLON = "brouillon"
    PASSEE = "passee"
    CONFIRMEE = "confirmee"
    PRODUCTION = "production"
    EXPEDIEE = "expediee"
    LIVREE = "livree"
    FACTUREE = "facturee"
    ANNULEE = "annulee"

class TypeAlerte(str, Enum):
    CRITIQUE = "critique"
    IMPORTANTE = "importante"
    INFORMATIVE = "informative"

class StatutAlerte(str, Enum):
    ACTIVE = "active"
    TRAITEE = "traitee"
    IGNOREE = "ignoree"

class Devise(str, Enum):
    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"
    JPY = "JPY"

class ModeTransport(str, Enum):
    ROUTIER = "routier"
    MARITIME = "maritime"
    AERIEN = "aerien"
    FERROVIAIRE = "ferroviaire"

# Modèle Contact
class Contact(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nom: str
    prenom: str
    fonction: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    principal: bool = False
    actif: bool = True
    date_creation: datetime = Field(default_factory=datetime.utcnow)

class ContactCreate(BaseModel):
    nom: str
    prenom: str
    fonction: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    mobile: Optional[str] = None
    principal: bool = False

# Modèle Fournisseur
class Fournisseur(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str  # Code unique fournisseur
    nom: str
    raison_sociale: Optional[str] = None
    
    # Adresse
    adresse: Optional[str] = None
    ville: Optional[str] = None
    code_postal: Optional[str] = None
    pays: Optional[str] = None
    
    # Informations commerciales
    telephone: Optional[str] = None
    email: Optional[str] = None
    site_web: Optional[str] = None
    
    # Conditions commerciales
    delai_paiement: Optional[int] = None  # en jours
    mode_reglement: Optional[str] = None
    devise_principale: Devise = Devise.EUR
    taux_remise: Optional[float] = 0.0
    
    # Informations logistiques
    delai_livraison_standard: Optional[int] = None  # en jours
    quantite_min_commande: Optional[float] = 0.0
    frais_port: Optional[float] = 0.0
    
    # Contacts associés
    contacts: List[Contact] = []
    
    # Métadonnées
    actif: bool = True
    notes: Optional[str] = None
    date_creation: datetime = Field(default_factory=datetime.utcnow)
    date_modification: datetime = Field(default_factory=datetime.utcnow)

class FournisseurCreate(BaseModel):
    code: str
    nom: str
    raison_sociale: Optional[str] = None
    adresse: Optional[str] = None
    ville: Optional[str] = None
    code_postal: Optional[str] = None
    pays: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    site_web: Optional[str] = None
    delai_paiement: Optional[int] = None
    mode_reglement: Optional[str] = None
    devise_principale: Devise = Devise.EUR
    taux_remise: Optional[float] = 0.0
    delai_livraison_standard: Optional[int] = None
    quantite_min_commande: Optional[float] = 0.0
    frais_port: Optional[float] = 0.0
    notes: Optional[str] = None

# Modèle Article
class Article(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reference: str  # Référence unique
    designation: str
    description: Optional[str] = None
    
    # Classification
    famille: Optional[str] = None
    sous_famille: Optional[str] = None
    marque: Optional[str] = None
    
    # Fournisseur principal
    fournisseur_id: str
    reference_fournisseur: Optional[str] = None
    
    # Prix et coûts
    prix_unitaire: float = 0.0
    devise: Devise = Devise.EUR
    prix_derniere_commande: Optional[float] = None
    date_derniere_commande: Optional[datetime] = None
    
    # Gestion des stocks
    stock_actuel: float = 0.0
    stock_minimum: float = 0.0
    stock_maximum: float = 0.0
    stock_securite: float = 0.0
    seuil_alerte: float = 0.0
    
    # Caractéristiques produit
    unite_mesure: str = "unité"
    poids: Optional[float] = None
    volume: Optional[float] = None
    duree_vie: Optional[int] = None  # en jours
    
    # Prévisions et consommation
    consommation_mensuelle: float = 0.0
    consommation_annuelle: float = 0.0
    prevision_prochaine_commande: Optional[date] = None
    quantite_prochaine_commande: Optional[float] = None
    
    # Variantes et composition
    variantes: List[str] = []  # Liste des variantes disponibles
    produit_compose: bool = False
    composants: List[Dict[str, Any]] = []  # [{"article_id": "xxx", "quantite": 2}]
    
    # Métadonnées
    actif: bool = True
    notes: Optional[str] = None
    date_creation: datetime = Field(default_factory=datetime.utcnow)
    date_modification: datetime = Field(default_factory=datetime.utcnow)

class ArticleCreate(BaseModel):
    reference: str
    designation: str
    description: Optional[str] = None
    famille: Optional[str] = None
    sous_famille: Optional[str] = None
    marque: Optional[str] = None
    fournisseur_id: str
    reference_fournisseur: Optional[str] = None
    prix_unitaire: float = 0.0
    devise: Devise = Devise.EUR
    stock_minimum: float = 0.0
    stock_maximum: float = 0.0
    stock_securite: float = 0.0
    seuil_alerte: float = 0.0
    unite_mesure: str = "unité"
    poids: Optional[float] = None
    volume: Optional[float] = None
    duree_vie: Optional[int] = None
    consommation_mensuelle: float = 0.0
    variantes: List[str] = []
    produit_compose: bool = False
    composants: List[Dict[str, Any]] = []
    notes: Optional[str] = None

# Modèle Ligne de Commande
class LigneCommande(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    article_id: str
    reference_article: str
    designation: str
    quantite: float
    prix_unitaire: float
    remise: float = 0.0
    total_ligne: float = 0.0
    date_livraison_souhaitee: Optional[str] = None
    notes: Optional[str] = None

class LigneCommandeCreate(BaseModel):
    article_id: str
    quantite: float
    prix_unitaire: Optional[float] = None
    remise: float = 0.0
    date_livraison_souhaitee: Optional[date] = None
    notes: Optional[str] = None

# Modèle Commande
class Commande(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    numero: str  # Numéro unique de commande
    
    # Fournisseur
    fournisseur_id: str
    nom_fournisseur: str
    
    # Dates
    date_commande: str
    date_livraison_prevue: Optional[str] = None
    date_livraison_reelle: Optional[str] = None
    
    # État et suivi
    etat: str = "brouillon"
    priorite: str = "normale"  # haute, normale, basse
    
    # Conditions commerciales
    devise: str = "EUR"
    incoterm: Optional[str] = None
    mode_transport: Optional[str] = None
    
    # Montants
    montant_ht: float = 0.0
    taux_tva: float = 20.0
    montant_tva: float = 0.0
    montant_ttc: float = 0.0
    frais_port: float = 0.0
    remise_globale: float = 0.0
    
    # Lignes de commande
    lignes: List[LigneCommande] = []
    
    # Suivi et validation
    validee_par: Optional[str] = None
    date_validation: Optional[datetime] = None
    numero_bon_livraison: Optional[str] = None
    numero_facture: Optional[str] = None
    
    # Notes et commentaires
    notes: Optional[str] = None
    commentaires_internes: Optional[str] = None
    
    # Métadonnées
    creee_par: str
    date_creation: datetime = Field(default_factory=datetime.utcnow)
    date_modification: datetime = Field(default_factory=datetime.utcnow)

class CommandeCreate(BaseModel):
    fournisseur_id: str
    date_commande: date
    date_livraison_prevue: Optional[date] = None
    priorite: str = "normale"
    devise: Devise = Devise.EUR
    incoterm: Optional[str] = None
    mode_transport: Optional[ModeTransport] = None
    taux_tva: float = 20.0
    frais_port: float = 0.0
    remise_globale: float = 0.0
    lignes: List[LigneCommandeCreate] = []
    notes: Optional[str] = None
    commentaires_internes: Optional[str] = None
    creee_par: str

# Modèle Stock
class Stock(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    article_id: str
    
    # Quantités
    quantite_physique: float = 0.0
    quantite_reservee: float = 0.0
    quantite_disponible: float = 0.0
    quantite_en_commande: float = 0.0
    
    # Seuils
    seuil_minimum: float = 0.0
    seuil_maximum: float = 0.0
    seuil_securite: float = 0.0
    seuil_alerte: float = 0.0
    
    # Prévisions
    consommation_jour: float = 0.0
    consommation_semaine: float = 0.0
    consommation_mois: float = 0.0
    prevision_3_mois: float = 0.0
    prevision_6_mois: float = 0.0
    prevision_12_mois: float = 0.0
    
    # Calculs automatiques
    couverture_jours: Optional[int] = None  # Nombre de jours de couverture
    date_rupture_prevue: Optional[date] = None
    quantite_a_commander: Optional[float] = None
    date_prochaine_commande: Optional[date] = None
    
    # Dernière mise à jour
    date_derniere_maj: datetime = Field(default_factory=datetime.utcnow)

class StockUpdate(BaseModel):
    quantite_physique: Optional[float] = None
    quantite_reservee: Optional[float] = None
    seuil_minimum: Optional[float] = None
    seuil_maximum: Optional[float] = None
    seuil_securite: Optional[float] = None
    seuil_alerte: Optional[float] = None

# Modèle Alerte
class Alerte(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    titre: str
    message: str
    type: TypeAlerte
    statut: StatutAlerte = StatutAlerte.ACTIVE
    
    # Contexte
    article_id: Optional[str] = None
    commande_id: Optional[str] = None
    fournisseur_id: Optional[str] = None
    
    # Données contextuelles
    valeur_actuelle: Optional[float] = None
    valeur_seuil: Optional[float] = None
    pourcentage_ecart: Optional[float] = None
    
    # Dates
    date_creation: datetime = Field(default_factory=datetime.utcnow)
    date_traitement: Optional[datetime] = None
    date_expiration: Optional[datetime] = None
    
    # Actions
    traitee_par: Optional[str] = None
    actions_prises: Optional[str] = None

class AlerteCreate(BaseModel):
    titre: str
    message: str
    type: TypeAlerte
    article_id: Optional[str] = None
    commande_id: Optional[str] = None
    fournisseur_id: Optional[str] = None
    valeur_actuelle: Optional[float] = None
    valeur_seuil: Optional[float] = None
    date_expiration: Optional[datetime] = None

# Modèles pour les réponses et statistiques
class StatistiquesDashboard(BaseModel):
    # Stocks
    nb_articles_total: int = 0
    nb_articles_alerte: int = 0
    nb_articles_rupture: int = 0
    valeur_stock_total: float = 0.0
    
    # Commandes
    nb_commandes_en_cours: int = 0
    nb_commandes_retard: int = 0
    montant_commandes_mois: float = 0.0
    
    # Fournisseurs
    nb_fournisseurs_actifs: int = 0
    
    # Alertes
    nb_alertes_critiques: int = 0
    nb_alertes_importantes: int = 0
    
    # Dates de mise à jour
    derniere_maj: datetime = Field(default_factory=datetime.utcnow)

class RapportPerformance(BaseModel):
    periode_debut: date
    periode_fin: date
    
    # Métriques clés
    taux_service_client: float = 0.0
    delai_moyen_livraison: float = 0.0
    nb_commandes_traitees: int = 0
    nb_commandes_retard: int = 0
    
    # Évolution des stocks
    rotation_stock: float = 0.0
    couverture_moyenne: float = 0.0
    
    # Performance fournisseurs
    nb_fournisseurs_evalues: int = 0
    note_moyenne_fournisseurs: float = 0.0
    
    date_generation: datetime = Field(default_factory=datetime.utcnow)