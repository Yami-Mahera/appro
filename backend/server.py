from fastapi import FastAPI, APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime, date, timedelta
import uuid

# Import all models
from .models import (
    # Fournisseurs
    Fournisseur, FournisseurCreate, Contact, ContactCreate,
    # Articles
    Article, ArticleCreate,
    # Commandes
    Commande, CommandeCreate, LigneCommande, LigneCommandeCreate,
    # Stocks
    Stock, StockUpdate,
    # Alertes
    Alerte, AlerteCreate,
    # Enums
    EtatCommande, TypeAlerte, StatutAlerte, Devise, ModeTransport,
    # Statistiques
    StatistiquesDashboard, RapportPerformance
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Système de Gestion des Approvisionnements", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ====================================
# ROUTES FOURNISSEURS
# ====================================

@api_router.get("/fournisseurs", response_model=List[Fournisseur])
async def get_fournisseurs(
    actif: Optional[bool] = None,
    search: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000)
):
    """Récupérer la liste des fournisseurs avec filtres optionnels"""
    filter_query = {}
    
    if actif is not None:
        filter_query["actif"] = actif
    
    if search:
        filter_query["$or"] = [
            {"nom": {"$regex": search, "$options": "i"}},
            {"code": {"$regex": search, "$options": "i"}},
            {"raison_sociale": {"$regex": search, "$options": "i"}}
        ]
    
    fournisseurs = await db.fournisseurs.find(filter_query).limit(limit).to_list(limit)
    return [Fournisseur(**f) for f in fournisseurs]

@api_router.post("/fournisseurs", response_model=Fournisseur)
async def create_fournisseur(fournisseur_data: FournisseurCreate):
    """Créer un nouveau fournisseur"""
    # Vérifier l'unicité du code
    existing = await db.fournisseurs.find_one({"code": fournisseur_data.code})
    if existing:
        raise HTTPException(status_code=400, detail="Un fournisseur avec ce code existe déjà")
    
    fournisseur = Fournisseur(**fournisseur_data.dict())
    await db.fournisseurs.insert_one(fournisseur.dict())
    return fournisseur

@api_router.get("/fournisseurs/{fournisseur_id}", response_model=Fournisseur)
async def get_fournisseur(fournisseur_id: str):
    """Récupérer un fournisseur par son ID"""
    fournisseur = await db.fournisseurs.find_one({"id": fournisseur_id})
    if not fournisseur:
        raise HTTPException(status_code=404, detail="Fournisseur non trouvé")
    return Fournisseur(**fournisseur)

@api_router.put("/fournisseurs/{fournisseur_id}", response_model=Fournisseur)
async def update_fournisseur(fournisseur_id: str, fournisseur_data: FournisseurCreate):
    """Mettre à jour un fournisseur"""
    existing = await db.fournisseurs.find_one({"id": fournisseur_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Fournisseur non trouvé")
    
    update_data = fournisseur_data.dict()
    update_data["date_modification"] = datetime.utcnow()
    
    await db.fournisseurs.update_one(
        {"id": fournisseur_id},
        {"$set": update_data}
    )
    
    updated = await db.fournisseurs.find_one({"id": fournisseur_id})
    return Fournisseur(**updated)

@api_router.delete("/fournisseurs/{fournisseur_id}")
async def delete_fournisseur(fournisseur_id: str):
    """Supprimer un fournisseur (désactivation)"""
    result = await db.fournisseurs.update_one(
        {"id": fournisseur_id},
        {"$set": {"actif": False, "date_modification": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Fournisseur non trouvé")
    
    return {"message": "Fournisseur désactivé avec succès"}

# Contacts fournisseurs
@api_router.post("/fournisseurs/{fournisseur_id}/contacts", response_model=Contact)
async def add_contact_fournisseur(fournisseur_id: str, contact_data: ContactCreate):
    """Ajouter un contact à un fournisseur"""
    fournisseur = await db.fournisseurs.find_one({"id": fournisseur_id})
    if not fournisseur:
        raise HTTPException(status_code=404, detail="Fournisseur non trouvé")
    
    contact = Contact(**contact_data.dict())
    
    # Si c'est un contact principal, désactiver les autres contacts principaux
    if contact.principal:
        await db.fournisseurs.update_one(
            {"id": fournisseur_id},
            {"$set": {"contacts.$[].principal": False}}
        )
    
    await db.fournisseurs.update_one(
        {"id": fournisseur_id},
        {"$push": {"contacts": contact.dict()}}
    )
    
    return contact

# ====================================
# ROUTES ARTICLES
# ====================================

@api_router.get("/articles", response_model=List[Article])
async def get_articles(
    actif: Optional[bool] = None,
    famille: Optional[str] = None,
    fournisseur_id: Optional[str] = None,
    alerte_stock: Optional[bool] = None,
    search: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000)
):
    """Récupérer la liste des articles avec filtres"""
    filter_query = {}
    
    if actif is not None:
        filter_query["actif"] = actif
    
    if famille:
        filter_query["famille"] = famille
    
    if fournisseur_id:
        filter_query["fournisseur_id"] = fournisseur_id
    
    if alerte_stock:
        filter_query["$expr"] = {"$lte": ["$stock_actuel", "$seuil_alerte"]}
    
    if search:
        filter_query["$or"] = [
            {"reference": {"$regex": search, "$options": "i"}},
            {"designation": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    articles = await db.articles.find(filter_query).limit(limit).to_list(limit)
    return [Article(**a) for a in articles]

@api_router.post("/articles", response_model=Article)
async def create_article(article_data: ArticleCreate):
    """Créer un nouveau article"""
    # Vérifier l'unicité de la référence
    existing = await db.articles.find_one({"reference": article_data.reference})
    if existing:
        raise HTTPException(status_code=400, detail="Un article avec cette référence existe déjà")
    
    # Vérifier que le fournisseur existe
    fournisseur = await db.fournisseurs.find_one({"id": article_data.fournisseur_id})
    if not fournisseur:
        raise HTTPException(status_code=400, detail="Fournisseur non trouvé")
    
    article = Article(**article_data.dict())
    await db.articles.insert_one(article.dict())
    
    # Créer l'entrée stock correspondante
    stock = Stock(
        article_id=article.id,
        seuil_minimum=article.stock_minimum,
        seuil_maximum=article.stock_maximum,
        seuil_securite=article.stock_securite,
        seuil_alerte=article.seuil_alerte
    )
    await db.stocks.insert_one(stock.dict())
    
    return article

@api_router.get("/articles/{article_id}", response_model=Article)
async def get_article(article_id: str):
    """Récupérer un article par son ID"""
    article = await db.articles.find_one({"id": article_id})
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    return Article(**article)

@api_router.put("/articles/{article_id}", response_model=Article)
async def update_article(article_id: str, article_data: ArticleCreate):
    """Mettre à jour un article"""
    existing = await db.articles.find_one({"id": article_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    
    update_data = article_data.dict()
    update_data["date_modification"] = datetime.utcnow()
    
    await db.articles.update_one(
        {"id": article_id},
        {"$set": update_data}
    )
    
    # Mettre à jour le stock correspondant
    await db.stocks.update_one(
        {"article_id": article_id},
        {"$set": {
            "seuil_minimum": article_data.stock_minimum,
            "seuil_maximum": article_data.stock_maximum,
            "seuil_securite": article_data.stock_securite,
            "seuil_alerte": article_data.seuil_alerte,
            "date_derniere_maj": datetime.utcnow()
        }}
    )
    
    updated = await db.articles.find_one({"id": article_id})
    return Article(**updated)

# ====================================
# ROUTES COMMANDES
# ====================================

@api_router.get("/commandes", response_model=List[Commande])
async def get_commandes(
    etat: Optional[EtatCommande] = None,
    fournisseur_id: Optional[str] = None,
    date_debut: Optional[date] = None,
    date_fin: Optional[date] = None,
    limit: int = Query(100, ge=1, le=1000)
):
    """Récupérer la liste des commandes avec filtres"""
    filter_query = {}
    
    if etat:
        filter_query["etat"] = etat
    
    if fournisseur_id:
        filter_query["fournisseur_id"] = fournisseur_id
    
    if date_debut or date_fin:
        date_filter = {}
        if date_debut:
            date_filter["$gte"] = date_debut
        if date_fin:
            date_filter["$lte"] = date_fin
        filter_query["date_commande"] = date_filter
    
    commandes = await db.commandes.find(filter_query).sort("date_commande", -1).limit(limit).to_list(limit)
    return [Commande(**c) for c in commandes]

@api_router.post("/commandes", response_model=Commande)
async def create_commande(commande_data: CommandeCreate):
    """Créer une nouvelle commande"""
    # Vérifier que le fournisseur existe
    fournisseur = await db.fournisseurs.find_one({"id": commande_data.fournisseur_id})
    if not fournisseur:
        raise HTTPException(status_code=400, detail="Fournisseur non trouvé")
    
    # Générer un numéro de commande unique
    count = await db.commandes.count_documents({})
    numero = f"CMD{datetime.now().year}{count + 1:06d}"
    
    # Traiter les lignes de commande
    lignes_processed = []
    montant_total_ht = 0.0
    
    for ligne_data in commande_data.lignes:
        # Récupérer les informations de l'article
        article = await db.articles.find_one({"id": ligne_data.article_id})
        if not article:
            raise HTTPException(status_code=400, detail=f"Article {ligne_data.article_id} non trouvé")
        
        # Utiliser le prix de l'article si pas fourni
        prix_unitaire = ligne_data.prix_unitaire or article.get("prix_unitaire", 0.0)
        
        # Calculer le total de la ligne
        sous_total = ligne_data.quantite * prix_unitaire
        remise_montant = sous_total * (ligne_data.remise / 100)
        total_ligne = sous_total - remise_montant
        
        ligne = LigneCommande(
            article_id=ligne_data.article_id,
            reference_article=article["reference"],
            designation=article["designation"],
            quantite=ligne_data.quantite,
            prix_unitaire=prix_unitaire,
            remise=ligne_data.remise,
            total_ligne=total_ligne,
            date_livraison_souhaitee=ligne_data.date_livraison_souhaitee,
            notes=ligne_data.notes
        )
        
        lignes_processed.append(ligne)
        montant_total_ht += total_ligne
    
    # Calculer les montants
    remise_globale_montant = montant_total_ht * (commande_data.remise_globale / 100)
    montant_ht_final = montant_total_ht - remise_globale_montant + commande_data.frais_port
    montant_tva = montant_ht_final * (commande_data.taux_tva / 100)
    montant_ttc = montant_ht_final + montant_tva
    
    commande = Commande(
        numero=numero,
        fournisseur_id=commande_data.fournisseur_id,
        nom_fournisseur=fournisseur["nom"],
        date_commande=commande_data.date_commande,
        date_livraison_prevue=commande_data.date_livraison_prevue,
        priorite=commande_data.priorite,
        devise=commande_data.devise,
        incoterm=commande_data.incoterm,
        mode_transport=commande_data.mode_transport,
        montant_ht=montant_ht_final,
        taux_tva=commande_data.taux_tva,
        montant_tva=montant_tva,
        montant_ttc=montant_ttc,
        frais_port=commande_data.frais_port,
        remise_globale=commande_data.remise_globale,
        lignes=lignes_processed,
        notes=commande_data.notes,
        commentaires_internes=commande_data.commentaires_internes,
        creee_par=commande_data.creee_par
    )
    
    await db.commandes.insert_one(commande.dict())
    return commande

@api_router.get("/commandes/{commande_id}", response_model=Commande)
async def get_commande(commande_id: str):
    """Récupérer une commande par son ID"""
    commande = await db.commandes.find_one({"id": commande_id})
    if not commande:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    return Commande(**commande)

@api_router.put("/commandes/{commande_id}/etat")
async def update_etat_commande(commande_id: str, nouvel_etat: EtatCommande):
    """Mettre à jour l'état d'une commande"""
    result = await db.commandes.update_one(
        {"id": commande_id},
        {"$set": {"etat": nouvel_etat, "date_modification": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Commande non trouvée")
    
    return {"message": f"État de la commande mis à jour: {nouvel_etat}"}

# ====================================
# ROUTES STOCKS
# ====================================

@api_router.get("/stocks", response_model=List[Stock])
async def get_stocks(
    alerte: Optional[bool] = None,
    rupture: Optional[bool] = None,
    limit: int = Query(100, ge=1, le=1000)
):
    """Récupérer la liste des stocks avec filtres"""
    filter_query = {}
    
    if alerte:
        filter_query["$expr"] = {"$lte": ["$quantite_disponible", "$seuil_alerte"]}
    
    if rupture:
        filter_query["quantite_disponible"] = {"$lte": 0}
    
    stocks = await db.stocks.find(filter_query).limit(limit).to_list(limit)
    return [Stock(**s) for s in stocks]

@api_router.get("/stocks/{article_id}", response_model=Stock)
async def get_stock_article(article_id: str):
    """Récupérer le stock d'un article"""
    stock = await db.stocks.find_one({"article_id": article_id})
    if not stock:
        raise HTTPException(status_code=404, detail="Stock non trouvé")
    return Stock(**stock)

@api_router.put("/stocks/{article_id}", response_model=Stock)
async def update_stock(article_id: str, stock_data: StockUpdate):
    """Mettre à jour le stock d'un article"""
    existing = await db.stocks.find_one({"article_id": article_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Stock non trouvé")
    
    update_data = {k: v for k, v in stock_data.dict().items() if v is not None}
    update_data["date_derniere_maj"] = datetime.utcnow()
    
    # Recalculer la quantité disponible
    if "quantite_physique" in update_data or "quantite_reservee" in update_data:
        quantite_physique = update_data.get("quantite_physique", existing["quantite_physique"])
        quantite_reservee = update_data.get("quantite_reservee", existing["quantite_reservee"])
        update_data["quantite_disponible"] = quantite_physique - quantite_reservee
    
    await db.stocks.update_one(
        {"article_id": article_id},
        {"$set": update_data}
    )
    
    updated = await db.stocks.find_one({"article_id": article_id})
    return Stock(**updated)

# ====================================
# ROUTES ALERTES
# ====================================

@api_router.get("/alertes", response_model=List[Alerte])
async def get_alertes(
    type: Optional[TypeAlerte] = None,
    statut: Optional[StatutAlerte] = None,
    limit: int = Query(100, ge=1, le=1000)
):
    """Récupérer la liste des alertes"""
    filter_query = {}
    
    if type:
        filter_query["type"] = type
    
    if statut:
        filter_query["statut"] = statut
    
    alertes = await db.alertes.find(filter_query).sort("date_creation", -1).limit(limit).to_list(limit)
    return [Alerte(**a) for a in alertes]

@api_router.post("/alertes", response_model=Alerte)
async def create_alerte(alerte_data: AlerteCreate):
    """Créer une nouvelle alerte"""
    alerte = Alerte(**alerte_data.dict())
    await db.alertes.insert_one(alerte.dict())
    return alerte

@api_router.put("/alertes/{alerte_id}/traiter")
async def traiter_alerte(
    alerte_id: str, 
    actions_prises: str = Query(..., description="Actions prises pour traiter l'alerte"),
    traitee_par: str = Query(..., description="Personne ayant traité l'alerte")
):
    """Marquer une alerte comme traitée"""
    result = await db.alertes.update_one(
        {"id": alerte_id},
        {"$set": {
            "statut": StatutAlerte.TRAITEE,
            "date_traitement": datetime.utcnow(),
            "traitee_par": traitee_par,
            "actions_prises": actions_prises
        }}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")
    
    return {"message": "Alerte traitée avec succès"}

# ====================================
# ROUTES DASHBOARD ET STATISTIQUES
# ====================================

@api_router.get("/dashboard", response_model=StatistiquesDashboard)
async def get_dashboard():
    """Récupérer les statistiques du tableau de bord"""
    # Compter les articles
    nb_articles_total = await db.articles.count_documents({"actif": True})
    
    # Articles en alerte (stock <= seuil_alerte)
    pipeline_alerte = [
        {"$match": {"actif": True}},
        {"$match": {"$expr": {"$lte": ["$stock_actuel", "$seuil_alerte"]}}}
    ]
    nb_articles_alerte = len(await db.articles.aggregate(pipeline_alerte).to_list(None))
    
    # Articles en rupture
    nb_articles_rupture = await db.articles.count_documents({
        "actif": True,
        "stock_actuel": {"$lte": 0}
    })
    
    # Valeur totale du stock
    pipeline_valeur = [
        {"$match": {"actif": True}},
        {"$group": {"_id": None, "total": {"$sum": {"$multiply": ["$stock_actuel", "$prix_unitaire"]}}}}
    ]
    valeur_result = await db.articles.aggregate(pipeline_valeur).to_list(None)
    valeur_stock_total = valeur_result[0]["total"] if valeur_result else 0.0
    
    # Commandes en cours
    nb_commandes_en_cours = await db.commandes.count_documents({
        "etat": {"$in": [EtatCommande.PASSEE, EtatCommande.CONFIRMEE, EtatCommande.PRODUCTION, EtatCommande.EXPEDIEE]}
    })
    
    # Commandes en retard
    today = date.today()
    nb_commandes_retard = await db.commandes.count_documents({
        "date_livraison_prevue": {"$lt": today},
        "etat": {"$nin": [EtatCommande.LIVREE, EtatCommande.FACTUREE, EtatCommande.ANNULEE]}
    })
    
    # Montant des commandes du mois
    debut_mois = date.today().replace(day=1)
    pipeline_montant = [
        {"$match": {"date_commande": {"$gte": debut_mois}}},
        {"$group": {"_id": None, "total": {"$sum": "$montant_ttc"}}}
    ]
    montant_result = await db.commandes.aggregate(pipeline_montant).to_list(None)
    montant_commandes_mois = montant_result[0]["total"] if montant_result else 0.0
    
    # Fournisseurs actifs
    nb_fournisseurs_actifs = await db.fournisseurs.count_documents({"actif": True})
    
    # Alertes
    nb_alertes_critiques = await db.alertes.count_documents({
        "type": TypeAlerte.CRITIQUE,
        "statut": StatutAlerte.ACTIVE
    })
    
    nb_alertes_importantes = await db.alertes.count_documents({
        "type": TypeAlerte.IMPORTANTE,
        "statut": StatutAlerte.ACTIVE
    })
    
    return StatistiquesDashboard(
        nb_articles_total=nb_articles_total,
        nb_articles_alerte=nb_articles_alerte,
        nb_articles_rupture=nb_articles_rupture,
        valeur_stock_total=valeur_stock_total,
        nb_commandes_en_cours=nb_commandes_en_cours,
        nb_commandes_retard=nb_commandes_retard,
        montant_commandes_mois=montant_commandes_mois,
        nb_fournisseurs_actifs=nb_fournisseurs_actifs,
        nb_alertes_critiques=nb_alertes_critiques,
        nb_alertes_importantes=nb_alertes_importantes
    )

# Route de base pour vérification
@api_router.get("/")
async def root():
    return {
        "message": "API Système de Gestion des Approvisionnements",
        "version": "1.0.0",
        "status": "operational"
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

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
