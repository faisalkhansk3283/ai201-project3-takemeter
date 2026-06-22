"""Adds required annotation notes to 3 genuinely ambiguous rows in labeled_posts.csv."""
import csv

NOTES = {
    "Mbappe's movement off the ball at Real Madrid is fundamentally different": (
        "analysis",
        "Hard case: reads like analysis (comparing two systems, referencing goal tally per 90) but there are no actual cited stats — the 'data' is asserted rather than sourced. Decided analysis because the argument is structurally built around tactical observation, not just a conclusion."
    ),
    "Argentina only won the 2022 World Cup because Messi's teammates carried him": (
        "hot_take",
        "Hard case: contains a factual claim (Messi was pressed out by France/Netherlands/Croatia) that could be verified with data, but the post leads with a provocative conclusion and uses the observation only to support it. Decided hot_take — the evidence is decorative, not derived."
    ),
    "Three points! Three points three points three points. We needed that so badly.": (
        "reaction",
        "Hard case: extremely short, pure celebration — clear reaction. But it also implicitly claims the result was needed, which edges toward a hot_take claim about the team's situation. Decided reaction because the post is expressing emotional state, not making an argument."
    ),
}

infile = outfile = "data/labeled_posts.csv"
with open(infile, encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

changed = 0
for row in rows:
    for fragment, (label, note) in NOTES.items():
        if fragment in row["text"] and not row["notes"]:
            row["notes"] = note
            changed += 1

with open(outfile, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["text", "label", "source", "notes"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Done. {changed} rows updated with annotation notes.")
