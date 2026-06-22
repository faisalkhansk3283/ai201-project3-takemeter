"""
TakeMeter — Gradio interface for the fine-tuned r/soccer classifier.

Usage:
    pip install gradio transformers torch
    python app.py
"""

import gradio as gr
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_PATH = "output/fine_tuned_model"
LABEL_MAP = {0: "analysis", 1: "hot_take", 2: "reaction"}
DESCRIPTIONS = {
    "analysis": "A soccer argument supported by evidence, statistics, or tactical reasoning.",
    "hot_take": "A strong declarative opinion with little or no supporting reasoning.",
    "reaction": "An emotional response to a match result, transfer news, or moment.",
}

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()


def classify(text):
    if not text.strip():
        return "Please enter a post.", ""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = torch.softmax(logits, dim=1)[0]
    pred_id = probs.argmax().item()
    label = LABEL_MAP[pred_id]
    confidence = probs[pred_id].item()
    all_scores = "\n".join(
        f"  {LABEL_MAP[i]}: {probs[i].item():.2%}" for i in range(3)
    )
    result = f"**{label.upper()}** ({confidence:.0%} confidence)\n\n_{DESCRIPTIONS[label]}_"
    breakdown = f"All scores:\n{all_scores}"
    return result, breakdown


demo = gr.Interface(
    fn=classify,
    inputs=gr.Textbox(lines=4, placeholder="Paste an r/soccer post here...", label="Post"),
    outputs=[
        gr.Markdown(label="Prediction"),
        gr.Textbox(label="Score breakdown"),
    ],
    title="TakeMeter — r/soccer Discourse Classifier",
    description="Classifies r/soccer posts as **analysis**, **hot_take**, or **reaction** using a fine-tuned DistilBERT model.",
    examples=[
        ["Rodri's absence has hurt City more than just in midfield. His 94% pass completion means City recycle the ball slower, which collapses their transition window."],
        ["Haaland is a one-trick pony. Put him at a club that doesn't create 20 big chances a game and he's average."],
        ["YESSSSS 94TH MINUTE WINNER I CAN'T BREATHE THIS IS WHY I WATCH FOOTBALL"],
    ],
)

if __name__ == "__main__":
    demo.launch()
