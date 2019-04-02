from django.urls import path, reverse_lazy

from cart.views import CartDetail


app_name = 'cart'
urlpatterns = [
    path('', CartDetail.as_view(), name='detail'),
]