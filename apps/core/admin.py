from django.contrib import admin

# Register your models here.

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
