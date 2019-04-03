from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from cart.cart import Cart
from cart.forms import CheckoutForm
from donation.models import DonationType, DonationUser, Donation


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

    def form_valid(self, form):
        self.make_donations(self.request)
        Cart(self.request).clear()
        # Send the email
        return super().form_valid(form)


class CheckoutDetail(TemplateView):
    template_name = 'cart/checkout.html'
