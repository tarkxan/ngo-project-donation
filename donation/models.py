from decimal import Decimal

from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractUser
from django.db import models


class DonationType(models.Model):
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    monthly_billing = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class DonationUser(AbstractUser):
    ROLE_REGULAR = 'RG'
    ROLE_ADMIN = 'AD'
    ROLE_CHOICES = (
        (ROLE_REGULAR, 'Regular'),
        (ROLE_ADMIN, 'Administrator'),
    )

    # fields included from user: username, first_name, last_name, email, (is_staff), date_joined
    role = models.CharField(verbose_name='Role', max_length=10, choices=ROLE_CHOICES, default=ROLE_REGULAR)
    phone_number = models.CharField(verbose_name='Phone #', max_length=20, blank=True)

    main_address = models.CharField(verbose_name='Address 1', max_length=100, blank=True)
    alt_address = models.CharField(verbose_name='Address 2', max_length=100, blank=True)
    city = models.CharField(verbose_name='City', max_length=50, blank=True)
    state = models.CharField(verbose_name='State', max_length=50, blank=True)
    zip_code = models.CharField(verbose_name='Zip/Postal Code', max_length=10, blank=True)
    country = models.CharField(verbose_name='Country', max_length=50, blank=True)

    def __str__(self):
        return self.username


def get_default_donation_type():
    return DonationType.objects.get_or_create(
        name="DELETED DONATION TYPE",
        is_active=False
    )[0]


class Donation(models.Model):
    user = models.ForeignKey('DonationUser', on_delete=models.SET_DEFAULT, default=1)
    type = models.ForeignKey('DonationType', on_delete=models.SET(get_default_donation_type))
    donation_time = models.DateTimeField(auto_now_add=True)
    monthly_billing = models.BooleanField(default=False)
    amount = models.DecimalField(
        verbose_name='Donation Amount',
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal(0.01))
        ]
    )

    def __str__(self):
        donation_user = get_user_model().objects.get(pk=self.user.pk)
        donation_type = apps.get_model(app_label='donation', model_name='DonationType')\
            .objects.get(pk=self.type.pk)
        return "{}: {} - {} {}".format(donation_user, donation_type, self.donation_time.date(), self.donation_time.time())
