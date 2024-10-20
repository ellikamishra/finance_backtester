from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from .models import train_and_predict

@require_http_methods(["GET"])
def predict_stock_prices(request):
    symbol = request.GET.get('symbol')
    predictions = train_and_predict(symbol)
    return JsonResponse({'predictions': predictions})