from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, reverse_lazy

from donation.views import DonationList, UserList, UserEdit, DonationCreate, DonationTypeList, IndexView, \
    DonationTypeRemove

app_name = 'donation'
urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('users/', UserList.as_view(), name='user_list'),
    path('users/<int:pk>/edit/', UserEdit.as_view(), name='user_edit'),
    path('donations', DonationList.as_view(), name='donation_list'),
    path('donations/new', DonationCreate.as_view(), name='donation_create'),
    path('dtypes/', DonationTypeList.as_view(), name = 'dtype_list'),
    path('dtypes/<int:pk>/remove/', DonationTypeRemove.as_view(), name='dtype_remove'),
    path('login/', LoginView.as_view(
        extra_context={'next': reverse_lazy('donation:index')}
    ), name='login'),
    path('logout/', LogoutView.as_view(next_page=reverse_lazy('donation:index')), name='logout'),
]