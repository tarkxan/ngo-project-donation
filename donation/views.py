from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView

from donation.models import Donation, DonationUser


AUTH_REGULAR = 'RG'
AUTH_ADMIN = 'AD'
AUTH_INVALID = 'XX'


def get_auth_status(user):
    if user.is_authenticated and user.role == DonationUser.ROLE_ADMIN:
        status = AUTH_ADMIN
    elif user.is_authenticated and user.role == DonationUser.ROLE_REGULAR:
        status = AUTH_REGULAR
    else:
        status = AUTH_INVALID
    return status


def get_sidebar_urls(user):
    auth = get_auth_status(user)
    urls = {
        AUTH_ADMIN: [
            {
                'name': 'View Donors',
                'url': reverse_lazy('donation:user_list'),
            },
            {
                'name': 'View Donations',
                'url': reverse_lazy('donation:index'),
            },
            {
                'name': 'Edit User Information',
                'url': reverse_lazy('donation:user_edit', kwargs={'pk': user.pk})
            },
        ],
        AUTH_REGULAR: [
            {
                'name': 'View Donations',
                'url': reverse_lazy('donation:index'),
            },
            {
                'name': 'Edit User Information',
                'url': reverse_lazy('donation:user_edit', kwargs={'pk': user.pk})
            },
        ],
    }.get(auth, [])
    return urls


class UserList(ListView):
    context_object_name = 'users'
    template_name = 'donation/list.html'

    def get_queryset(self):
        user = self.request.user
        auth = get_auth_status(user)
        queryset = {
            AUTH_ADMIN: DonationUser.objects.all(),
        }.get(auth, DonationUser.objects.none())
        return queryset

    def get_context_data(self, *args, object_list=None, **kwargs):
        user = self.request.user
        context = super(UserList, self).get_context_data(*args, object_list=object_list, **kwargs)
        context['sidebar_urls'] = get_sidebar_urls(user)
        return context


# noinspection SpellCheckingInspection
class DonationList(ListView):
    context_object_name = 'donations'
    template_name = 'donation/donation/list.html'

    def get_queryset(self):
        user = self.request.user
        auth = get_auth_status(user)
        queryfunc, kwargs = {
            AUTH_ADMIN: (Donation.objects.all, {}),
            AUTH_REGULAR: (Donation.objects.filter, {'user': user}),
        }.get(auth, (Donation.objects.none, {}))
        queryset = queryfunc(**kwargs)
        return queryset

    def get_context_data(self, *args, object_list=None, **kwargs):
        user = self.request.user
        context = super(DonationList, self).get_context_data(*args, object_list=object_list, **kwargs)
        context['sidebar_urls'] = get_sidebar_urls(user)
        return context


class UserEdit(UpdateView):
    model = DonationUser
    template_name = 'donation/user/edit.html'
    fields = [
        'first_name', 'last_name', 'email', 'phone_number',
        'main_address', 'alt_address', 'city',
        'state', 'zip_code', 'country',
    ]

    def get_success_url(self):
        return reverse_lazy('donation:index')

    def get_context_data(self, *args, object_list=None, **kwargs):
        user = self.request.user
        context = super(UserEdit, self).get_context_data(*args, object_list=object_list, **kwargs)
        context['sidebar_urls'] = get_sidebar_urls(user)
        return context
