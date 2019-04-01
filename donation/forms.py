from django.forms import forms, DecimalField, BooleanField

from donation.models import DonationType


class DonationCreateForm(forms.Form):
    def __init__(self, *args, **kwargs):
        amount = DecimalField(max_digits=12, decimal_places=2)
        recurring = BooleanField(required=False)
        super(DonationCreateForm, self).__init__(*args, **kwargs)
        objs = DonationType.objects.filter(is_active=True)
        for obj, i in zip(objs, range(len(objs))):
            self.fields['amount_{}'.format(i)] = DecimalField(max_digits=12, decimal_places=2)
            self.fields['amount_{}'.format(i)].label = obj.name
            self.fields['recurring_{}'.format(i)] = BooleanField(required=False)
            self.fields['recurring_{}'.format(i)].label = 'recurring' if obj.monthly_billing else ''
