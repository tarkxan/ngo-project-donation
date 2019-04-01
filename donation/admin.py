from django.apps import apps
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.forms import ModelForm, forms

from donation.models import DonationUser, DonationType, Donation


@admin.register(DonationUser)
class UserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': (
            'phone_number',
            'main_address',
            'alt_address',
            'city',
            'state',
            'zip_code',
            'country',
            'role',
        )}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': (
            'first_name',
            'last_name',
            'email',
            'role',
        )}),
    )


@admin.register(DonationType)
class TypeAdmin(admin.ModelAdmin):
    pass


class DonationAddForm(ModelForm):
    class Meta:
        model = Donation
        exclude = ('user',)

    def clean_monthly_billing(self):
        selected_option = self.cleaned_data['monthly_billing']
        donation_type = apps.get_model(app_label='donation', model_name='DonationType')\
            .objects.get(pk=self.cleaned_data['type'].pk)
        if selected_option and not donation_type.monthly_billing:
            raise forms.ValidationError('Monthly billing not enabled for this donation type', code='invalid_billing')
        return selected_option


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    form = DonationAddForm

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj, form, change)
