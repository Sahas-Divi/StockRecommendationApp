import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf
from arch import arch_model

def calculate_garch_math_model(ticker_symbol):
    # 1. Fetch data
    data = yf.download(ticker_symbol, period="2y", multi_level_index=False, auto_adjust=True)
    if data.empty:
        return {"status": "error", "message": f"No data found for ticker {ticker_symbol}"}

    # 2. Calculate daily log returns
    data["Log_Return"] = 100 * np.log(data["Close"] / data["Close"].shift(1))
    data.dropna(inplace=True)

    # 3. Fit GARCH(1,1)
    model = arch_model(data["Log_Return"], vol="Garch", p=1, q=1, dist="StudentsT")
    results = model.fit(disp="off")

    # 4. Extract annualized conditional volatility
    data["Conditional_Volatility"] = results.conditional_volatility * np.sqrt(252)

    # 5. Calculate Volatility Regime
    current_vol = float(data["Conditional_Volatility"].iloc[-1]) # Convert to native Python float
    vol_percentile = float((data["Conditional_Volatility"] < current_vol).mean() * 100)

    if vol_percentile > 80:
        regime_status = "CRITICAL RISK: Volatility is extremely high. Recommend cutting position sizing by half and widening stop losses."
        risk_level = "High"
    elif vol_percentile < 20:
        regime_status = "LOW RISK / COMPRESSED: Volatility is coiled tight. Expect a massive breakout swing soon."
        risk_level = "Low"
    else:
        regime_status = "NORMAL RISK: Standard environment for geometric/technical swing trading setups."
        risk_level = "Normal"

    # 6. Forecast future volatility for a 5-day swing window
    forecast_horizon = 5
    forecasts = results.forecast(horizon=forecast_horizon)
    forecasted_variance = forecasts.variance.iloc[-1]
    forecasted_vol_array = np.sqrt(forecasted_variance) * np.sqrt(252)
    
    # Convert NumPy array into a standard Python list of rounded floats
    five_day_forecast = [round(float(vol), 2) for vol in forecasted_vol_array]

    # --- THE RETURN PAYLOAD ---
    return {
        "status": "success",
        "ticker": ticker_symbol,
        "current_volatility": round(current_vol, 2),
        "volatility_percentile": round(vol_percentile, 1),
        "risk_level": risk_level,
        "recommendation": regime_status,
        "five_day_forecast": five_day_forecast,
        # OPTIONAL: Uncomment the line below if you want to pass recent historical data to plot a chart on your frontend
        # "history": [round(float(v), 2) for v in data["Conditional_Volatility"].tail(30).values]
    }