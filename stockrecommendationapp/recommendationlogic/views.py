from django.shortcuts import render
from django.http import HttpResponse
from .langchain_logic.agent_workflow import get_stock_news, get_rsi_data, get_ma_data, get_macd_data
from .langchain_logic.lstm_math_model_calculation import calculate_lstm_math_model
from .langchain_logic.garch_math_model_calculation import calculate_garch_math_model
from langchain.agents import create_agent
from .langchain_logic.schemas import StockRecommendation
from langchain_core.prompts import PromptTemplate



def recommendation_view(request):
    if request.method == 'POST':
        ticker_symbol = request.POST.get('tickersymbol')
        stock_news = get_stock_news(ticker_symbol)
        rsi_data = get_rsi_data(ticker_symbol)
        ma_data = get_ma_data(ticker_symbol)
        macd_data = get_macd_data(ticker_symbol)
        lstm_math_model_answer = calculate_lstm_math_model(ticker_symbol)
        garch_math_model_answer = calculate_garch_math_model(ticker_symbol)
        recommendation_agent = create_agent("openai:gpt-5.4",  system_prompt="You are an expert in stock analysis who takes information like news, some technical analysis and answers from math models and reccomends whether the user should buy a stock or not",
                                            response_format=StockRecommendation)
        prompt = PromptTemplate.from_template("Use the following data: stock news: {stock_news}, Relative strength index data: {rsi_data}, Moving Average data: {ma_data}, Moving Average Convergence Divergence: {macd_data}, answer from Long Short-Term Memory (LSTM) mathematical model: {lstm_math_model_answer} and answer from GARCH (Generalized Autoregressive Conditional Heteroskedasticity) model: {garch_math_model_answer}. Interpret all this data and give me a recommendation of whether I should buy the stock or short it along with proper reasoning. ")
        formatted_prompt = prompt.format(stock_news=stock_news, rsi_data = rsi_data, ma_data = ma_data, macd_data=macd_data, lstm_math_model_answer = lstm_math_model_answer, garch_math_model_answer=garch_math_model_answer)
        result = recommendation_agent.invoke({"messages": [{"role": "user", "content": formatted_prompt}]})
        return render(request, "final_recommendation.html", {"recommendation_answer": result["structured_response"].recommendation, "reason": result["structured_response"].reason})
    else:
        return HttpResponse("reached get successfully")