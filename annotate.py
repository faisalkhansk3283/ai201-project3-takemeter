"""
TakeMeter annotation helper.
Pre-labels raw_posts.csv using Groq, then saves labeled_posts.csv for your review.

Usage:
    pip install groq pandas
    GROQ_API_KEY=your_key python annotate.py

After running: open data/labeled_posts.csv, review every label, fix any you disagree
with, and fill in the 'notes' column for the 3+ hardest cases (required for README).
"""

import csv
import os
import sys
import time

TAXONOMY = """
You are an annotation assistant for an r/soccer post classifier.

Classify the following post as exactly one of:
- analysis: a soccer argument supported by evidence, statistics, tactical reasoning, or historical context. The supporting information is the structural core of the post.
- hot_take: a strong declarative opinion with little or no supporting reasoning. Often absolutist, provocative, or contrarian. The conclusion is the whole post.
- reaction: an emotional or immediate response to a match, transfer news, or moment. Focused on feeling rather than argument.

Edge case rules:
- If a post has one stat but the conclusion far outstrips it (stat is decorative, not derived), label it hot_take.
- Short match thread comments expressing emotion are reaction even if they contain a mild opinion.
- "This is the worst season ever" = hot_take (declarative claim). "I'm devastated, this is the worst feeling" = reaction (emotional state).

Respond with ONLY the label. No explanation. No punctuation. One of: analysis, hot_take, reaction
""".strip()


def label_post(client, text):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": TAXONOMY},
                {"role": "user", "content": f"Post: {text[:500]}"},
            ],
            max_tokens=10,
            temperature=0,
        )
        raw = response.choices[0].message.content.strip().lower()
        # normalize
        for label in ["analysis", "hot_take", "reaction"]:
            if label in raw:
                return label
        return "unknown"
    except Exception as e:
        print(f"  API error: {e}")
        return "unknown"


def main():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("Set GROQ_API_KEY environment variable first.")
        sys.exit(1)

    from groq import Groq
    client = Groq(api_key=api_key)

    infile = "data/raw_posts.csv"
    outfile = "data/labeled_posts.csv"

    with open(infile, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    print(f"Labeling {len(rows)} posts...")
    labeled = []
    for i, row in enumerate(rows):
        if row.get("label"):  # already labeled, keep it
            labeled.append(row)
            continue
        label = label_post(client, row["text"])
        row["label"] = label
        labeled.append(row)
        if (i + 1) % 20 == 0:
            print(f"  {i+1}/{len(rows)} done")
        time.sleep(0.1)  # light rate limiting

    with open(outfile, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["text", "label", "source", "notes"])
        writer.writeheader()
        writer.writerows(labeled)

    from collections import Counter
    dist = Counter(r["label"] for r in labeled)
    print(f"\nDone. {len(labeled)} posts saved to {outfile}")
    print("Label distribution:")
    for label, count in dist.most_common():
        pct = count / len(labeled) * 100
        print(f"  {label}: {count} ({pct:.1f}%)")
    print("\nNow open data/labeled_posts.csv and review every label before using it.")


if __name__ == "__main__":
    main()
