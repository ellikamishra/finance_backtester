from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import pdfkit

from .services.data_fetcher import fetch_stock_data
from .models import StockData
from .services.backtester import backtest_strategy
from django.conf import settings
from .services.report_generator import generate_report
import webbrowser
import os
import tempfile
class FetchStockDataView(APIView):
    @csrf_exempt
    def post(self, request):
        symbol = request.data.get('symbol')
        if not symbol:
            return Response({'error': 'Symbol is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = fetch_stock_data(symbol, settings.ALPHA_VANTAGE_API_KEY)
            for date, values in data.items():
                StockData.objects.create(
                    symbol=symbol,
                    date=date,
                    open_price=values['1. open'],
                    high_price=values['2. high'],
                    low_price=values['3. low'],
                    close_price=values['4. close'],
                    volume=values['5. volume']
                )
            return Response({'message': f'Successfully fetched and stored data for {symbol}'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    @csrf_exempt
    @require_http_methods(["POST"])
    def backtest(request):
        symbol = request.POST.get('symbol')
        initial_investment = float(request.POST.get('initial_investment'))
        buy_ma = int(request.POST.get('buy_ma'))
        sell_ma = int(request.POST.get('sell_ma'))
        
        result = backtest_strategy(symbol, initial_investment, buy_ma, sell_ma)
        
        return JsonResponse(result)
    @csrf_exempt
    @require_http_methods(["GET"])
    def generate_report_view(request):
        symbol = request.GET.get('symbol')
        initial_investment = float(request.GET.get('initial_investment',1000))
        buy_ma = int(request.GET.get('buy_ma',500))
        sell_ma = int(request.GET.get('sell_ma',20))
        
        report = generate_report(symbol, initial_investment, buy_ma, sell_ma)
        html = render(request, 'report.html', report).content.decode('utf-8')

    # Create a temporary file to save the PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as pdf_file:
            pdf_file_path = pdf_file.name

    # Convert HTML to PDF and save it to the temp file
        pdfkit.from_string(html, pdf_file_path)

    # Return a JSON response with the PDF file path
        response_data = {
            "message": "PDF report generated successfully",
            "pdf_file_path": pdf_file_path
        }
    
        return JsonResponse(response_data)