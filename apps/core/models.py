from django.db import models

# Create your models here.

class Department(models.Model):
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=20, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=120)
    parent = models.ForeignKey(
        "self", null=True, blank=True,
        on_delete=models.PROTECT, related_name="children",
    )

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["parent", "name"],
                name="unique_location_name_per_parent",
                nulls_distinct=False,
            )
        ]

    def __str__(self):
        parts = [self.name]
        node = self.parent
        while node:
            parts.append(node.name)
            node = node.parent
        return " > ".join(reversed(parts))


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    useful_life_years = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Supplier(models.Model):
    name = models.CharField(max_length=160, unique=True)
    contact = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db.models import Q, UniqueConstraint
from django.utils import timezone
from simple_history.models import HistoricalRecords


class Asset(models.Model):
    class Status(models.TextChoices):
        IN_USE = "in_use", "In use"
        IN_STORAGE = "in_storage", "In storage"
        UNDER_REPAIR = "under_repair", "Under repair"
        DISPOSED = "disposed", "Disposed"

    asset_tag = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=150)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="assets")
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="assets")
    location = models.ForeignKey(Location, on_delete=models.PROTECT, related_name="assets")
    supplier = models.ForeignKey(
        Supplier, null=True, blank=True, on_delete=models.PROTECT, related_name="assets"
    )
    serial_number = models.CharField(max_length=100, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    purchase_cost = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0)],
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_USE)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    class Meta:
        ordering = ["asset_tag"]
        constraints = [
            UniqueConstraint(
                fields=["serial_number"],
                condition=~Q(serial_number=""),
                name="unique_serial_when_set",
            )
        ]

    def __str__(self):
        return f"{self.asset_tag} {self.name}"

    def get_absolute_url(self):
        return reverse("asset_detail", args=[self.pk])
    def clean(self):
        if self.purchase_date and self.purchase_date > timezone.localdate():
            raise ValidationError({"purchase_date": "Purchase date cannot be in the future."})
