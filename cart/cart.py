from decimal import Decimal

from django import template
register = template.Library()

from donation.models import DonationType


class Cart:
    def __init__(self, request):
        self.session = request.session
        self.donation_items = self.session.get('donation_items')

    def num_items(self):
        return sum([1 for item in self.donation_items])

    def remove(self, donation_type):
        dtype_id = int(donation_type.id)
        self.donation_items = [
            item for item in self.donation_items
            if item[0] != dtype_id
        ]
        self.save()

    def save(self):
        self.session['donation_items'] = self.donation_items
        self.session.modified = True

    def clear(self):
        self.donation_items = []
        self.save()

    def get_total_price(self):
        total = sum(Decimal(item[1]['amount']) * item[1]['quantity'] for item in self.donation_items)
        return total

