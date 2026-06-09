import os
from dotenv import load_dotenv
from twelvedata import TDClient

load_dotenv()




def calculate_rsi_trend(rsi_values):
    """
    rsi_values should be ordered newest -> oldest.
    Uses the most recent 5 RSI values.
    """

    if len(rsi_values) < 5:
        raise ValueError("Need at least 5 RSI values")

    current_rsi = rsi_values[0]
    rsi_5_days_ago = rsi_values[4]

    slope = (current_rsi - rsi_5_days_ago) / 4

    return slope



def classify_rsi_trend(slope):
    if slope > 1:
        return "strongly_rising"
    elif slope > 0.3:
        return "rising"
    elif slope < -1:
        return "strongly_falling"
    elif slope < -0.3:
        return "falling"
    else:
        return "flat"
    

def classify_rsi_zone(current_rsi, rsi_trend):
    if current_rsi < 30 and rsi_trend == "rising":
        signal = "bullish"

    elif current_rsi > 70 and rsi_trend == "falling":
        signal = "bearish"

    else:
        signal = "neutral"

    return signal


def ma_alignment_classification(ma20, ma50, ma200):
    if ma20 > ma50 > ma200:
        alignment = "bullish"
    elif ma20 < ma50 < ma200:
        alignment = "bearish"
    else:
        alignment = "mixed"

    return alignment