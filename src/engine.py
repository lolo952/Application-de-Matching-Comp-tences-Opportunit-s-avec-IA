"""Moteur de recommandation : charge les données une fois, puis classe les offres pour un CV."""
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

from matching import MODEL_NAME, MIN_SCORE, allowed_mask, load_data
from skills_lexicon import extract

ALPHA = 0.1  # poids du score de compétences (voir 05_hybrid_eval.py)


class Engine:
    def __init__(self):
        _, self.jobs = load_data()
        job_sk = pd.read_parquet("data/processed/jobs_skills.parquet").drop_duplicates("job_id")
        job_sk = job_sk.set_index("job_id")["skills_list"]
        self.job_skills = [set(job_sk.get(j, [])) for j in self.jobs["job_id"]]
        df = {}
        for sk in self.job_skills:
            for s in sk:
                df[s] = df.get(s, 0) + 1
        n = len(self.jobs)
        self.idf = {s: float(np.log(n / c)) for s, c in df.items()}
        self.model = SentenceTransformer(MODEL_NAME)
        self.job_emb = np.asarray(self.model.encode(
            self.jobs["text"].tolist(), normalize_embeddings=True, show_progress_bar=False))

    def _skill_score(self, have, need):
        total = sum(self.idf.get(s, 0) for s in need)
        if not need or not total:
            return 0.0
        return sum(self.idf.get(s, 0) for s in need & have) / total

    def recommend(self, cv, k=5):
        """cv : dict avec skills, experience, desired_fields, city, mobility (liste), contracts (liste)."""
        text = f"{cv['skills']}. {cv['desired_fields']}. {cv['experience']}"
        have = set(extract(text))
        emb = np.asarray(self.model.encode([text], normalize_embeddings=True, show_progress_bar=False))[0]
        sem = self.job_emb @ emb
        row = {"city": cv["city"], "mobility": cv["mobility"], "contracts": cv["contracts"]}
        idx = np.where(allowed_mask(row, self.jobs))[0]
        idx = [j for j in idx if sem[j] >= MIN_SCORE]
        scored = []
        for j in idx:
            sk = self._skill_score(have, self.job_skills[j])
            scored.append((float((1 - ALPHA) * sem[j] + ALPHA * sk), float(sem[j]), j))
        scored.sort(reverse=True)
        out = []
        for final, s, j in scored[:k]:
            r = self.jobs.iloc[j]
            out.append({
                "job_id": str(r["job_id"]), "title": r["title"], "role": r["role"],
                "city": r["city"], "work_type": r["work_type"],
                "score": round(final, 3), "semantic_score": round(s, 3),
                "common_skills": sorted(have & self.job_skills[j]),
            })
        return out
