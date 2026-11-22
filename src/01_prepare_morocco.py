import re
import pandas as pd

cv = pd.read_csv("data/raw/morocco_CV_sampled_4.csv")
jobs = pd.read_csv("data/raw/morocco_jobs_sampled_5.csv")


def clean(s):
    return re.sub(r"\s+", " ", str(s)).strip()


# ---------- CV (français) ----------
cv_out = pd.DataFrame({
    "cv_id": cv["Candidate_ID"],
    "city": cv["Lieu_résidence"].map(clean),
    "mobility": cv["Mobilité_géographique"].map(clean),
    "remote_pref": cv["Préférence_télétravail"].map(clean),
    "contracts": cv["Contrats_acceptés"].map(clean),
    "availability": cv["Disponibilité"].map(clean),
    "desired_fields": cv["Types de métiers recherchés"].map(clean),
    "skills": cv["Compétences clés"].map(clean),
    "experience": cv["Expérience professionnelle"].map(clean),
    "languages": cv["Langues"].map(clean),
})
# texte à encoder : compétences d'abord (le plus informatif), puis expérience
cv_out["text"] = cv_out["skills"] + ". " + cv_out["experience"]

# ---------- Offres (anglais) ----------
# Contact, Contact Person, Company Profile et Latitude/Longitude (constantes)
# sont volontairement ignorés
jobs_out = pd.DataFrame({
    "job_id": jobs["Job Id"].astype(str),
    "city": jobs["location"].map(clean),
    "work_type": jobs["Work Type"].map(clean),
    "title": jobs["Job Title"].map(clean),
    "role": jobs["Role"].map(clean),
    "skills": jobs["skills"].map(clean),
    "description": jobs["Job Description"].map(clean),
    "responsibilities": jobs["Responsibilities"].map(clean),
    "experience_req": jobs["Experience"].map(clean),
    "qualification": jobs["Qualifications"].map(clean),
    "salary": jobs["Salary_Numeric"],
})
jobs_out["text"] = (jobs_out["title"] + ". " + jobs_out["role"] + ". "
                    + jobs_out["skills"] + ". " + jobs_out["description"])

# ---------- Contrôles ----------
print("CV :", cv_out.shape, "| doublons texte :", cv_out.duplicated("text").sum())
print("Offres :", jobs_out.shape,
      "| descriptions distinctes :", jobs_out["description"].nunique())
print("Villes communes CV/offres :", sorted(set(cv_out["city"]) & set(jobs_out["city"])))

cv_out.to_parquet("data/processed/cv_morocco.parquet")
jobs_out.to_parquet("data/processed/jobs_morocco.parquet")
print("OK -> data/processed/")
