# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import error_report, fake_apis

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluye las rutas de las APIs de error
app.include_router(error_report.router, prefix="/api")

# Incluye las APIs falsas bajo la ruta /fakeapp
app.include_router(fake_apis.router, prefix="/fakeapp")

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="/app/static"), name="static")
app.mount("/screenshots", StaticFiles(directory="screenshots"), name="screenshots")
