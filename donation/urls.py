from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, reverse_lazy

from donation.views import DonationList, UserList, UserEdit

app_name = 'donation'
urlpatterns = [
    path('', DonationList.as_view(), name='index'),
    path('users/', UserList.as_view(), name='user_list'),
    path('users/<int:pk>/edit/', UserEdit.as_view(), name='user_edit'),
    path('accounts/login/', LoginView.as_view(extra_context={
        'next': reverse_lazy('donation:index')
    }), name='login'),
    path('accounts/logout/', LogoutView.as_view(next_page=
        reverse_lazy('donation:index')
    ), name='logout'),
]