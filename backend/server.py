from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
from enum import Enum


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Create the main app without a prefix
app = FastAPI(title="Outil de Gestion des Approvisionnements", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class UserRole(str, Enum):
    ADMIN = "administrateur"
    MANAGER = "manager"
    USER = "utilisateur"

class CommandeStatus(str, Enum):
    DRAFT = "brouillon"
    PENDING = "en_attente"
    APPROVED = "approuvee"
    ORDERED = "commandee"
    DELIVERED = "livree"
    CANCELLED = "annulee"

class AlerteType(str, Enum):
    STOCK_BAS = "stock_bas"
    RETARD_LIVRAISON = "retard_livraison"
    SEUIL_ATTEINT = "seuil_atteint"
    COMMANDE_URGENTE = "commande_urgente"

class AlertePriorite(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Auth Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    nom: str
    prenom: str
    role: UserRole = UserRole.USER

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nom: Optional[str] = None
    prenom: Optional[str] = None
    role: Optional[UserRole] = None
    active: Optional[bool] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    nom: str
    prenom: str
    role: UserRole
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

# Fournisseur Models
class Contact(BaseModel):
    nom: str
    prenom: str
    telephone: Optional[str] = None
    email: Optional[EmailStr] = None
    poste: Optional[str] = None

class Fournisseur(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nom: str
    code_fournisseur: str
    adresse: str
    ville: str
    code_postal: str
    pays: str
    telephone: Optional[str] = None
    email: Optional[EmailStr] = None
    site_web: Optional[str] = None
    conditions_paiement: Optional[str] = None
    delai_livraison_moyen: Optional[int] = None  # en jours
    contacts: List[Contact] = []
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class FournisseurCreate(BaseModel):
    nom: str
    code_fournisseur: str
    adresse: str
    ville: str
    code_postal: str
    pays: str
    telephone: Optional[str] = None
    email: Optional[EmailStr] = None
    site_web: Optional[str] = None
    conditions_paiement: Optional[str] = None
    delai_livraison_moyen: Optional[int] = None
    contacts: List[Contact] = []

# Article Models
class Article(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reference: str
    nom: str
    description: Optional[str] = None
    famille: Optional[str] = None
    fournisseur_id: str
    prix_unitaire: float
    unite: str  # pièce, kg, litre, etc.
    seuil_min: int = 0
    seuil_max: int = 0
    stock_actuel: int = 0
    duree_vie: Optional[int] = None  # en jours
    emplacement_stockage: Optional[str] = None
    active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ArticleCreate(BaseModel):
    reference: str
    nom: str
    description: Optional[str] = None
    famille: Optional[str] = None
    fournisseur_id: str
    prix_unitaire: float
    unite: str
    seuil_min: int = 0
    seuil_max: int = 0
    stock_actuel: int = 0
    duree_vie: Optional[int] = None
    emplacement_stockage: Optional[str] = None

# Commande Models
class LigneCommande(BaseModel):
    article_id: str
    quantite: int
    prix_unitaire: float
    total: float

class Commande(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    numero_commande: str
    fournisseur_id: str
    status: CommandeStatus = CommandeStatus.DRAFT
    lignes: List[LigneCommande] = []
    total_ht: float = 0.0
    total_ttc: float = 0.0
    taux_tva: float = 20.0
    date_commande: Optional[datetime] = None
    date_livraison_prevue: Optional[datetime] = None
    date_livraison_reelle: Optional[datetime] = None
    notes: Optional[str] = None
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CommandeCreate(BaseModel):
    fournisseur_id: str
    lignes: List[LigneCommande]
    date_livraison_prevue: Optional[datetime] = None
    notes: Optional[str] = None

# Alerte Models
class Alerte(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: AlerteType
    priorite: AlertePriorite
    titre: str
    message: str
    article_id: Optional[str] = None
    commande_id: Optional[str] = None
    fournisseur_id: Optional[str] = None
    lue: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Nouveaux modèles pour la gestion avancée des stocks

class TypeMouvement(str, Enum):
    ENTREE = "entree"
    SORTIE = "sortie"
    AJUSTEMENT = "ajustement"
    TRANSFERT = "transfert"

class MouvementStock(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    article_id: str
    type_mouvement: TypeMouvement
    quantite: int
    stock_avant: int
    stock_apres: int
    date_mouvement: datetime = Field(default_factory=datetime.utcnow)
    commande_id: Optional[str] = None
    reference_document: Optional[str] = None
    commentaire: Optional[str] = None
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PrevisionConsommation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    article_id: str
    semaine: int  # Numéro de semaine (1-52)
    annee: int
    date_debut_semaine: datetime
    date_fin_semaine: datetime
    quantite_prevue: float
    quantite_reelle: Optional[float] = None
    ecart_absolu: Optional[float] = None
    ecart_relatif: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CalculCouverture(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    article_id: str
    date_calcul: datetime = Field(default_factory=datetime.utcnow)
    
    # Paramètres de calcul
    variation_logistique: float = 0.0  # VL
    variation_prevision: float = 0.0   # Vp
    horizon: int = 0                   # H en semaines
    
    # Résultats de calcul
    couverture_minimale_securite: float = 0.0  # CMS
    couverture_maximale_commande: float = 0.0  # CMC
    quantite_maximale_commande: float = 0.0    # QM
    couverture_actuelle: float = 0.0           # Cr
    
    # Dates importantes
    date_besoin: Optional[datetime] = None
    date_arrivee_prevue: Optional[datetime] = None
    
    # Données pour le calcul
    stock_actuel: int = 0
    moyenne_consommation_hebdo: float = 0.0
    duree_vie_produit: int = 0
    delai_acheminement: int = 0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class NiveauAlerte(str, Enum):
    NORMAL = "normal"
    URGENT = "urgent"
    CRITIQUE = "critique"
    A_SUIVRE = "a_suivre"

class AlerteAvancee(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    article_id: str
    commande_id: Optional[str] = None
    niveau_alerte: NiveauAlerte
    type_alerte: str  # "nouvelle_commande" ou "commande_en_cours"
    
    # Calculs d'alerte
    date_besoin: Optional[datetime] = None
    date_observation: datetime = Field(default_factory=datetime.utcnow)
    delai_passation: int = 0
    ecart_jours: Optional[int] = None
    
    # Pour commandes en cours
    couverture_prevue: Optional[float] = None
    couverture_minimale: Optional[float] = None
    pourcentage_variation: Optional[float] = None
    
    message: str
    recommandation: str
    lue: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CompositionTC(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reference_tc: str
    articles: List[Dict[str, Any]]  # [{article_id, quantite_par_tc, taux_remplissage}]
    nombre_conteneurs: int = 0
    quantite_complement: Dict[str, int] = {}  # {article_id: quantite}
    quantite_alignement: Dict[str, int] = {}  # {article_id: quantite}
    date_besoin_groupe: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Fonctions de calcul avancées pour la gestion des stocks

async def calculer_variation_logistique(article_id: str, nb_commandes: int = 5) -> float:
    """
    Calcule la variation logistique (VL)
    VL = Moyenne (Valeur Absolue (Date demandée – Date d'arrivée réelle))
    """
    commandes = await db.commandes.find({
        "lignes.article_id": article_id,
        "date_livraison_prevue": {"$exists": True},
        "date_livraison_reelle": {"$exists": True}
    }).sort("created_at", -1).limit(nb_commandes).to_list(nb_commandes)
    
    if not commandes:
        return 0.0
    
    ecarts = []
    for commande in commandes:
        if commande.get("date_livraison_prevue") and commande.get("date_livraison_reelle"):
            ecart = abs((commande["date_livraison_reelle"] - commande["date_livraison_prevue"]).days)
            ecarts.append(ecart)
    
    return sum(ecarts) / len(ecarts) if ecarts else 0.0

async def calculer_variation_prevision(article_id: str, nb_commandes: int = 5) -> float:
    """
    Calcule la variation de prévision (Vp)
    Vp = Moyenne ((Cp-Cr)/(Cr+da))
    """
    # Récupérer les 5 dernières commandes avec leurs couvertures
    commandes = await db.commandes.find({
        "lignes.article_id": article_id,
        "date_livraison_reelle": {"$exists": True}
    }).sort("created_at", -1).limit(nb_commandes).to_list(nb_commandes)
    
    if not commandes:
        return 0.0
    
    variations = []
    for commande in commandes:
        # Récupérer les calculs de couverture pour cette commande
        calcul = await db.calculs_couverture.find_one({
            "article_id": article_id,
            "date_calcul": {"$lte": commande["date_livraison_reelle"]}
        })
        
        if calcul:
            cp = calcul.get("couverture_prevue", 0)
            cr = calcul.get("couverture_reelle", 0)
            da = calcul.get("delai_acheminement", 1)
            
            if (cr + da) > 0:
                variation = (cp - cr) / (cr + da)
                variations.append(variation)
    
    return sum(variations) / len(variations) if variations else 0.0

async def calculer_couverture_minimale_securite(article_id: str) -> float:
    """
    Calcule la Couverture Minimale de Sécurité (CMS)
    CMS = VL . (1+Vp) + H . Vp, avec un minimum de 6 semaines
    """
    vl = await calculer_variation_logistique(article_id)
    vp = await calculer_variation_prevision(article_id)
    
    # Horizon = estimation basée sur le délai d'acheminement moyen
    article = await db.articles.find_one({"id": article_id})
    if not article:
        return 6.0  # Minimum par défaut
    
    fournisseur = await db.fournisseurs.find_one({"id": article["fournisseur_id"]})
    horizon = (fournisseur.get("delai_livraison_moyen", 14) / 7) if fournisseur else 2  # Convertir en semaines
    
    cms = vl * (1 + vp) + horizon * vp
    return max(cms, 6.0)  # Minimum de 6 semaines

async def calculer_couverture_maximale_commande(article_id: str) -> float:
    """
    Calcule la Couverture Maximale pour la commande (CMC)
    CMC = (Dv-10-Da).(1-Vp)-H.Vp
    """
    article = await db.articles.find_one({"id": article_id})
    if not article:
        return 0.0
    
    dv = article.get("duree_vie", 365)  # Durée de vie en jours
    fournisseur = await db.fournisseurs.find_one({"id": article["fournisseur_id"]})
    da = fournisseur.get("delai_livraison_moyen", 14) if fournisseur else 14  # Délai d'acheminement
    
    vp = await calculer_variation_prevision(article_id)
    horizon = da / 7  # Convertir en semaines
    
    # Convertir en semaines pour le calcul
    dv_semaines = dv / 7
    da_semaines = da / 7
    
    cmc = (dv_semaines - 10/7 - da_semaines) * (1 - vp) - horizon * vp
    return max(cmc, 0.0)

async def calculer_quantite_maximale_commande(article_id: str) -> float:
    """
    Calcule la Quantité Maximale d'une commande (QM)
    QM = CMC - Cr
    """
    cmc = await calculer_couverture_maximale_commande(article_id)
    cr = await calculer_couverture_actuelle(article_id)
    
    return max(cmc - cr, 0.0)

async def calculer_couverture_actuelle(article_id: str) -> float:
    """
    Calcule la couverture actuelle (Cr)
    Cr = Stock à la date indiquée / prévision de consommation à la date indiquée
    """
    article = await db.articles.find_one({"id": article_id})
    if not article:
        return 0.0
    
    stock_actuel = article.get("stock_actuel", 0)
    
    # Calculer la moyenne de consommation hebdomadaire
    moyenne_consommation = await calculer_moyenne_consommation_hebdo(article_id)
    
    if moyenne_consommation > 0:
        return stock_actuel / moyenne_consommation
    return 0.0

async def calculer_moyenne_consommation_hebdo(article_id: str) -> float:
    """
    Calcule la moyenne de consommation hebdomadaire
    """
    # Récupérer les mouvements de sortie des 12 dernières semaines
    date_limite = datetime.utcnow() - timedelta(weeks=12)
    mouvements = await db.mouvements_stock.find({
        "article_id": article_id,
        "type_mouvement": "sortie",
        "date_mouvement": {"$gte": date_limite}
    }).to_list(1000)
    
    if not mouvements:
        return 0.0
    
    total_consommation = sum(abs(m["quantite"]) for m in mouvements)
    return total_consommation / 12

async def calculer_date_besoin(article_id: str) -> Optional[datetime]:
    """
    Calcule la date de besoin
    Date de besoin = Recherche Date (couverture projective = Seuil de sécurité)
    """
    cms = await calculer_couverture_minimale_securite(article_id)
    moyenne_consommation = await calculer_moyenne_consommation_hebdo(article_id)
    
    article = await db.articles.find_one({"id": article_id})
    if not article or moyenne_consommation == 0:
        return None
    
    stock_actuel = article.get("stock_actuel", 0)
    
    # Calculer combien de semaines le stock actuel peut couvrir
    couverture_actuelle = stock_actuel / moyenne_consommation
    
    # Si la couverture actuelle est déjà en dessous du seuil
    if couverture_actuelle <= cms:
        return datetime.utcnow()
    
    # Calculer quand le stock atteindra le seuil de sécurité
    semaines_avant_seuil = couverture_actuelle - cms
    date_besoin = datetime.utcnow() + timedelta(weeks=semaines_avant_seuil)
    
    return date_besoin

async def calculer_niveau_alerte_nouvelle_commande(article_id: str) -> NiveauAlerte:
    """
    Calcule le niveau d'alerte pour une nouvelle commande
    """
    date_besoin = await calculer_date_besoin(article_id)
    if not date_besoin:
        return NiveauAlerte.NORMAL
    
    date_observation = datetime.utcnow()
    
    # Délai de passation par défaut (3 jours)
    delai_passation = 3
    
    # Calculer l'écart en jours
    ecart_jours = (date_besoin - date_observation).days - delai_passation
    
    if ecart_jours > 4:
        return NiveauAlerte.NORMAL
    elif 0 < ecart_jours <= 4:
        return NiveauAlerte.NORMAL
    elif -4 < ecart_jours < 0:
        return NiveauAlerte.URGENT
    else:  # ecart_jours <= -4
        return NiveauAlerte.CRITIQUE

async def calculer_niveau_alerte_commande_en_cours(article_id: str, commande_id: str) -> NiveauAlerte:
    """
    Calcule le niveau d'alerte pour une commande en cours
    """
    cms = await calculer_couverture_minimale_securite(article_id)
    
    # Récupérer la couverture prévue pour cette commande
    calcul = await db.calculs_couverture.find_one({
        "article_id": article_id,
        "commande_id": commande_id
    })
    
    if not calcul:
        return NiveauAlerte.NORMAL
    
    cp = calcul.get("couverture_prevue", 0)
    da = calcul.get("delai_acheminement", 1)
    
    if (cms + da) > 0:
        variation_pourcent = (cp - cms) / (cms + da)
        
        if variation_pourcent > 0.1:  # > 10%
            return NiveauAlerte.NORMAL
        elif 0 < variation_pourcent <= 0.1:  # 0% à 10%
            return NiveauAlerte.A_SUIVRE
        else:  # < 0%
            return NiveauAlerte.URGENT
    
    return NiveauAlerte.NORMAL

async def calculer_composition_tc(articles_ids: List[str]) -> Dict[str, Any]:
    """
    Calcule la composition optimale des TCs (conteneurs)
    """
    if not articles_ids:
        return {}
    
    # Calculer les dates de besoin pour tous les articles
    dates_besoin = {}
    for article_id in articles_ids:
        date_besoin = await calculer_date_besoin(article_id)
        if date_besoin:
            dates_besoin[article_id] = date_besoin
    
    if not dates_besoin:
        return {}
    
    # Date de besoin du groupe = minimum des dates de besoin
    date_besoin_groupe = min(dates_besoin.values())
    
    # Calculer les couvertures et moyennes de consommation
    resultats = {}
    for article_id in articles_ids:
        couverture_actuelle = await calculer_couverture_actuelle(article_id)
        moyenne_consommation = await calculer_moyenne_consommation_hebdo(article_id)
        
        resultats[article_id] = {
            "couverture_actuelle": couverture_actuelle,
            "moyenne_consommation": moyenne_consommation,
            "date_besoin": dates_besoin.get(article_id)
        }
    
    return {
        "date_besoin_groupe": date_besoin_groupe,
        "articles": resultats
    }

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"email": email})
    if user is None:
        raise credentials_exception
    return User(**user)

def require_roles(roles: List[UserRole]):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker

# Authentication Routes
@api_router.post("/auth/register", response_model=User)
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password and create user
    hashed_password = get_password_hash(user_data.password)
    user_dict = user_data.dict()
    user_dict.pop("password")
    user_dict["hashed_password"] = hashed_password
    
    user = User(**user_dict)
    user_dict_to_insert = user.dict()
    user_dict_to_insert["hashed_password"] = hashed_password  # Add hashed_password to the dict before inserting
    await db.users.insert_one(user_dict_to_insert)
    return user

@api_router.post("/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    user = await db.users.find_one({"email": user_credentials.email})
    if not user or not verify_password(user_credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    # Update last login
    await db.users.update_one(
        {"email": user["email"]}, 
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    user_obj = User(**user)
    return {"access_token": access_token, "token_type": "bearer", "user": user_obj}

@api_router.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# Users Management Routes
@api_router.get("/users", response_model=List[User])
async def get_users(
    search: Optional[str] = None,
    sort_by: Optional[str] = "nom",
    sort_order: Optional[str] = "asc",
    role: Optional[UserRole] = None,
    active: Optional[bool] = None,
    limit: Optional[int] = 1000,
    skip: Optional[int] = 0,
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    # Build query
    query = {}
    if active is not None:
        query["active"] = active
    if role:
        query["role"] = role
    
    # Add search functionality
    if search:
        query["$or"] = [
            {"nom": {"$regex": search, "$options": "i"}},
            {"prenom": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]
    
    # Build sort criteria
    sort_direction = 1 if sort_order == "asc" else -1
    sort_criteria = [(sort_by, sort_direction)]
    
    users = await db.users.find(query).sort(sort_criteria).skip(skip).limit(limit).to_list(limit)
    return [User(**u) for u in users]

@api_router.post("/users", response_model=User)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = pwd_context.hash(user_data.password)
    
    # Create user
    user_dict = user_data.dict(exclude={"password"})
    user = User(**user_dict)
    user_with_password = user.dict()
    user_with_password["hashed_password"] = hashed_password
    
    await db.users.insert_one(user_with_password)
    return user

@api_router.get("/users/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)

@api_router.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    # Check if user exists
    existing_user = await db.users.find_one({"id": user_id})
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check email uniqueness if email is being updated
    if user_data.email and user_data.email != existing_user["email"]:
        email_exists = await db.users.find_one({"email": user_data.email, "id": {"$ne": user_id}})
        if email_exists:
            raise HTTPException(status_code=400, detail="Email already in use")
    
    # Update only provided fields
    update_data = {}
    for field, value in user_data.dict(exclude_unset=True).items():
        update_data[field] = value
    
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await db.users.update_one(
            {"id": user_id},
            {"$set": update_data}
        )
    
    # Return updated user
    updated_user = await db.users.find_one({"id": user_id})
    return User(**updated_user)

@api_router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    # Check if user exists
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent admin from deleting themselves
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    
    # Soft delete - mark as inactive
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"active": False, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "User deleted successfully"}

class PasswordResetRequest(BaseModel):
    new_password: str

@api_router.put("/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: str,
    password_data: PasswordResetRequest,
    current_user: User = Depends(require_roles([UserRole.ADMIN]))
):
    # Check if user exists
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Hash new password
    hashed_password = pwd_context.hash(password_data.new_password)
    
    # Update password
    await db.users.update_one(
        {"id": user_id},
        {"$set": {"hashed_password": hashed_password, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Password reset successfully"}

# Fournisseur Routes
@api_router.post("/fournisseurs", response_model=Fournisseur)
async def create_fournisseur(
    fournisseur_data: FournisseurCreate,
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.MANAGER]))
):
    fournisseur = Fournisseur(**fournisseur_data.dict())
    await db.fournisseurs.insert_one(fournisseur.dict())
    return fournisseur

@api_router.get("/fournisseurs", response_model=List[Fournisseur])
async def get_fournisseurs(
    search: Optional[str] = None,
    sort_by: Optional[str] = "nom",
    sort_order: Optional[str] = "asc",
    ville: Optional[str] = None,
    pays: Optional[str] = None,
    active: Optional[bool] = True,
    limit: Optional[int] = 1000,
    skip: Optional[int] = 0,
    current_user: User = Depends(get_current_user)
):
    # Build query
    query = {}
    if active is not None:
        query["active"] = active
    
    # Add search functionality
    if search:
        query["$or"] = [
            {"nom": {"$regex": search, "$options": "i"}},
            {"code_fournisseur": {"$regex": search, "$options": "i"}},
            {"ville": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}}
        ]
    
    # Add filters
    if ville:
        query["ville"] = {"$regex": ville, "$options": "i"}
    if pays:
        query["pays"] = {"$regex": pays, "$options": "i"}
    
    # Build sort criteria
    sort_direction = 1 if sort_order == "asc" else -1
    sort_criteria = [(sort_by, sort_direction)]
    
    fournisseurs = await db.fournisseurs.find(query).sort(sort_criteria).skip(skip).limit(limit).to_list(limit)
    return [Fournisseur(**f) for f in fournisseurs]

@api_router.get("/fournisseurs/{fournisseur_id}", response_model=Fournisseur)
async def get_fournisseur(
    fournisseur_id: str,
    current_user: User = Depends(get_current_user)
):
    fournisseur = await db.fournisseurs.find_one({"id": fournisseur_id})
    if not fournisseur:
        raise HTTPException(status_code=404, detail="Fournisseur not found")
    return Fournisseur(**fournisseur)

@api_router.put("/fournisseurs/{fournisseur_id}", response_model=Fournisseur)
async def update_fournisseur(
    fournisseur_id: str,
    fournisseur_data: FournisseurCreate,
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.MANAGER]))
):
    updated_data = fournisseur_data.dict()
    updated_data["updated_at"] = datetime.utcnow()
    
    await db.fournisseurs.update_one(
        {"id": fournisseur_id},
        {"$set": updated_data}
    )
    
    fournisseur = await db.fournisseurs.find_one({"id": fournisseur_id})
    if not fournisseur:
        raise HTTPException(status_code=404, detail="Fournisseur not found")
    return Fournisseur(**fournisseur)

# Articles Routes
@api_router.post("/articles", response_model=Article)
async def create_article(
    article_data: ArticleCreate,
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.MANAGER]))
):
    article = Article(**article_data.dict())
    await db.articles.insert_one(article.dict())
    return article

@api_router.get("/articles", response_model=List[Article])
async def get_articles(
    search: Optional[str] = None,
    sort_by: Optional[str] = "nom",
    sort_order: Optional[str] = "asc",
    famille: Optional[str] = None,
    fournisseur_id: Optional[str] = None,
    stock_bas: Optional[bool] = None,
    active: Optional[bool] = True,
    limit: Optional[int] = 1000,
    skip: Optional[int] = 0,
    current_user: User = Depends(get_current_user)
):
    # Build query
    query = {}
    if active is not None:
        query["active"] = active
    
    # Add search functionality
    if search:
        query["$or"] = [
            {"nom": {"$regex": search, "$options": "i"}},
            {"reference": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
            {"famille": {"$regex": search, "$options": "i"}}
        ]
    
    # Add filters
    if famille:
        query["famille"] = {"$regex": famille, "$options": "i"}
    if fournisseur_id:
        query["fournisseur_id"] = fournisseur_id
    if stock_bas:
        query["$expr"] = {"$lte": ["$stock_actuel", "$seuil_min"]}
    
    # Build sort criteria
    sort_direction = 1 if sort_order == "asc" else -1
    sort_criteria = [(sort_by, sort_direction)]
    
    articles = await db.articles.find(query).sort(sort_criteria).skip(skip).limit(limit).to_list(limit)
    return [Article(**a) for a in articles]

@api_router.get("/articles/stock-bas")
async def get_articles_stock_bas(
    current_user: User = Depends(get_current_user)
):
    articles = await db.articles.find({
        "active": True,
        "$expr": {"$lte": ["$stock_actuel", "$seuil_min"]}
    }).to_list(1000)
    return [Article(**a) for a in articles]

# Commandes Routes
@api_router.post("/commandes", response_model=Commande)
async def create_commande(
    commande_data: CommandeCreate,
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.MANAGER]))
):
    # Calculate totals
    total_ht = sum(ligne.total for ligne in commande_data.lignes)
    total_ttc = total_ht * 1.2  # 20% TVA
    
    commande_dict = commande_data.dict()
    commande_dict.update({
        "numero_commande": f"CMD-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}",
        "total_ht": total_ht,
        "total_ttc": total_ttc,
        "created_by": current_user.id
    })
    
    commande = Commande(**commande_dict)
    await db.commandes.insert_one(commande.dict())
    return commande

@api_router.get("/commandes", response_model=List[Commande])
async def get_commandes(
    search: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "desc",
    status: Optional[CommandeStatus] = None,
    fournisseur_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: Optional[int] = 1000,
    skip: Optional[int] = 0,
    current_user: User = Depends(get_current_user)
):
    # Build query
    query = {}
    
    # Add search functionality
    if search:
        query["$or"] = [
            {"numero_commande": {"$regex": search, "$options": "i"}},
            {"notes": {"$regex": search, "$options": "i"}}
        ]
    
    # Add filters
    if status:
        query["status"] = status
    if fournisseur_id:
        query["fournisseur_id"] = fournisseur_id
    
    # Date range filter
    if date_from or date_to:
        date_query = {}
        if date_from:
            date_query["$gte"] = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
        if date_to:
            date_query["$lte"] = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
        query["created_at"] = date_query
    
    # Build sort criteria
    sort_direction = 1 if sort_order == "asc" else -1
    sort_criteria = [(sort_by, sort_direction)]
    
    commandes = await db.commandes.find(query).sort(sort_criteria).skip(skip).limit(limit).to_list(limit)
    return [Commande(**c) for c in commandes]

# Alertes Routes
@api_router.get("/alertes", response_model=List[Alerte])
async def get_alertes(
    lue: Optional[bool] = None,
    current_user: User = Depends(get_current_user)
):
    query = {}
    if lue is not None:
        query["lue"] = lue
    
    alertes = await db.alertes.find(query).sort("created_at", -1).to_list(100)
    return [Alerte(**a) for a in alertes]

@api_router.post("/alertes/test-create", response_model=Alerte)
async def create_test_alerte(
    alerte_data: dict,
    current_user: User = Depends(get_current_user)
):
    alerte = Alerte(
        type=alerte_data.get("type", "stock_bas"),
        priorite=alerte_data.get("priorite", "high"),
        titre=alerte_data.get("titre", "Test Alert"),
        message=alerte_data.get("message", "This is a test alert"),
        article_id=alerte_data.get("article_id"),
        commande_id=alerte_data.get("commande_id"),
        fournisseur_id=alerte_data.get("fournisseur_id"),
        lue=alerte_data.get("lue", False)
    )
    await db.alertes.insert_one(alerte.dict())
    return alerte

@api_router.put("/alertes/{alerte_id}/marquer-lue")
async def marquer_alerte_lue(
    alerte_id: str,
    current_user: User = Depends(get_current_user)
):
    await db.alertes.update_one(
        {"id": alerte_id},
        {"$set": {"lue": True}}
    )
    return {"message": "Alerte marquée comme lue"}

# Reporting Routes
@api_router.get("/reports/fournisseurs")
async def get_fournisseurs_report(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    pipeline = [
        {"$match": {"active": True}},
        {
            "$lookup": {
                "from": "articles",
                "localField": "id",
                "foreignField": "fournisseur_id",
                "as": "articles"
            }
        },
        {
            "$lookup": {
                "from": "commandes",
                "localField": "id",
                "foreignField": "fournisseur_id",
                "as": "commandes"
            }
        },
        {
            "$addFields": {
                "total_articles": {"$size": "$articles"},
                "total_commandes": {"$size": "$commandes"},
                "valeur_stock": {
                    "$sum": {
                        "$map": {
                            "input": "$articles",
                            "as": "article",
                            "in": {"$multiply": ["$$article.stock_actuel", "$$article.prix_unitaire"]}
                        }
                    }
                }
            }
        },
        {
            "$project": {
                "nom": 1,
                "code_fournisseur": 1,
                "ville": 1,
                "pays": 1,
                "email": 1,
                "telephone": 1,
                "total_articles": 1,
                "total_commandes": 1,
                "valeur_stock": 1,
                "created_at": 1
            }
        }
    ]
    
    # Add date filter if provided
    if date_from or date_to:
        match_stage = pipeline[0]["$match"]
        date_query = {}
        if date_from:
            date_query["$gte"] = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
        if date_to:
            date_query["$lte"] = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
        match_stage["created_at"] = date_query
    
    results = await db.fournisseurs.aggregate(pipeline).to_list(1000)
    return results

@api_router.get("/reports/articles")
async def get_articles_report(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    pipeline = [
        {"$match": {"active": True}},
        {
            "$lookup": {
                "from": "fournisseurs",
                "localField": "fournisseur_id",
                "foreignField": "id",
                "as": "fournisseur"
            }
        },
        {
            "$unwind": {
                "path": "$fournisseur",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$addFields": {
                "fournisseur_nom": "$fournisseur.nom",
                "valeur_stock": {"$multiply": ["$stock_actuel", "$prix_unitaire"]},
                "stock_status": {
                    "$cond": {
                        "if": {"$lte": ["$stock_actuel", "$seuil_min"]},
                        "then": "Critique",
                        "else": {
                            "$cond": {
                                "if": {"$lte": ["$stock_actuel", {"$multiply": ["$seuil_min", 1.5]}]},
                                "then": "Bas",
                                "else": "Normal"
                            }
                        }
                    }
                }
            }
        },
        {
            "$project": {
                "reference": 1,
                "nom": 1,
                "famille": 1,
                "fournisseur_nom": 1,
                "prix_unitaire": 1,
                "unite": 1,
                "seuil_min": 1,
                "seuil_max": 1,
                "stock_actuel": 1,
                "valeur_stock": 1,
                "stock_status": 1,
                "created_at": 1
            }
        }
    ]
    
    # Add date filter if provided
    if date_from or date_to:
        match_stage = pipeline[0]["$match"]
        date_query = {}
        if date_from:
            date_query["$gte"] = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
        if date_to:
            date_query["$lte"] = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
        match_stage["created_at"] = date_query
    
    results = await db.articles.aggregate(pipeline).to_list(1000)
    return results

@api_router.get("/reports/commandes")
async def get_commandes_report(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    pipeline = [
        {
            "$lookup": {
                "from": "fournisseurs",
                "localField": "fournisseur_id",
                "foreignField": "id",
                "as": "fournisseur"
            }
        },
        {
            "$unwind": {
                "path": "$fournisseur",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$lookup": {
                "from": "users",
                "localField": "created_by",
                "foreignField": "id",
                "as": "user"
            }
        },
        {
            "$unwind": {
                "path": "$user",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$addFields": {
                "fournisseur_nom": "$fournisseur.nom",
                "created_by_name": {"$concat": ["$user.prenom", " ", "$user.nom"]},
                "delai_livraison": {
                    "$cond": {
                        "if": {"$and": ["$date_commande", "$date_livraison_reelle"]},
                        "then": {
                            "$divide": [
                                {"$subtract": ["$date_livraison_reelle", "$date_commande"]},
                                86400000
                            ]
                        },
                        "else": None
                    }
                }
            }
        },
        {
            "$project": {
                "numero_commande": 1,
                "fournisseur_nom": 1,
                "status": 1,
                "total_ht": 1,
                "total_ttc": 1,
                "date_commande": 1,
                "date_livraison_prevue": 1,
                "date_livraison_reelle": 1,
                "delai_livraison": 1,
                "created_by_name": 1,
                "created_at": 1,
                "notes": 1
            }
        }
    ]
    
    # Add date filter if provided
    if date_from or date_to:
        date_query = {}
        if date_from:
            date_query["$gte"] = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
        if date_to:
            date_query["$lte"] = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
        pipeline.insert(0, {"$match": {"created_at": date_query}})
    
    results = await db.commandes.aggregate(pipeline).to_list(1000)
    return results

@api_router.get("/reports/synthese")
async def get_synthese_report(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    date_filter = {}
    if date_from or date_to:
        if date_from:
            date_filter["$gte"] = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
        if date_to:
            date_filter["$lte"] = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
    
    # Get basic stats
    stats = {}
    
    # Fournisseurs stats
    fournisseurs_query = {"active": True}
    if date_filter:
        fournisseurs_query["created_at"] = date_filter
    stats["total_fournisseurs"] = await db.fournisseurs.count_documents(fournisseurs_query)
    
    # Articles stats
    articles_query = {"active": True}
    if date_filter:
        articles_query["created_at"] = date_filter
    stats["total_articles"] = await db.articles.count_documents(articles_query)
    
    # Stock bas
    stats["articles_stock_bas"] = await db.articles.count_documents({
        "active": True,
        "$expr": {"$lte": ["$stock_actuel", "$seuil_min"]}
    })
    
    # Commandes stats
    commandes_query = {}
    if date_filter:
        commandes_query["created_at"] = date_filter
    stats["total_commandes"] = await db.commandes.count_documents(commandes_query)
    
    # Valeur totale des commandes
    commandes_pipeline = [
        {"$match": commandes_query},
        {"$group": {"_id": None, "valeur_totale": {"$sum": "$total_ttc"}}}
    ]
    valeur_result = await db.commandes.aggregate(commandes_pipeline).to_list(1)
    stats["valeur_totale_commandes"] = valeur_result[0]["valeur_totale"] if valeur_result else 0
    
    # Commandes par statut
    statut_pipeline = [
        {"$match": commandes_query},
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    stats["commandes_par_statut"] = await db.commandes.aggregate(statut_pipeline).to_list(10)
    
    # Valeur totale du stock
    stock_pipeline = [
        {"$match": {"active": True}},
        {
            "$group": {
                "_id": None,
                "valeur_totale_stock": {
                    "$sum": {"$multiply": ["$stock_actuel", "$prix_unitaire"]}
                }
            }
        }
    ]
    stock_result = await db.articles.aggregate(stock_pipeline).to_list(1)
    stats["valeur_totale_stock"] = stock_result[0]["valeur_totale_stock"] if stock_result else 0
    
    # Alertes non lues
    stats["alertes_non_lues"] = await db.alertes.count_documents({"lue": False})
    
    return stats

# Dashboard Routes
@api_router.get("/dashboard/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user)
):
    total_fournisseurs = await db.fournisseurs.count_documents({"active": True})
    total_articles = await db.articles.count_documents({"active": True})
    total_commandes = await db.commandes.count_documents({})
    alertes_non_lues = await db.alertes.count_documents({"lue": False})
    
    articles_stock_bas = await db.articles.count_documents({
        "active": True,
        "$expr": {"$lte": ["$stock_actuel", "$seuil_min"]}
    })
    
    commandes_en_cours = await db.commandes.count_documents({
        "status": {"$in": [CommandeStatus.PENDING, CommandeStatus.APPROVED, CommandeStatus.ORDERED]}
    })
    
    return {
        "total_fournisseurs": total_fournisseurs,
        "total_articles": total_articles,
        "total_commandes": total_commandes,
        "alertes_non_lues": alertes_non_lues,
        "articles_stock_bas": articles_stock_bas,
        "commandes_en_cours": commandes_en_cours
    }

# Basic routes for backward compatibility
@api_router.get("/")
async def root():
    return {"message": "API Gestion des Approvisionnements"}

# Routes pour la gestion avancée des stocks

@api_router.post("/stock/mouvements", response_model=MouvementStock)
async def create_mouvement_stock(
    mouvement_data: dict,
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.MANAGER]))
):
    """Créer un mouvement de stock"""
    mouvement = MouvementStock(
        article_id=mouvement_data["article_id"],
        type_mouvement=mouvement_data["type_mouvement"],
        quantite=mouvement_data["quantite"],
        stock_avant=mouvement_data["stock_avant"],
        stock_apres=mouvement_data["stock_apres"],
        commande_id=mouvement_data.get("commande_id"),
        reference_document=mouvement_data.get("reference_document"),
        commentaire=mouvement_data.get("commentaire"),
        created_by=current_user.id
    )
    await db.mouvements_stock.insert_one(mouvement.dict())
    return mouvement

@api_router.get("/stock/mouvements/{article_id}")
async def get_mouvements_stock(
    article_id: str,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Récupérer l'historique des mouvements d'un article"""
    mouvements = await db.mouvements_stock.find(
        {"article_id": article_id}
    ).sort("date_mouvement", -1).limit(limit).to_list(limit)
    return [MouvementStock(**m) for m in mouvements]

@api_router.get("/stock/couverture/{article_id}")
async def get_calcul_couverture(
    article_id: str,
    current_user: User = Depends(get_current_user)
):
    """Calculer et retourner les métriques de couverture pour un article"""
    
    # Effectuer tous les calculs
    vl = await calculer_variation_logistique(article_id)
    vp = await calculer_variation_prevision(article_id)
    cms = await calculer_couverture_minimale_securite(article_id)
    cmc = await calculer_couverture_maximale_commande(article_id)
    qm = await calculer_quantite_maximale_commande(article_id)
    cr = await calculer_couverture_actuelle(article_id)
    date_besoin = await calculer_date_besoin(article_id)
    moyenne_consommation = await calculer_moyenne_consommation_hebdo(article_id)
    
    # Récupérer l'article pour les données de base
    article = await db.articles.find_one({"id": article_id})
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    
    fournisseur = await db.fournisseurs.find_one({"id": article["fournisseur_id"]})
    horizon = (fournisseur.get("delai_livraison_moyen", 14) / 7) if fournisseur else 2
    
    # Créer l'objet de calcul
    calcul = CalculCouverture(
        article_id=article_id,
        variation_logistique=vl,
        variation_prevision=vp,
        horizon=int(horizon),
        couverture_minimale_securite=cms,
        couverture_maximale_commande=cmc,
        quantite_maximale_commande=qm,
        couverture_actuelle=cr,
        date_besoin=date_besoin,
        stock_actuel=article.get("stock_actuel", 0),
        moyenne_consommation_hebdo=moyenne_consommation,
        duree_vie_produit=article.get("duree_vie", 365),
        delai_acheminement=fournisseur.get("delai_livraison_moyen", 14) if fournisseur else 14
    )
    
    # Sauvegarder le calcul
    await db.calculs_couverture.insert_one(calcul.dict())
    
    return calcul

@api_router.get("/stock/evolution/{article_id}")
async def get_evolution_stock(
    article_id: str,
    semaines: int = 26,
    current_user: User = Depends(get_current_user)
):
    """
    Récupérer les données d'évolution du stock sur X semaines
    pour le graphique sophisticated
    """
    # Calculer la date de début
    date_debut = datetime.utcnow() - timedelta(weeks=semaines)
    
    # Récupérer les prévisions de consommation
    previsions = await db.previsions_consommation.find({
        "article_id": article_id,
        "date_debut_semaine": {"$gte": date_debut}
    }).sort("date_debut_semaine", 1).to_list(semaines)
    
    # Récupérer les mouvements de stock
    mouvements = await db.mouvements_stock.find({
        "article_id": article_id,
        "date_mouvement": {"$gte": date_debut}
    }).sort("date_mouvement", 1).to_list(1000)
    
    # Calculer l'évolution du stock semaine par semaine
    evolution_data = []
    current_date = date_debut
    
    for i in range(semaines):
        semaine_debut = current_date
        semaine_fin = current_date + timedelta(weeks=1)
        
        # Mouvements de la semaine
        mouvements_semaine = [
            m for m in mouvements
            if semaine_debut <= m["date_mouvement"] < semaine_fin
        ]
        
        # Prévision de la semaine
        prevision_semaine = next(
            (p for p in previsions if p["date_debut_semaine"] == semaine_debut),
            None
        )
        
        # Calculer les métriques de la semaine
        stock_debut = 0  # À calculer selon les mouvements précédents
        stock_fin = stock_debut + sum(
            m["quantite"] if m["type_mouvement"] == "entree" else -m["quantite"]
            for m in mouvements_semaine
        )
        
        evolution_data.append({
            "semaine": i + 1,
            "date_debut": semaine_debut,
            "date_fin": semaine_fin,
            "stock_debut": stock_debut,
            "stock_fin": stock_fin,
            "prevision_consommation": prevision_semaine["quantite_prevue"] if prevision_semaine else 0,
            "consommation_reelle": prevision_semaine["quantite_reelle"] if prevision_semaine else 0,
            "mouvements": len(mouvements_semaine)
        })
        
        current_date = semaine_fin
    
    return {
        "article_id": article_id,
        "periode": f"{semaines} semaines",
        "evolution": evolution_data
    }

@api_router.get("/stock/alertes-avancees")
async def get_alertes_avancees(
    current_user: User = Depends(get_current_user)
):
    """Récupérer toutes les alertes avancées"""
    alertes = await db.alertes_avancees.find({}).sort("created_at", -1).to_list(100)
    return [AlerteAvancee(**a) for a in alertes]

@api_router.post("/stock/generer-alertes")
async def generer_alertes_avancees(
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.MANAGER]))
):
    """Générer les alertes avancées pour tous les articles"""
    # Récupérer tous les articles actifs
    articles = await db.articles.find({"active": True}).to_list(1000)
    
    alertes_generees = []
    
    for article in articles:
        article_id = article["id"]
        
        # Alerte pour nouvelle commande
        niveau_alerte = await calculer_niveau_alerte_nouvelle_commande(article_id)
        date_besoin = await calculer_date_besoin(article_id)
        
        if niveau_alerte in [NiveauAlerte.URGENT, NiveauAlerte.CRITIQUE]:
            alerte = AlerteAvancee(
                article_id=article_id,
                niveau_alerte=niveau_alerte,
                type_alerte="nouvelle_commande",
                date_besoin=date_besoin,
                delai_passation=3,
                ecart_jours=(date_besoin - datetime.utcnow()).days if date_besoin else 0,
                message=f"Commande {niveau_alerte.value} pour {article['nom']}",
                recommandation=f"Passer commande immédiatement" if niveau_alerte == NiveauAlerte.CRITIQUE else "Passer commande rapidement"
            )
            
            await db.alertes_avancees.insert_one(alerte.dict())
            alertes_generees.append(alerte)
        
        # Alertes pour commandes en cours
        commandes_en_cours = await db.commandes.find({
            "lignes.article_id": article_id,
            "status": {"$in": [CommandeStatus.PENDING, CommandeStatus.APPROVED, CommandeStatus.ORDERED]}
        }).to_list(100)
        
        for commande in commandes_en_cours:
            niveau_alerte = await calculer_niveau_alerte_commande_en_cours(article_id, commande["id"])
            
            if niveau_alerte in [NiveauAlerte.URGENT, NiveauAlerte.A_SUIVRE]:
                alerte = AlerteAvancee(
                    article_id=article_id,
                    commande_id=commande["id"],
                    niveau_alerte=niveau_alerte,
                    type_alerte="commande_en_cours",
                    message=f"Commande {niveau_alerte.value} pour {article['nom']}",
                    recommandation=f"Suivre la commande {commande['numero_commande']}"
                )
                
                await db.alertes_avancees.insert_one(alerte.dict())
                alertes_generees.append(alerte)
    
    return {
        "message": f"{len(alertes_generees)} alertes générées",
        "alertes": alertes_generees
    }

@api_router.post("/stock/previsions", response_model=PrevisionConsommation)
async def create_prevision_consommation(
    prevision_data: dict,
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.MANAGER]))
):
    """Créer une prévision de consommation"""
    prevision = PrevisionConsommation(
        article_id=prevision_data["article_id"],
        semaine=prevision_data["semaine"],
        annee=prevision_data["annee"],
        date_debut_semaine=datetime.fromisoformat(prevision_data["date_debut_semaine"]),
        date_fin_semaine=datetime.fromisoformat(prevision_data["date_fin_semaine"]),
        quantite_prevue=prevision_data["quantite_prevue"],
        quantite_reelle=prevision_data.get("quantite_reelle"),
        ecart_absolu=prevision_data.get("ecart_absolu"),
        ecart_relatif=prevision_data.get("ecart_relatif")
    )
    await db.previsions_consommation.insert_one(prevision.dict())
    return prevision

@api_router.get("/stock/previsions/{article_id}")
async def get_previsions_consommation(
    article_id: str,
    semaines: int = 26,
    current_user: User = Depends(get_current_user)
):
    """Récupérer les prévisions de consommation d'un article"""
    date_limite = datetime.utcnow() - timedelta(weeks=semaines)
    
    previsions = await db.previsions_consommation.find({
        "article_id": article_id,
        "date_debut_semaine": {"$gte": date_limite}
    }).sort("date_debut_semaine", 1).to_list(semaines)
    
    return [PrevisionConsommation(**p) for p in previsions]

@api_router.post("/stock/composition-tc")
async def calculer_composition_tc_endpoint(
    data: dict,
    current_user: User = Depends(require_roles([UserRole.ADMIN, UserRole.MANAGER]))
):
    """Calculer la composition optimale des TCs"""
    articles_ids = data.get("articles_ids", [])
    
    if not articles_ids:
        raise HTTPException(status_code=400, detail="Liste d'articles requise")
    
    composition = await calculer_composition_tc(articles_ids)
    
    # Sauvegarder la composition
    composition_tc = CompositionTC(
        reference_tc=f"TC-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8]}",
        articles=articles_ids,
        date_besoin_groupe=composition.get("date_besoin_groupe")
    )
    
    await db.compositions_tc.insert_one(composition_tc.dict())
    
    return {
        "composition_tc": composition_tc,
        "calculs": composition
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
