# StockLens

StockLens is a Django web app that generates AI-assisted stock recommendations from a ticker symbol. It combines recent market news, technical indicators, and quantitative model output, then uses a LangChain/OpenAI agent to return a structured `buy` or `short` recommendation with reasoning.

> This project is for learning and experimentation only. It is not financial advice.

## Features

- User sign-up, sign-in, and sign-out with Django authentication.
- Authenticated home page for entering stock ticker symbols.
- Recent stock news retrieval through Tavily search.
- Technical analysis using Twelve Data:
  - RSI trend and zone classification.
  - 20-day, 50-day, and 200-day moving average comparisons.
  - MACD signal position and crossover detection.
- LSTM next-close prediction using a Hugging Face hosted Keras model and yfinance price data.
- GARCH volatility regime analysis using yfinance historical data.
- LangChain agent response formatted with Pydantic schemas.
- Short-lived recommendation caching with Django's local memory cache.

## Tech Stack

- Python
- Django
- SQLite
- LangChain
- OpenAI
- Tavily
- Twelve Data
- yfinance
- TensorFlow / Keras
- Hugging Face Hub
- arch

## Project Structure

```text
.
|-- requirements.txt
|-- .env
`-- stockrecommendationapp/
    |-- manage.py
    |-- db.sqlite3
    |-- recommendationlogic/
    |   |-- views.py
    |   |-- news_retrieval_logic.py
    |   `-- langchain_logic/
    |       |-- agent_workflow.py
    |       |-- garch_math_model_calculation.py
    |       |-- lstm_math_model_calculation.py
    |       |-- schemas.py
    |       `-- technical_analysis_functions.py
    |-- stockrecommendationapp/
    |   |-- settings.py
    |   |-- urls.py
    |   `-- views.py
    |-- templates/
    |-- users/
    `-- static/
```

## Prerequisites

- Python 3.11+ recommended.
- API keys for:
  - OpenAI
  - Tavily
  - Twelve Data

The first recommendation request may take extra time because the LSTM model, scaler, and metadata are downloaded from Hugging Face Hub.

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the repository root:

```env
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
TWELVE_DATA_API_KEY=your_twelve_data_api_key
KERAS_BACKEND=tensorflow
DJANGO_SECRET_KEY=your_django_secret_key
```

4. Apply database migrations:

```bash
python stockrecommendationapp/manage.py migrate
```

5. Start the development server:

```bash
python stockrecommendationapp/manage.py runserver
```

6. Open the app:

```text
http://127.0.0.1:8000/
```

If you are not signed in, Django redirects you to the sign-in page. Create an account at:

```text
http://127.0.0.1:8000/users/sign-up/
```

## Main Routes

| Route | Description |
| --- | --- |
| `/` | Authenticated home page for ticker input |
| `/recommendationlogic/recommendation/` | POST endpoint that generates a recommendation |
| `/users/sign-up/` | Create a user account |
| `/users/sign-in/` | Sign in |
| `/users/sign-out/` | Sign out |
| `/admin/` | Django admin |

## Running Tests

```bash
python stockrecommendationapp/manage.py test
```

## Notes

- Keep `.env` out of version control. This project already ignores `.env` in `.gitignore`.
- The app uses SQLite by default, with the database stored at `stockrecommendationapp/db.sqlite3`.
- Recommendation results are cached for 5 minutes per ticker symbol.
- The recommendation endpoint calls external APIs and model providers, so a valid internet connection and API quotas are required.
- The current response schema only allows `buy` or `short`, so the app does not currently return `hold`.
