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
    list_display = ("asset_tag", "name", "category", "department", "location", "status")
    list_filter = ("status", "category", "department")
    search_fields = ("asset_tag", "name", "serial_number")
    list_select_related = ("category", "department", "location")
