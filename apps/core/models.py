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
