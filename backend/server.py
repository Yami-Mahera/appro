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
