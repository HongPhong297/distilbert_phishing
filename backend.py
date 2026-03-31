"""
backend.py — FastAPI server for phishing detection model.
Run: uvicorn backend:app --host 0.0.0.0 --port 3000
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
from transformers import pipeline, DistilBertForSequenceClassification, DistilBertTokenizerFast

app = FastAPI(title="Phishing Detection API")

MODEL_DIR = "best"

predictor = None


@app.on_event("startup")
def load_model():
    global predictor
    device = 0 if torch.cuda.is_available() else -1
    predictor = pipeline(
        "text-classification",
        model=MODEL_DIR,
        tokenizer=MODEL_DIR,
        truncation=True,
        max_length=512,
        device=device,
    )


class PredictRequest(BaseModel):
    text: str


class PredictResponse(BaseModel):
    label: str
    confidence: float
    is_phishing: bool


@app.get("/")
def root():
    return {"message": "Phishing Detection API", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    result = predictor(request.text)[0]
    label = result["label"]
    confidence = result["score"]

    is_phishing = label == "PHISHING"

    return PredictResponse(
        label=label,
        confidence=round(confidence, 4),
        is_phishing=is_phishing
    )


@app.post("/predict/batch", response_model=list[PredictResponse])
def predict_batch(texts: list[str]):
    if not texts:
        raise HTTPException(status_code=400, detail="Text list cannot be empty")

    if predictor is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    results = predictor(texts)
    return [
        PredictResponse(
            label=r["label"],
            confidence=round(r["score"], 4),
            is_phishing=r["label"] == "PHISHING"
        )
        for r in results
    ]
