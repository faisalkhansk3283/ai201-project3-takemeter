import csv

infile = outfile = "data/labeled_posts.csv"
with open(infile, encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

note = ("Hard case: reads like analysis (comparing two systems, referencing goal tally per 90) "
        "but there are no actual cited stats - the data is asserted rather than sourced. "
        "Decided analysis because the argument is structurally built around tactical observation, "
        "not just a conclusion.")

for row in rows:
    if "Mbappe" in row["text"] and "Real Madrid" in row["text"] and not row["notes"].strip():
        row["notes"] = note
        print("Patched:", row["text"][:60])

with open(outfile, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["text", "label", "source", "notes"])
    writer.writeheader()
    writer.writerows(rows)

print("Done.")
