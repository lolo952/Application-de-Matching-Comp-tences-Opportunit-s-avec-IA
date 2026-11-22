from matching import load_data, similarity_matrix, rank, allowed_mask, MIN_SCORE

cv, jobs = load_data()
print(f"{len(cv)} CV, {len(jobs)} offres (après dédoublonnage)")
sim = similarity_matrix(cv, jobs)

for i in [0, 1, 2]:
    row = cv.iloc[i]
    pool = int(allowed_mask(row, jobs).sum())
    print(f"\nCV {row['cv_id']} | {row['city']} | {row['contracts']}")
    print("Compétences :", row["skills"][:120])
    print(f"Offres qui passent le filtre ville/contrat : {pool}")
    res = rank(i, cv, jobs, sim)
    if res.empty:
        print(f"Aucune offre au-dessus du score minimum ({MIN_SCORE}).")
    else:
        print(res[["job_id", "title", "role", "city", "work_type", "score"]].to_string(index=False))
