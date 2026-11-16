from django.shortcuts import render

# Create your views here.

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import DetailView, ListView

from .models import Asset, Category, Department


class AssetListView(LoginRequiredMixin, ListView):
    model = Asset
    paginate_by = 25

    def get_queryset(self):
        qs = Asset.objects.select_related("category", "department", "location")
        get = self.request.GET

        q = get.get("q", "").strip()
        if q:
            qs = qs.filter(
                Q(asset_tag__icontains=q) | Q(name__icontains=q) | Q(serial_number__icontains=q)
            )

        status = get.get("status")
        if status in Asset.Status.values:
            qs = qs.filter(status=status)

        for field in ("department", "category"):
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


class AssetDetailView(LoginRequiredMixin, DetailView):
    queryset = Asset.objects.select_related("category", "department", "location", "supplier")

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
