from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import AssetForm
from .models import Asset, Category, Department


class AssetListView(PermissionRequiredMixin, ListView):
    permission_required = "core.view_asset"
    model = Asset
    paginate_by = 25

    def get_queryset(self):
        qs = Asset.objects.select_related("category", "department", "location", "custodian")
        get = self.request.GET

        q = get.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(asset_tag__icontains=q) | Q(name__icontains=q) | Q(serial_number__icontains=q)
                | Q(custodian__full_name__icontains=q)
            )

        status = get.get("status")
        if status in Asset.Status.values:
            qs = qs.filter(status=status)

        for field in ("department", "category", "custodian"):
            value = get.get(field)
            if value and value.isdigit():
                qs = qs.filter(**{f"{field}_id": value})
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop("page", None)
        ctx.update(
            departments=Department.objects.all(),
            categories=Category.objects.all(),
            statuses=Asset.Status.choices,
            params=self.request.GET,
            querystring=params.urlencode(),
        )
        return ctx


class AssetDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "core.view_asset"
    queryset = Asset.objects.select_related("category", "department", "location", "supplier", "custodian")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        records = list(self.object.history.select_related("history_user"))
        entries = []
        for i, rec in enumerate(records):
            older = records[i + 1] if i + 1 < len(records) else None
            changes = (
                rec.diff_against(older, foreign_keys_are_objs=True).changes if older else []
            )
            entries.append({"record": rec, "changes": changes})
        ctx["entries"] = entries
        return ctx
class AssetCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = "core.add_asset"
    model = Asset
    form_class = AssetForm
    success_message = "Asset %(asset_tag)s created."


class AssetUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = "core.change_asset"
    model = Asset
    form_class = AssetForm
    success_message = "Asset %(asset_tag)s updated."
