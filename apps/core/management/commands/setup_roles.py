from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError

LOOKUPS = ["department", "location", "category", "supplier"]
VIEW_ALL = ["view_asset", "view_historicalasset", "view_custodian"] + [
    f"view_{m}" for m in LOOKUPS
]

ROLES = {
    "IT Audit": VIEW_ALL,
    "User": VIEW_ALL + ["add_asset", "change_asset"],
    "Administrator": VIEW_ALL
    + ["add_asset", "change_asset", "add_custodian", "change_custodian"]
    + [f"{a}_{m}" for m in LOOKUPS for a in ("add", "change", "delete")],
}


class Command(BaseCommand):
    help = "Create or update the role groups. Safe to run repeatedly."

    def handle(self, *args, **options):
        for name, codenames in ROLES.items():
            wanted = set(codenames)
            perms = Permission.objects.filter(
                content_type__app_label="core", codename__in=wanted
            )
            if perms.count() != len(wanted):
                missing = wanted - set(perms.values_list("codename", flat=True))
                raise CommandError(f"Unknown permissions for {name}: {sorted(missing)}")
            group, _ = Group.objects.get_or_create(name=name)
            group.permissions.set(perms)
            self.stdout.write(f"{name}: {len(wanted)} permissions")
