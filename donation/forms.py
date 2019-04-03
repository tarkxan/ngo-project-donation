from decimal import Decimal

from django.core.validators import MinValueValidator
from django.forms import forms, DecimalField, BooleanField, CharField

from donation.models import DonationType


class DonationCreateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(DonationCreateForm, self).__init__(*args, **kwargs)
        objs = DonationType.objects.filter(is_active=True)
        for obj, i in zip(objs, range(len(objs))):
            self.fields['amount_{}'.format(obj.pk)] = DecimalField(
                max_digits=12, decimal_places=2,
                validators=[MinValueValidator(Decimal('0.01'))],
                required=False
            )
            self.fields['amount_{}'.format(obj.pk)].label = obj.name
            self.fields['recurring_{}'.format(obj.pk)] = BooleanField(required=False)
            self.fields['recurring_{}'.format(obj.pk)].label = 'recurring' if obj.monthly_billing else ''
        self.fields['user_id'] = CharField(max_length=100)
