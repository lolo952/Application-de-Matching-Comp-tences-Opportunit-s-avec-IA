"""API FastAPI : POST /match renvoie les meilleures offres pour un CV.

Lancer (depuis la racine du projet) :
    uvicorn api:app --app-dir src --reload
Documentation interactive : http://127.0.0.1:8000/docs
"""
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel, Field

from engine import Engine

state = {}


@asynccontextmanager
async def lifespan(app):
    state["engine"] = Engine()  # chargement unique (~30 s : modèle + embeddings des offres)
    yield
    state.clear()


app = FastAPI(title="Matching Compétences-Opportunités", lifespan=lifespan)


class CVIn(BaseModel):
    skills: str = Field(..., examples=["Python SQL React"])
    experience: str = Field("", examples=["Développeur web, 2 ans"])
    desired_fields: str = Field("", examples=["Informatique"])
    city: str = Field(..., examples=["Casablanca"])
    mobility: List[str] = Field(default_factory=list, examples=[["Rabat"]])
    contracts: List[str] = Field(..., examples=[["CDI", "Stage"]])
    k: int = Field(5, ge=1, le=20)


class JobOut(BaseModel):
    job_id: str
    title: str
    role: str
    city: str
    work_type: str
    score: float
    semantic_score: float
    common_skills: List[str]


@app.get("/health")
def health():
    return {"status": "ok", "jobs": len(state["engine"].jobs)}


@app.post("/match", response_model=List[JobOut])
def match(cv: CVIn):
    return state["engine"].recommend(cv.model_dump(), k=cv.k)
