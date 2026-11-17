from django.contrib import admin

# Register your models here.
from simple_history.admin import SimpleHistoryAdmin
from .models import Asset
from .models import Category, Department, Location, Supplier


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("__str__", "parent")
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "useful_life_years")
    search_fields = ("name",)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "contact")
    search_fields = ("name",)

@admin.register(Asset)
class AssetAdmin(SimpleHistoryAdmin):
    list_display = ("asset_tag", "name", "category", "department", "location", "custodian", "status")
    list_filter = ("status", "category", "department")
    search_fields = ("asset_tag", "name", "serial_number", "custodian__full_name")
    list_select_related = ("category", "department", "location", "custodian")


from django.db.models import Count

from .models import Custodian


@admin.register(Custodian)
class CustodianAdmin(admin.ModelAdmin):
    list_display = ("full_name", "employee_number", "department", "is_active", "items_held")
    list_filter = ("is_active", "department")
    search_fields = ("full_name", "employee_number")
    list_select_related = ("department",)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_held=Count("assets"))

    @admin.display(description="Items held", ordering="_held")
    def items_held(self, obj):
        return obj._held
