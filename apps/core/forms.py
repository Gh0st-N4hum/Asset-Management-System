from django import forms

from .models import Asset


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            "asset_tag", "name", "category", "department", "location", "supplier",
            "serial_number", "purchase_date", "purchase_cost", "status", "notes",
        ]
        widgets = {
            "purchase_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
