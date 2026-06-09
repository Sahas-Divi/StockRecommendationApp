from django.shortcuts import render
from django.http import HttpResponse
from .langchain_logic.agent_workflow import get_stock_news, get_rsi_data, get_ma_data, get_macd_data
from .langchain_logic.lstm_math_model_calculation import calculate_lstm_math_model
from .langchain_logic.garch_math_model_calculation import calculate_garch_math_model



def recommendation_view(request):
    if request.method == 'POST':
        ticker_symbol = request.POST.get('tickersymbol')
        print(get_stock_news(ticker_symbol))
        print(get_rsi_data(ticker_symbol))
        print(get_ma_data(ticker_symbol))
        print(get_macd_data(ticker_symbol))
        print(calculate_lstm_math_model(ticker_symbol))
        print(calculate_garch_math_model(ticker_symbol))
        return HttpResponse("Reached post here successfully")
    else:
        return HttpResponse("reached get successfully")