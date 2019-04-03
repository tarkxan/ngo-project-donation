from django.urls import path, reverse_lazy

from cart.views import CartDetail, CheckoutDetail

app_name = 'cart'
urlpatterns = [
    path('', CartDetail.as_view(), name='detail'),
    path('checkout/', CheckoutDetail.as_view(), name='checkout'),
]