from fastapi import FastAPI

from api.routers import auth, incidents, indicateurs, stations, trajets

app = FastAPI(title="VéloVille")
app.include_router(auth.router)
app.include_router(stations.router)
app.include_router(trajets.router)
app.include_router(incidents.router)
app.include_router(indicateurs.router)
@app.get("/sante")
def health():
    """Confirme que l’API répond."""
    return {"statut": "ok"}