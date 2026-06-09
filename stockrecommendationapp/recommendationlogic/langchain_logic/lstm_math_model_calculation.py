import os
from huggingface_hub import hf_hub_download
import keras
import joblib
import json
import numpy as np
import pandas as pd
import tensorflow as tf
import yfinance as yf

os.environ["KERAS_BACKEND"] = "tensorflow"


repo_id = "jengyang/lstm-stock-prediction-model"

model_path = hf_hub_download(
    repo_id=repo_id,
    filename="stage2_universal_lstm_20250705_170829.keras"
)

scaler_path = hf_hub_download(
    repo_id=repo_id,
    filename="stage2_scalers_20250705_170829.pkl"
)

metadata_path = hf_hub_download(
    repo_id=repo_id,
    filename="stage2_metadata_20250705_170829.json"
)

model = keras.saving.load_model(model_path, compile=False)

scalers = joblib.load(scaler_path)

with open(metadata_path, "r") as f:
    metadata = json.load(f)

model.summary()
print(metadata)

print("Scaler type:", type(scalers))

if isinstance(scalers, dict):
    print("Scaler keys:", scalers.keys())
else:
    print(scalers)


def calculate_lstm_math_model(ticker_symbol):

    df = yf.download(ticker_symbol, period="6mo", interval="1d", auto_adjust=True)

    # 2. Add '.copy()' to eliminate potential SettingWithCopy warnings
    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()

    # 3. Inject LLM Scores (Using 0.0 as a neutral placeholder for testing)
    # In production, replace this with a dynamic array of your daily LLM news scores (-1 to +1)
    df["Sentiment"] = 0.0

    # 4. Extract trailing sequence window
    latest_60 = df.tail(60).values

    # 5. Fail-Safe: Verify matrix constraints match the LSTM input shape rules
    if latest_60.shape[0] != 60:
        raise ValueError(
            f"Data footprint mismatch. Got {latest_60.shape[0]} rows, but LSTM requires exactly 60 rows."
        )

    # 6. Apply preprocessing scalers
    latest_60_scaled = scalers["feature_scaler"].transform(latest_60)

    # 7. Reshape to 3D Tensor format: (Batch Size, Timesteps, Features)
    X = latest_60_scaled.reshape(1, 60, 6)

    # 8. Inference Execution
    raw_prediction = model.predict(X, verbose=0)  # verbose=0 suppresses console log clutter

    # 9. Invert target back into currency space
    predicted_price = scalers["target_scaler"].inverse_transform(raw_prediction)[0][0]

    return f"Predicted next close price for {ticker_symbol} using LSTM model: ${predicted_price:.2f}"