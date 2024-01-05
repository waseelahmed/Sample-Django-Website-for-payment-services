from decimal import Decimal
from django.http import JsonResponse
from rest_framework.decorators import api_view

# The dictionary of exchange rates against USD for all currencies
exchange_rate = {'GBP': Decimal(0.81715), 'EURO': Decimal(0.93032), 'USD': Decimal(1)}


@api_view(['GET'])
def get_converted_amount(request, currency1, currency2, amount):
    """
    This method redirects admin users to main admin panel
    :param request:
    :param amount: The amount needed to be converted
    :param currency1: The currency of amount provided
    :param currency2: The currency of amount required
    :return: The equivalent amount of required currency
   """

    # Get currency ones equivalent value in currency 2
    amount = Decimal(amount)
    base = amount / exchange_rate[currency1]
    final = base * exchange_rate[currency2]

    return JsonResponse({'converted_amount': Decimal('{:.2f}'.format(final))})
