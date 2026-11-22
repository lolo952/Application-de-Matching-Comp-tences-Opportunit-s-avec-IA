"""Fonctions communes de matching CV <-> offres (utilisées par 02 et 03)."""
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
MIN_SCORE = 0.35  # seuil provisoire : à ajuster avec l'évaluation

# Correspondance des types de contrat (hypothèse à valider avec ta binôme)
CONTRACT_MAP = {
    "CDI": {"Full-Time"},
    "CDD": {"Contract", "Temporary"},
    "Freelance": {"Contract"},
    "Stage": {"Intern"},
}

JOB_COLS = ["job_id", "title", "role", "city", "work_type", "skills"]


def load_data():
    cv = pd.read_parquet("data/processed/cv_morocco.parquet")
    jobs = pd.read_parquet("data/processed/jobs_morocco.parquet")
    # offres identiques (même titre, rôle, ville, contrat) : on n'en garde qu'une
    jobs = jobs.drop_duplicates(["title", "role", "city", "work_type"]).reset_index(drop=True)
    # texte du CV : compétences + métiers recherchés + expérience
    cv["text_match"] = cv["skills"] + ". " + cv["desired_fields"] + ". " + cv["experience"]
    return cv, jobs


def similarity_matrix(cv, jobs):
    model = SentenceTransformer(MODEL_NAME)
    cv_emb = model.encode(cv["text_match"].tolist(), normalize_embeddings=True,
                          show_progress_bar=True)
    job_emb = model.encode(jobs["text"].tolist(), normalize_embeddings=True,
                           show_progress_bar=True)
    return np.asarray(cv_emb) @ np.asarray(job_emb).T  # (nb_CV, nb_offres)


def allowed_mask(row, jobs):
    """Filtre dur : ville (ou mobilité) et type de contrat compatibles."""
    ok = {t for c, ts in CONTRACT_MAP.items() if c in row["contracts"] for t in ts}
    city_ok = (jobs["city"] == row["city"]) | jobs["city"].apply(lambda c: c in row["mobility"])
    return (city_ok & jobs["work_type"].isin(ok)).values


def rank(i, cv, jobs, sim, k=5, min_score=MIN_SCORE):
    """Meilleures offres du CV numéro i (après filtre dur et score minimum)."""
    mask = allowed_mask(cv.iloc[i], jobs)
    idx = np.where(mask)[0]
    idx = idx[np.argsort(-sim[i, idx])]
    idx = [j for j in idx if sim[i, j] >= min_score][:k]
    out = jobs.iloc[idx][JOB_COLS].copy()
    out["score"] = np.round(sim[i, idx], 3)
    return out
