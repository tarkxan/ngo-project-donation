from django.views.generic import TemplateView

from cart.cart import Cart
from donation.models import DonationType


class CartDetail(TemplateView):
    template_name = 'cart/detail.html'

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
