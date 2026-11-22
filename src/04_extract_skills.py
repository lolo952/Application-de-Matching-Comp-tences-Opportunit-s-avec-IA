"""Extraction des compétences des CV (FR) et des offres (EN) avec un dictionnaire bilingue.

Sortie : data/processed/cv_skills.parquet et jobs_skills.parquet
(colonne `skills_list` : liste de compétences canoniques, ex. ["python", "sql"]).
"""
from collections import Counter

import pandas as pd

from skills_lexicon import extract

cv = pd.read_parquet("data/processed/cv_morocco.parquet")
jobs = pd.read_parquet("data/processed/jobs_morocco.parquet")

# CV : compétences + métiers recherchés + expérience ; offre : titre + rôle + compétences + description
cv["skills_list"] = (cv["skills"] + ". " + cv["desired_fields"] + ". " + cv["experience"]).apply(extract)
jobs["skills_list"] = (jobs["title"] + ". " + jobs["role"] + ". " + jobs["skills"] + ". " + jobs["description"]).apply(extract)

cv[["cv_id", "skills_list"]].to_parquet("data/processed/cv_skills.parquet", index=False)
jobs[["job_id", "skills_list"]].to_parquet("data/processed/jobs_skills.parquet", index=False)

for name, df in [("CV", cv), ("Offres", jobs)]:
    n = df["skills_list"].apply(len)
    print(f"\n=== {name} : {len(df)} lignes ===")
    print(f"Compétences par ligne : moyenne {n.mean():.1f}, médiane {n.median():.0f}")
    print(f"Lignes sans aucune compétence détectée : {(n == 0).sum()} ({(n == 0).mean():.0%})")
    print("Top 15 :", Counter(s for l in df["skills_list"] for s in l).most_common(15))

print("\nExemples de CV :")
for i in range(5):
    print(f"  CV {cv.iloc[i]['cv_id']} -> {cv.iloc[i]['skills_list']}")
print("\nExemples d'offres :")
for i in range(5):
    print(f"  {jobs.iloc[i]['title']} -> {jobs.iloc[i]['skills_list']}")
