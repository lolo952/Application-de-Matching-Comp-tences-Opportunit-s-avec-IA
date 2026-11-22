import numpy as np
import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
from matching import load_data, similarity_matrix, rank

N_CV, K = 30, 10  # 30 CV x 10 offres = 300 paires à noter

cv, jobs = load_data()
sim = similarity_matrix(cv, jobs)
rng = np.random.default_rng(42)
chosen = rng.choice(len(cv), size=N_CV, replace=False)

sheet, key = [], []
for i in chosen:
    r = cv.iloc[i]
    top = rank(i, cv, jobs, sim, k=K, min_score=-1).reset_index(drop=True)
    for rk, t in top.iterrows():
        # préfixe "J" : Excel ne doit pas arrondir les identifiants de 16 chiffres
        key.append({"cv_id": r["cv_id"], "job_id": "J" + str(t["job_id"]),
                    "model_rank": rk + 1, "model_score": t["score"]})
    # ordre mélangé dans la feuille pour ne pas influencer les annotatrices
    for _, t in top.sample(frac=1, random_state=42).iterrows():
        sheet.append({
            "cv_id": r["cv_id"], "cv_city": r["city"], "cv_contracts": r["contracts"],
            "cv_skills": r["skills"][:200], "cv_experience": r["experience"][:300],
            "job_id": "J" + str(t["job_id"]), "job_title": t["title"], "job_role": t["role"],
            "job_city": t["city"], "job_work_type": t["work_type"],
            "job_skills": t["skills"][:200],
            "note_moi": "", "note_binome": "",
        })

df = pd.DataFrame(sheet)
out = "data/processed/annotation_sheet.xlsx"
with pd.ExcelWriter(out, engine="openpyxl") as writer:
    df.to_excel(writer, index=False, sheet_name="annotation")
    ws = writer.sheets["annotation"]
    widths = {"cv_id": 8, "cv_city": 12, "cv_contracts": 16, "cv_skills": 40,
              "cv_experience": 60, "job_id": 20, "job_title": 26, "job_role": 26,
              "job_city": 12, "job_work_type": 14, "job_skills": 60,
              "note_moi": 10, "note_binome": 12}
    for n, col in enumerate(df.columns, start=1):
        ws.column_dimensions[ws.cell(1, n).column_letter].width = widths[col]
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
    for c in ws[1]:
        c.font = Font(bold=True)
    for col in ("note_moi", "note_binome"):
        n = list(df.columns).index(col) + 1
        ws.cell(1, n).fill = PatternFill("solid", fgColor="FFF2CC")
    ws.freeze_panes = "A2"
    # liste déroulante 0 / 1 / 2 dans les colonnes de notes
    dv = DataValidation(type="list", formula1='"0,1,2"', allow_blank=True)
    ws.add_data_validation(dv)
    for col in ("note_moi", "note_binome"):
        L = ws.cell(1, list(df.columns).index(col) + 1).column_letter
        dv.add(f"{L}2:{L}{len(df) + 1}")

pd.DataFrame(key).to_csv("data/processed/annotation_model_scores.csv", index=False)
print(f"{len(df)} paires -> {out}")
print("Notes : 0 = non pertinente, 1 = partiellement pertinente, 2 = très pertinente")
