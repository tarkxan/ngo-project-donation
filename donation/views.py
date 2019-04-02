from decimal import Decimal

from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, UpdateView, FormView, TemplateView

from donation.forms import DonationCreateForm
from donation.models import Donation, DonationUser, DonationType

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
            {
                'name': 'Make donation',
                'url': reverse_lazy('donation:donation_create')
            },
            {
                'name': 'View Donation Types',
                'url': reverse_lazy('donation:dtype_list')
            },
        ],
        AUTH_REGULAR: [
            {
                'name': 'View Donation Types',
                'url': reverse_lazy('donation:index'),
            },
            {
                'name': 'Edit User Information',
                'url': reverse_lazy('donation:user_edit', kwargs={'pk': user.pk})
            },
            {
                'name': 'Make donation',
                'url': reverse_lazy('donation:donation_create')
            },
            {
                'name': 'View Donations',
                'url': reverse_lazy('donation:donation_list')
            },
        ],
    }.get(auth, [])
    return urls


class UserList(ListView):
    context_object_name = 'users'
    template_name = 'donation/user/list.html'

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


class DonationCreate(FormView):
    template_name = 'donation/donation/create.html'
    form_class = DonationCreateForm
    success_url = reverse_lazy('cart:detail')

    def get_initial(self):
        initial = super(DonationCreate, self).get_initial()
        items = self.request.session['donation_items']
        for item in items:
            pk = item[0]
            initial['amount_{}'.format(pk)] = Decimal(item[1]['amount'])
            initial['recurring_{}'.format(pk)] = item[1]['recurrence']
        return initial

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super(DonationCreate, self).get_context_data(**kwargs)
        context['sidebar_urls'] = get_sidebar_urls(user)
        context['donation_types'] = DonationType.objects.filter(is_active=True)
        return context

    @staticmethod
    def make_donations(data):
        user = DonationUser.objects.get(pk=data[0])
        for item in data[1]:
            type = DonationType.objects.get(pk=item[0])
            amount = item[1]['amount']
            recurrence = item[1]['recurrence']
            Donation(user=user, type=type, monthly_billing=recurrence, amount=amount).save()

    def form_valid(self, form):
        pks = [int(s[7:]) for s in [k for k in form.cleaned_data.keys()][:-1:2]]
        amounts = [v for v in form.cleaned_data.values()][:-1:2]
        recurrences = [v for v in form.cleaned_data.values()][1:-1:2]
        data = (int(form.cleaned_data['user_id']), [
            (pk, {'amount': str(amount), 'recurrence': recurrence, 'quantity':1})
            for pk, amount, recurrence in zip(pks, amounts, recurrences)
            if amount
        ])
        # Do not save the data yet. Go to the cart first
        # self.make_donations(data)
        self.request.session['user_id'] = data[0]
        self.request.session['donation_items'] = data[1]
        self.request.session.modified = True
        return super().form_valid(form)


class DonationTypeList(ListView):
    context_object_name = 'donation_types'
    template_name = 'donation/donation_type/list.html'

    def get_queryset(self):
        user = self.request.user
        auth = get_auth_status(user)
        queryset = {
            AUTH_ADMIN: DonationType.objects.filter(is_active=True),
            AUTH_REGULAR: DonationType.objects.filter(is_active=True),
        }.get(auth, DonationType.objects.none())
        return queryset

    def get_context_data(self, *args, object_list=None, **kwargs):
        user = self.request.user
        context = super(DonationTypeList, self).get_context_data(*args, object_list=object_list, **kwargs)
        context['sidebar_urls'] = get_sidebar_urls(user)
        return context


class HomeView(TemplateView):
    template_name = 'donation/home.html'


class IndexView(View):
    def get(self, request, *args, **kwargs):
        auth = get_auth_status(self.request.user)
        view = {
            AUTH_ADMIN: DonationList.as_view(),
            AUTH_REGULAR: DonationTypeList.as_view(),
        }.get(auth, HomeView.as_view())
        return view(request, *args, **kwargs)


class DonationTypeRemove(UpdateView):
    model = DonationType
    template_name = 'donation/donation_type/remove.html'
    fields = ['is_active']

    def get_success_url(self):
        return reverse_lazy('donation:dtype_list')

    def get_context_data(self, *args, object_list=None, **kwargs):
        user = self.request.user
        context = super(DonationTypeRemove, self).get_context_data(*args, object_list=object_list, **kwargs)
        context['sidebar_urls'] = get_sidebar_urls(user)
        context['name'] = self.object.name
        return context
