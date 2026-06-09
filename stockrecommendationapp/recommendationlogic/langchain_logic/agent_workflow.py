from langchain.agents import create_agent
import os
from dotenv import load_dotenv
import getpass
from langchain_tavily import TavilySearch
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from .schemas import StockNews
from twelvedata import TDClient
import requests
from .technical_analysis_functions import calculate_rsi_trend, classify_rsi_zone, classify_rsi_trend, ma_alignment_classification


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")

tavily_search_news_tool = TavilySearch(
        max_results=5,
        topic="news",
        time_range="week",
)

llm = ChatOpenAI(
    model="gpt-5-mini",
)

#stock news 

news_agent = create_agent(
        model=llm,
        tools=[tavily_search_news_tool],
        system_prompt="You are a helpful assistant",
        response_format=StockNews,
    )


def get_stock_news(ticker_symbol):

    result = news_agent.invoke({
    "messages": [{"role": "user", "content": f"Give me the latest stock news for the ticker symbol {ticker_symbol} including headlines and a short summary of the article"}]
    })

    structured_data = result["structured_response"]
    return structured_data.news




#technical analysis
twelve_data_api_key = os.getenv("TWELVE_DATA_API_KEY")
td = TDClient(apikey=twelve_data_api_key)

def get_rsi_data(ticker_symbol):
    RSI_response = requests.get(f"https://api.twelvedata.com/rsi?symbol={ticker_symbol}&interval=1day&apikey={twelve_data_api_key}")
    current_RSI = RSI_response.json()["values"][-1]
    rsi_dict = {}

    rsi_values = []
    for i in range(5):
        rsi_values.append(float(RSI_response.json()["values"][i]['rsi']))

    current_RSI = float(RSI_response.json()["values"][0]['rsi'])
    rsi_slope = calculate_rsi_trend(rsi_values)
    rsi_trend = classify_rsi_trend(rsi_slope)
    rsi_zone = classify_rsi_zone(current_rsi=current_RSI, rsi_trend=rsi_trend)

    rsi_dict["current_RSI"] = current_RSI
    rsi_dict["rsi_trend"] = rsi_trend
    rsi_dict["rsi_zone"] = rsi_zone
    

    return rsi_dict

def get_ma_data(ticker_symbol):
    ma_dict = {}

    moving_average_20 = requests.get(f"https://api.twelvedata.com/ma?symbol={ticker_symbol}&interval=1day&time_period=20&apikey={twelve_data_api_key}")
    
    moving_average_50 = requests.get(f"https://api.twelvedata.com/ma?symbol={ticker_symbol}&interval=1day&time_period=50&apikey={twelve_data_api_key}")

    moving_average_200 = requests.get(f"https://api.twelvedata.com/ma?symbol={ticker_symbol}&interval=1day&time_period=200&apikey={twelve_data_api_key}")

    current_price = td.price(symbol=ticker_symbol).as_json()

    ma20 = float(moving_average_20.json()["values"][0]["ma"])
    ma50 = float(moving_average_50.json()["values"][0]["ma"])
    ma200 = float(moving_average_200.json()["values"][0]["ma"])
    price = float(current_price["price"])

    price_above_ma20 = price > ma20
    price_above_ma50 = price > ma50
    price_above_ma200 = price > ma200


    ma_dict["price_above_ma20"]=price_above_ma20
    ma_dict["price_above_ma50"]=price_above_ma50
    ma_dict["price_above_ma200"]=price_above_ma200
    ma_dict["alignment"] = ma_alignment_classification(ma20, ma50, ma200)


    ma20_values = moving_average_20.json()["values"]
    current_ma20 = float(ma20_values[0]["ma"])
    past_ma20 = float(ma20_values[4]["ma"])
    ma20_slope = (current_ma20 - past_ma20) / 4

    ma50_values = moving_average_50.json()["values"]
    current_ma50 = float(ma50_values[0]["ma"])
    past_ma50 = float(ma50_values[4]["ma"])
    ma50_slope = (current_ma50 - past_ma50) / 4

    ma200_values = moving_average_200.json()["values"]
    current_ma200 = float(ma200_values[0]["ma"])
    past_ma200 = float(ma200_values[4]["ma"])
    ma200_slope = (current_ma200 - past_ma200) / 4

    pct_above_ma20 = ((price - ma20) / ma20) * 100
    pct_above_ma50 = ((price - ma50) / ma50) * 100
    pct_above_ma200 = ((price - ma200) / ma200) * 100

    ma50_values = moving_average_50.json()["values"]
    ma200_values = moving_average_200.json()["values"]

    current_ma50 = float(ma50_values[0]["ma"])
    previous_ma50 = float(ma50_values[1]["ma"])

    current_ma200 = float(ma200_values[0]["ma"])
    previous_ma200 = float(ma200_values[1]["ma"])

    golden_cross_today = (
        current_ma50 > current_ma200 and
        previous_ma50 <= previous_ma200
    )

    death_cross_today = (
        current_ma50 < current_ma200 and
        previous_ma50 >= previous_ma200
    )

    ma_dict["pct_above_ma20"] = round(((price - ma20) / ma20) * 100, 2)
    ma_dict["pct_above_ma50"] = round(((price - ma50) / ma50) * 100, 2)
    ma_dict["pct_above_ma200"] = round(((price - ma200) / ma200) * 100, 2)


    ma_dict["ma20_slope"] = round(ma20_slope, 3)
    ma_dict["ma50_slope"] = round(ma50_slope, 3)
    ma_dict["ma200_slope"] = round(ma200_slope, 3)

    ma_dict["golden_cross"] = golden_cross_today


    return ma_dict



def get_macd_data(ticker_symbol):
    macd_dict = {}
    macd_response = requests.get(f"https://api.twelvedata.com/macd?symbol={ticker_symbol}&interval=1day&apikey={twelve_data_api_key}")

    macd_data = macd_response.json()["values"]
    current_macd = float(macd_data[0]["macd"])
    current_signal = float(macd_data[0]["macd_signal"])

    if current_macd > current_signal:
        macd_position = "above_signal"
    elif current_macd < current_signal:
        macd_position = "below_signal"
    else:
        macd_position = "at_signal"

    current_macd = float(macd_data[0]["macd"])
    current_signal = float(macd_data[0]["macd_signal"])

    previous_macd = float(macd_data[1]["macd"])
    previous_signal = float(macd_data[1]["macd_signal"])

    if (
    current_macd > current_signal and
    previous_macd <= previous_signal
    ):
        macd_crossover = "bullish"

    elif (
        current_macd < current_signal and
        previous_macd >= previous_signal
    ):
        macd_crossover = "bearish"

    else:
        macd_crossover = "none"

    macd_dict["macd_position"] = macd_position
    macd_dict["macd_crossover"] = macd_crossover

    return macd_dict

