"""Combine score sémantique + score de compétences communes, et mesure le NDCG@5.

score_final = (1 - alpha) * sémantique + alpha * compétences
compétences = poids des compétences de l'offre présentes dans le CV / poids total des compétences de l'offre
(poids = IDF : une compétence rare compte plus que 'management' ou 'communication').

Évaluation : on reclasse, pour chaque CV annoté, ses 10 offres annotées avec les notes `note_claude`.
"""
import numpy as np
import pandas as pd

from matching import load_data, similarity_matrix

SHEET = "data/processed/annotation_sheet_remplie.xlsx"

cv, jobs = load_data()
sim = similarity_matrix(cv, jobs)

cv_sk = pd.read_parquet("data/processed/cv_skills.parquet").set_index("cv_id")["skills_list"]
job_sk = pd.read_parquet("data/processed/jobs_skills.parquet").drop_duplicates("job_id").set_index("job_id")["skills_list"]

# poids IDF calculés sur les offres
n_jobs = len(jobs)
df = {}
for j in jobs["job_id"]:
    for s in set(job_sk.get(j, [])):
        df[s] = df.get(s, 0) + 1
idf = {s: np.log(n_jobs / c) for s, c in df.items()}


def skill_score(cv_id, job_id):
    need = set(job_sk.get(job_id, []))
    if not need:
        return 0.0
    have = set(cv_sk.get(cv_id, []))
    total = sum(idf.get(s, 0) for s in need)
    return sum(idf.get(s, 0) for s in need & have) / total if total else 0.0


ann = pd.read_excel(SHEET, dtype={"job_id": str})
ann["job_id"] = ann["job_id"].str.lstrip("J")
ann = ann[["cv_id", "job_id", "note_claude"]].rename(columns={"note_claude": "rel"})

cv_pos = {c: i for i, c in enumerate(cv["cv_id"])}
job_pos = {j: i for i, j in enumerate(jobs["job_id"].astype(str))}
ann["sem"] = [sim[cv_pos[c], job_pos[j]] for c, j in zip(ann["cv_id"], ann["job_id"])]
ann["sk"] = [skill_score(c, j) for c, j in zip(ann["cv_id"], ann["job_id"])]


def dcg(rels):
    return sum((2 ** r - 1) / np.log2(i + 2) for i, r in enumerate(rels))


def ndcg5(col):
    out = []
    for _, g in ann.groupby("cv_id"):
        ideal = dcg(sorted(g["rel"], reverse=True)[:5])
        if ideal == 0:
            continue
        out.append(dcg(g.sort_values(col, ascending=False)["rel"].tolist()[:5]) / ideal)
    return np.mean(out), len(out)


print(f"{len(ann)} paires annotées")
print("\nalpha  NDCG@5   (0 = sémantique seul, 1 = compétences seules)")
best = (0, 0)
for a in np.arange(0, 1.01, 0.1):
    ann["final"] = (1 - a) * ann["sem"] + a * ann["sk"]
    v, n = ndcg5("final")
    best = max(best, (v, a))
    print(f"{a:.1f}    {v:.3f}")
print(f"\nMeilleur : alpha = {best[1]:.1f} -> NDCG@5 = {best[0]:.3f} sur {n} CV")
