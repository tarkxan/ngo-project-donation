from decimal import Decimal

from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from cart.cart import Cart
from cart.forms import CheckoutForm
from donation.models import DonationType, DonationUser, Donation
from project.secret import DEFAULT_EMAIL


class CartDetail(FormView):
    template_name = 'cart/detail.html'
    form_class = CheckoutForm
    success_url = reverse_lazy('cart:checkout')

    def get_context_data(self, **kwargs):
        context = super(CartDetail, self).get_context_data(**kwargs)
        donation_items = self.request.session.get('donation_items')
        context_items = [
            {
                'name': DonationType.objects.get(pk=item[0]).name,
                'quantity': item[1]['quantity'],
                'price': item[1]['amount'],
                'total': item[1]['quantity']*item[1]['amount'],
            }
            for item in donation_items
        ]
        context['cart'] = Cart(self.request)
        context['items'] = context_items
        return context

    @staticmethod
    def make_donations(request):
        user = request.user
        data = request.session['donation_items']
        for item in data:
            type = DonationType.objects.get(pk=item[0])
            amount = item[1]['amount']
            recurrence = item[1]['recurrence']
            Donation(user=user, type=type, monthly_billing=recurrence, amount=amount).save()

    @staticmethod
    def send_confirmation_mail(request):
        user = request.user
        name = user.first_name + " " + user.last_name
        data = request.session['donation_items']
        donation_entries = []
        for item in data:
            type_name = DonationType.objects.get(pk=item[0]).name
            amount = item[1]['amount']
            donation_entries.append('{0}: ${1}'.format(type_name, Decimal(amount)))
        donation_details = '\n'.join(donation_entries)

        email_body = (
            'Thank you {0} for your donation. Below are the details of the donation:\n\n'
            '{1}'
        ).format(name, donation_details)
        send_mail(
            'NGO - Donation',
            email_body,
            DEFAULT_EMAIL,
            [request.user.email,]
        )


    def form_valid(self, form):
        self.send_confirmation_mail(self.request)
        self.make_donations(self.request)
        Cart(self.request).clear()
        return super().form_valid(form)


class CheckoutDetail(TemplateView):
    template_name = 'cart/checkout.html'
