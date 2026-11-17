from django import forms
from django.db.models import Q

from .models import Asset, Custodian


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            "asset_tag", "name", "category", "department", "location", "supplier",
            "serial_number", "custodian", "purchase_date", "purchase_cost", "status", "notes",
        ]
        widgets = {
            "purchase_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        allowed = Q(is_active=True)
        if self.instance.pk and self.instance.custodian_id:
            allowed |= Q(pk=self.instance.custodian_id)
        self.fields["custodian"].queryset = Custodian.objects.filter(allowed)
