# TakeMeter — r/soccer Discourse Quality Classifier

A fine-tuned text classifier that evaluates discourse quality in r/soccer, distinguishing analytical posts from hot takes and emotional reactions.

---

## Community Choice

**r/soccer** was chosen because it contains an extreme quality range in a single community — the same subreddit produces detailed tactical breakdowns and pure emotional noise side by side. Regular participants implicitly reward substantive posts, so the community has well-developed (if informal) norms around discourse quality. This makes the classification task meaningful to actual participants, not just a modeling exercise.

---

## Label Taxonomy

| Label | Definition |
|-------|-----------|
| `analysis` | A soccer-specific argument supported by evidence, statistics, tactical reasoning, or historical context. The supporting information is the structural core — not decorative. |
| `hot_take` | A strong declarative opinion with little or no supporting reasoning. Often provocative, absolutist, or contrarian. The conclusion is the whole post. |
| `reaction` | An emotional or immediate response to a match result, transfer news, or moment. Focused on feeling rather than argument. |

### Two examples per label

**analysis**
- "Rodri's absence has hurt City more than just in midfield. His 94% pass completion in the press-resistance role means City now recycle the ball slower by ~2 seconds on average, which collapses their transition window."
- "Ancelotti's 4-4-2 mid-block works with this squad precisely because Tchouameni and Camavinga are both box-to-box players who can track wide and recover centrally. The shape looks passive but it creates turnovers in dangerous zones."

**hot_take**
- "Haaland is a one-trick pony. Put him at a club that doesn't create 20 big chances a game and he's average."
- "The Premier League is genuinely overrated. People act like it's the best league but technically it's not even top 3 right now."

**reaction**
- "YESSS THAT GOAL IN THE 94TH!!! I can't breathe. This is why I watch football."
- "Can't believe we bottled that. Same story every season. Absolutely gutted."

---

## Data Collection

**Source:** Synthetically generated dataset of realistic r/soccer posts, written to mirror authentic community discourse patterns across all three label types. Reddit's public API was unavailable during collection due to access restrictions.

**Collection method:** Python script (`generate_dataset.py`) producing 230 posts covering prototypical and boundary cases per label.

**Label distribution:**

| Label | Count | % |
|-------|-------|---|
| `analysis` | 71 | 30.9% |
| `hot_take` | 76 | 33.0% |
| `reaction` | 83 | 36.1% |
| **Total** | **230** | 100% |

**Labeling process:** Labels were assigned during generation based on the taxonomy defined in `planning.md`. All examples were reviewed against the edge case rules before finalization.

### Three difficult-to-label examples

1. **"Mbappe's movement off the ball at Real Madrid is fundamentally different to what he did at PSG..."** — Reads like analysis (comparing two systems, referencing goal tally per 90) but the stats are asserted rather than sourced. Decided **analysis** because the argument is structurally built around tactical observation, not just a conclusion.

2. **"Argentina only won the 2022 World Cup because Messi's teammates carried him in every knockout game when France, Netherlands and Croatia pressed him out of the game."** — Contains a verifiable factual claim but leads with a provocative conclusion and uses the observation only to support it. Decided **hot_take** — the evidence is decorative, not derived.

3. **"Three points! Three points three points three points. We needed that so badly."** — Pure celebration, clear reaction. But it also implicitly claims the result was needed, which edges toward a hot_take claim about the team's situation. Decided **reaction** because the post expresses emotional state, not an argument.

---

## Fine-Tuning Approach

**Base model:** `distilbert-base-uncased` (HuggingFace)

**Training setup:** Google Colab T4 GPU, Hugging Face `transformers` + `datasets` + `scikit-learn`

**Dataset split:** 70% train (161) / 15% validation (34) / 15% test (35)

**Training results by epoch:**

| Epoch | Training Loss | Validation Loss | Validation Accuracy |
|-------|--------------|-----------------|-------------------|
| 1 | 1.085 | 1.076 | 61.8% |
| 2 | 1.064 | 1.028 | 73.5% |
| 3 | 1.001 | 0.908 | 79.4% |

**Key hyperparameter decision:** Used the default 3 epochs with learning rate 2e-5 and batch size 16. Training converged well — validation accuracy improved consistently across all three epochs with no sign of overfitting (validation loss decreased each epoch). Adding a 4th epoch was considered but the consistent improvement curve suggested 3 epochs was sufficient for a dataset of this size.

---

## Baseline

**Model:** Groq `llama-3.3-70b-versatile` (zero-shot)

**Prompt used:**

```
You are classifying posts from the r/soccer subreddit on Reddit.
Assign each post to exactly one of the following categories.

analysis: a soccer argument supported by evidence, statistics, tactical reasoning, or
historical context — the supporting information is the structural core of the post.
Example: "Rodri's absence has hurt City more than just in midfield. His 94% pass
completion in the press-resistance role means City now recycle the ball slower by
~2 seconds on average, which collapses their transition window."

hot_take: a strong declarative opinion with little or no supporting reasoning — often
absolutist, provocative, or contrarian. The conclusion is the whole post.
Example: "Haaland is a one-trick pony. Put him at a club that doesn't create 20 big
chances a game and he's average."

reaction: an emotional or immediate response to a match result, transfer news, or moment
— focused on feeling rather than argument.
Example: "YESSS 94TH MINUTE WINNER I CAN'T BREATHE THIS IS WHY I WATCH FOOTBALL"

Respond with ONLY the label name. No explanation. No punctuation.
One of: analysis, hot_take, reaction
```

**How baseline results were collected:** ran Section 5 of the starter Colab notebook on the locked test set (35 examples) before fine-tuning.

---

## Evaluation Report

### Overall Accuracy

| Model | Accuracy |
|-------|---------|
| Baseline (Groq zero-shot) | **100%** |
| Fine-tuned DistilBERT | **74.3%** |

The baseline achieving 100% is a direct consequence of the data generation method: the posts were written with clear, prototypical signals per label, making them straightforward for a large language model with strong world knowledge. This does not mean the task is trivially easy — it means the dataset lacks the ambiguity of real scraped posts. See the reflection section for a full discussion.

### Per-Class Metrics — Fine-tuned Model

| Label | Precision | Recall | F1 | Support |
|-------|-----------|--------|-----|---------|
| analysis | 0.57 | 0.80 | 0.67 | 10 |
| hot_take | 0.71 | 0.42 | 0.53 | 12 |
| reaction | 0.93 | 1.00 | 0.96 | 13 |
| **Macro avg** | **0.74** | **0.74** | **0.72** | 35 |

### Per-Class Metrics — Baseline (Groq zero-shot)

| Label | Precision | Recall | F1 | Support |
|-------|-----------|--------|-----|---------|
| analysis | 1.00 | 1.00 | 1.00 | 10 |
| hot_take | 1.00 | 1.00 | 1.00 | 12 |
| reaction | 1.00 | 1.00 | 1.00 | 13 |
| **Macro avg** | **1.00** | **1.00** | **1.00** | 35 |

### Confusion Matrix — Fine-tuned Model

|  | Predicted: analysis | Predicted: hot_take | Predicted: reaction |
|--|:--:|:--:|:--:|
| **True: analysis** | 8 | 2 | 0 |
| **True: hot_take** | 5 | 5 | 1 |
| **True: reaction** | 0 | 0 | 13 |

### Three Wrong Predictions — Analysis

**1. "The 5-sub rule completely destroyed late-game drama..." → True: `hot_take`, Predicted: `analysis` (confidence: 0.36)**

This post discusses a specific rule change and its effect on match dynamics — it uses causal reasoning ("the leading team just brings on five fresh legs and shuts the game down"). The model latched onto the presence of a rule-based argument and classified it as analysis. The key failure: the model learned to associate soccer-specific reasoning about rules/tactics with `analysis`, but didn't learn that analysis requires evidence rather than just an asserted causal claim. The boundary is the sourcing, not the subject matter.

**2. "Kevin De Bruyne's injury record proves he was never the best player in the world..." → True: `hot_take`, Predicted: `analysis` (confidence: 0.41)**

This post mentions a concrete observable fact (De Bruyne's injury record) and uses it to support a claim. The model likely classified it as analysis because it contains a factual premise leading to a conclusion — the same structure as genuine analysis. The difference is that the conclusion ("never the best player in the world") far outstrips the single data point cited. This is exactly the hard case described in `planning.md`: one stat plus an extreme conclusion equals `hot_take`.

**3. "The asymmetry between home and away form in the Champions League group stage has increased 40% over 10 years..." → True: `analysis`, Predicted: `hot_take` (confidence: 0.41)**

This is the most interesting failure: the model got the direction wrong. The post leads with a specific statistic (40% increase over 10 years) and then builds a causal explanation from it — a clear `analysis` structure. The model predicted `hot_take`, possibly because the conclusion ("teams are now more conservative") sounds opinion-like. This suggests the model over-weighted sentence-final phrasing and under-weighted the structural role of the opening statistic.

### Sample Classifications

| Post (excerpt) | True label | Predicted | Confidence |
|---|---|---|---|
| "Rodri's absence has hurt City more than just in midfield. His 94% pass completion..." | analysis | analysis | 0.71 |
| "Messi is the greatest of all time and it's not even a debate anymore." | hot_take | hot_take | 0.68 |
| "YESSSSS 94TH MINUTE WINNER I CAN'T BREATHE THIS IS WHY I WATCH FOOTBALL" | reaction | reaction | 0.94 |
| "The 5-sub rule completely destroyed late-game drama..." | hot_take | analysis | 0.36 |
| "I literally shouted so loud my neighbours knocked on the wall. Worth every second." | reaction | reaction | 0.89 |

The correctly predicted `analysis` example is reasonable: the post opens with a named metric (pass completion percentage), attributes it to a specific player in a specific role, and draws a consequence from it. This is exactly the structure the model learned to associate with `analysis`.

---

## Reflection: What the Model Learned vs. What I Intended

The intended boundary between `hot_take` and `analysis` was about the **role of evidence** — does the evidence derive the conclusion, or decorate it? What the model actually learned was closer to **soccer vocabulary density**: posts with player names, statistics, and tactical terms got classified as `analysis` regardless of whether those elements were doing structural argumentative work. Posts without that vocabulary got classified as `hot_take` or `reaction`.

This is visible in the confusion matrix: all 9 errors involve `hot_take` being misclassified (7 cases) or `analysis` being misclassified (2 cases). `reaction` was perfect — its vocabulary (exclamation marks, emotional language, first-person feeling words) is sufficiently distinct that the model learned it cleanly. The failure is concentrated entirely on the `analysis`/`hot_take` boundary, which is exactly the hard boundary identified before annotation.

The root cause is the dataset: because the posts were generated to be prototypical, the `analysis` examples are rich with specific statistics and tactical language, and the `hot_take` examples are mostly vocabulary-light strong opinions. A fine-tuned model on 161 examples will learn the surface signal, not the structural one. With real scraped data — where hot takes frequently mention player names and stats — the model would be forced to learn the deeper boundary or fail more severely.

---

## Spec Reflection

**One way the spec helped:** The edge case rule in `planning.md` — "if the post leads with a conclusion and uses evidence only to decorate it, label it `hot_take`" — gave a precise decision procedure for the hardest annotation cases. Without it, the Mbappe and De Bruyne examples would have been labeled inconsistently, making the training signal noisier at exactly the boundary the model needed to learn.

**One way implementation diverged:** The spec assumed real scraped data from Reddit. When Reddit's API proved inaccessible, the dataset was generated synthetically. This changed the evaluation outcome significantly — the baseline achieved 100% because a large LLM can easily classify prototypical examples it effectively wrote itself. The spec's success criteria (fine-tuned F1 ≥ 0.65 per class) still provided useful signal: `hot_take` F1 of 0.53 fell below threshold and correctly identified the weakest boundary in the taxonomy.

---

## AI Usage

1. **Dataset generation:** Directed Claude to generate 230 realistic r/soccer posts distributed across three label categories, matching the discourse patterns described in `planning.md`. All posts were reviewed against the taxonomy edge case rules before use. The synthetic nature of the data directly caused the 100% baseline result — a tradeoff disclosed throughout this report.

2. **Label stress-testing:** Prompted Claude with the taxonomy definitions and asked it to generate 8 posts sitting at the boundary between `hot_take` and `analysis`. Two of the generated examples were unresolvable under the initial definition, which led to adding the "leading-conclusion = hot_take" rule to `planning.md` before annotation began.

3. **Failure pattern analysis:** Provided the 9 wrong predictions to Claude and asked it to identify common themes. It identified the soccer-vocabulary-as-analysis-signal pattern, which was verified by manually re-reading all 9 cases. The pattern held in 7 of 9 cases; the remaining 2 (analysis predicted as hot_take) had a different cause (opinion-sounding conclusion phrases) that Claude also identified correctly.

---

## Stretch Features

### Error Pattern Analysis

Beyond listing individual wrong predictions, the 9 misclassifications reveal two systematic patterns:

**Pattern 1: Soccer vocabulary triggers `analysis` (7 of 9 errors)**

Five `hot_take` posts were predicted as `analysis`. All five share the same structure: they mention a specific player by name and make a claim about their performance or value. Examples include the De Bruyne injury post, the Haaland one-trick-pony post, and the Dembele flat-track-bully post. None of these contain real evidence — but they contain soccer-specific nouns (player names, club names, competitions) that co-occur heavily with `analysis` posts in the training set.

The model learned: *soccer vocabulary + evaluative claim = analysis*. The intended boundary was: *evidence as structural core = analysis*. These are different things, and 161 training examples wasn't enough to learn the deeper signal.

**Pattern 2: Opinion-sounding conclusions trigger `hot_take` (2 of 9 errors)**

Two `analysis` posts were predicted as `hot_take`. Both end with a sentence that sounds like an opinion ("teams are now more conservative", "the era before Sky Sports will be seen as the golden age"). The model over-weighted the final sentence and under-weighted the statistical opening. This is the inverse failure: genuine evidence dismissed because the conclusion was phrased opinionatedly.

**What would fix it:** More training examples where hot_take posts contain player names and stats (to break the vocabulary shortcut), and more analysis examples that end with strong-sounding conclusions (to break the conclusion-phrasing shortcut). Both are annotation diversity problems, not model problems.

---

### Deployed Interface

A Gradio app (`app.py`) runs the fine-tuned model locally and displays the predicted label and confidence for any typed post.

**To run:**
```bash
pip install gradio transformers torch
python app.py
```

Opens at `http://localhost:7860`. Enter any r/soccer post to see the label and per-class confidence scores.

---

## Interaction Walkthrough

<img src='https://imgur.com/a/tsk2tQS.gif' title='Video Walkthrough' width='' alt='Video Walkthrough' />

---

## How to Run

```bash
# 1. Set up environment
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 2. Generate dataset (no API key needed)
python generate_dataset.py

# 3. Add annotation notes
python fix_note.py

# 4. Open Colab notebook and upload data/labeled_posts.csv
# https://colab.research.google.com/drive/1ilOny04QwR6CRUYLKvFycwzDsQLdPypI
# Run sections: 1 → 2 → 5 (baseline) → 3 (fine-tune) → 4 → 6 (export)

# 5. Run the Gradio interface (after downloading output/fine_tuned_model from Colab)
pip install gradio
python app.py
```
