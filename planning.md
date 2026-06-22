# TakeMeter Planning: r/soccer Discourse Quality Classifier

> Written before data collection (Milestone 2).
> Updated before stretch features if pursued.

---

## Community

**r/soccer** (reddit.com/r/soccer) — one of the largest sports communities on Reddit, with ~4 million members. The subreddit covers all levels of football: Premier League, Champions League, La Liga, international fixtures, and transfer news.

Why it's a good fit: the discourse spans an extreme quality range. On any given day the same subreddit contains a detailed tactical breakdown of a team's pressing structure alongside a comment that says "Messi is done, fight me." This spread makes label boundaries real and non-trivial. Regular participants explicitly reward substantive comments ("quality post") and dismiss low-effort takes, so the community itself has implicit norms that our labels can formalize.

---

## Label Taxonomy

### Labels

| Label | Definition |
|-------|-----------|
| `analysis` | A post or comment that makes a soccer-specific argument supported by evidence, statistics, tactical reasoning, or historical context. The claim is accompanied by supporting information — not just the conclusion. |
| `hot_take` | A strong, declarative opinion stated with confidence but little or no supporting reasoning. Often provocative, absolutist ("X is trash", "Y is the GOAT"), or contrarian. The take is the whole post. |
| `reaction` | An emotional or immediate response to a match result, transfer news, or moment — focused on feeling rather than argument. Includes celebrations, disappointment, and expressions of disbelief. |

**Why 3 labels, not 4:** A fourth label (e.g. "question" or "discussion") was considered but creates an overlap problem — questions often embed hot takes or analysis. Three labels cover ≥90% of r/soccer posts without a catch-all bucket.

### Two examples per label

**analysis**
- "Rodri's absence has hurt City more than just in midfield. His 94% pass completion in the press-resistance role means City now recycle the ball slower by ~2 seconds on average, which collapses their transition window. The data from FBref shows their PPDA (passes allowed per defensive action) has dropped from 8.1 to 11.3 since his injury."
- "People underestimate how Ancelotti's 4-4-2 mid-block works with this squad. Tchouameni and Camavinga cover the halfspaces precisely because neither is a traditional 8 — they're both box-to-box players who can track wide and recover centrally. The shape looks passive but it creates turnovers in dangerous zones."

**hot_take**
- "Haaland is a one-trick pony. Put him at a club that doesn't create 20 big chances a game and he's average."
- "The Premier League is genuinely overrated. People act like it's the best league but technically it's not even top 3 right now."

**reaction**
- "YESSS THAT GOAL IN THE 94TH!!! I can't breathe. This is why I watch football."
- "Can't believe we bottled that. Same story every season. Absolutely gutted."

---

## Hard Edge Cases

**The key ambiguous pair: `hot_take` vs `analysis`**

The hardest cases are posts that include *some* evidence but the conclusion far outstrips it — e.g., one stat cited, then an extreme conclusion drawn. Rule: if the post leads with a conclusion and uses evidence only to decorate it (not to derive it), label it `hot_take`. If the evidence is the structural core of the argument, label it `analysis`.

**Example of the ambiguous middle:**
> "Mbappe's xG per 90 last season was actually 0.4 lower than Lewandowski's. That's why Real bought the wrong striker and will regret it."

One stat → sweeping conclusion. This is `hot_take`. A single supporting data point does not make analysis.

**Rule for `reaction` vs `hot_take`:**
Reaction is about *feeling* — the emotional state of the poster. Hot take is about *claiming something is true*. "This is the worst transfer window ever" is `hot_take` (declarative claim). "I can't believe we just won" is `reaction` (emotional state).

**What to do with short or context-dependent posts:**
If a post is fewer than 15 words and could only be understood in the context of a match thread (e.g., "What a save!!"), label it `reaction` regardless of any slight opinion content. Match thread comments skew reaction by default unless they contain a tactical or statistical claim.

---

## Data Collection Plan

**Source:** r/soccer public posts and comments via Reddit API (PRAW, read-only)

**Target per label:** ~70 examples each (total 210+)

**Collection strategy:**
- Top posts (month): yields high-scoring takes and analysis
- Hot posts: yields reactions from recent match threads
- Top posts (year): yields longer analysis posts
- Match thread comments: primary source of reaction-label examples
- Discussion flair posts + comments: primary source of analysis and hot_take examples

**If a label is underrepresented after 200 examples:**
- For `analysis`: search r/soccer for "tactical", "xG", "formation" — these posts skew analytical
- For `hot_take`: search for "unpopular opinion" posts — extremely reliable
- For `reaction`: match thread comments are an unlimited source

**Label distribution target:** no label below 25% or above 45% of the dataset.

---

## Evaluation Metrics

**Primary: F1-score per class (macro-averaged F1 overall)**

Accuracy alone is insufficient here because:
1. A model that learns to predict only `hot_take` (the easiest label to over-represent) could achieve 40%+ accuracy while being useless for `analysis` and `reaction`.
2. The classes are roughly balanced by design, but any imbalance in annotation will make accuracy misleading.

**Per-class F1** is the right metric because it weights precision and recall equally and surfaces class-specific failure modes. If `analysis` F1 is 0.30 while others are 0.80, the model hasn't learned the analytical boundary — and that's the class that matters most for the stated goal.

**Confusion matrix:** required to identify directional error patterns (which label is being confused for which).

**Baseline:** Groq `llama-3.3-70b-versatile` zero-shot, same test set, same metrics. This answers the question: did fine-tuning actually help?

---

## Definition of Success

**Minimum acceptable:** fine-tuned model exceeds the baseline on macro F1 by at least 0.10, and no per-class F1 is below 0.50.

**Good enough for real use:** per-class F1 ≥ 0.65 for all three labels. At this level, a community moderation tool could reliably surface analysis posts and suppress low-effort content with acceptable false positive rate.

**Red flag:** if fine-tuned F1 is lower than baseline across the board, check for label leakage between train and test splits, or for annotation inconsistency (particularly at the hot_take/analysis boundary).

---

## AI Tool Plan

**Label stress-testing (Milestone 1):**
Prompt: *"Here are my three label definitions for r/soccer posts: [paste taxonomy]. Generate 8 posts that sit at the boundary between hot_take and analysis — posts where a reasonable person could go either way. Don't label them yourself."*
Use output to: test whether my edge case rule (leading-conclusion = hot_take) resolves each case. If 3+ posts feel genuinely unresolvable, tighten the definition before labeling 200 examples.

**Annotation assistance (Milestone 3):**
Pre-label the 200 collected posts using Claude with the taxonomy as context. Prompt:
*"Label each post as exactly one of: analysis, hot_take, reaction. Use these definitions: [taxonomy]. Return only the label, one per line, in the same order."*
Then review every label — don't accept wholesale. Spend extra time on posts the model labeled with low-confidence phrasing or where my gut disagreed.

**Failure analysis (Milestone 6):**
Paste all misclassified examples into Claude: *"Here are posts my classifier got wrong. For each one, the true label is X but the model predicted Y. Identify any common patterns — post length, vocabulary, structure, sarcasm, missing context — that might explain why the model failed."*
Verify each pattern manually by re-reading the examples before writing the evaluation report.

---

## Stretch Features (if time permits)

- [ ] **Inter-annotator reliability**: have a groupmate label 30+ examples, compute Cohen's kappa
- [ ] **Error pattern analysis**: identify systematic confusion beyond listing individual failures
- [ ] **Deployed interface**: Gradio app showing label + confidence for any typed post

---

## Hard Annotation Decisions (filled in during Milestone 3)

*(Document at least 3 genuinely difficult cases here as you label)*

| Post excerpt | Candidate labels | Decision | Reason |
|---|---|---|---|
| TBD | | | |
| TBD | | | |
| TBD | | | |
