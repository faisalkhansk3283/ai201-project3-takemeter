import csv

with open("data/labeled_posts.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

noted = [r for r in rows if r["notes"].strip()]
print(f"{len(noted)} rows have notes")
for r in noted:
    print(f"  [{r['label']}] {r['text'][:70]}...")
