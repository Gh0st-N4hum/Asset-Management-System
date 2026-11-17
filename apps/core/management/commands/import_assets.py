import csv
import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.core.models import Asset, Category, Custodian, Department, Location, Supplier

REQUIRED = ["asset_tag", "name", "category", "department", "location"]
OPTIONAL = ["supplier", "custodian", "serial_number", "purchase_date", "purchase_cost", "status", "notes"]


def normalize_path(value):
    return " > ".join(part.strip() for part in value.split(">")).lower()


def location_paths():
    by_pk = {loc.pk: loc for loc in Location.objects.all()}
    paths = {}
    for loc in by_pk.values():
        parts, node = [], loc
        while node is not None and len(parts) < 20:
            parts.append(node.name)
            node = by_pk.get(node.parent_id)
        paths[normalize_path(" > ".join(reversed(parts)))] = loc
    return paths


class Command(BaseCommand):
    help = "Import assets from a CSV file. Use --dry-run to check it without saving."

    def add_arguments(self, parser):
        parser.add_argument("path")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, path, dry_run, **options):
        categories = {c.name.lower(): c for c in Category.objects.all()}
        suppliers = {s.name.lower(): s for s in Supplier.objects.all()}
        custodians_by_number, custodians_by_name = {}, {}
        for c in Custodian.objects.filter(is_active=True):
            if c.employee_number:
                custodians_by_number[c.employee_number.lower()] = c
            custodians_by_name.setdefault(c.full_name.lower(), []).append(c)
        departments = {}
        for d in Department.objects.all():
            departments[d.name.lower()] = d
            if d.code:
                departments[d.code.lower()] = d
        locations = location_paths()
        statuses = {}
        for value, label in Asset.Status.choices:
            statuses[value.lower()] = value
            statuses[str(label).lower()] = value

        try:
            fh = open(path, newline="", encoding="utf-8-sig")
        except OSError as exc:
            raise CommandError(f"Cannot open {path}: {exc}")

        errors, assets = [], []
        seen_tags, seen_serials = set(), set()

        with fh:
            reader = csv.DictReader(fh)
            headers = [h.strip().lower() for h in (reader.fieldnames or [])]
            reader.fieldnames = headers
            missing = [c for c in REQUIRED if c not in headers]
            unknown = [h for h in headers if h not in REQUIRED + OPTIONAL]
            if missing or unknown:
                raise CommandError(f"Header problem. Missing: {missing}. Unknown: {unknown}.")

            for line, row in enumerate(reader, start=2):
                row = {k: (v or "").strip() for k, v in row.items() if k}
                if not any(row.values()):
                    continue
                problems = []

                for col in REQUIRED:
                    if not row.get(col):
                        problems.append(f"{col} is empty")

                tag = row.get("asset_tag", "")
                if tag:
                    if tag.lower() in seen_tags:
                        problems.append(f"asset_tag {tag} appears twice in the file")
                    seen_tags.add(tag.lower())

                serial = row.get("serial_number", "")
                if serial:
                    if serial.lower() in seen_serials:
                        problems.append(f"serial_number {serial} appears twice in the file")
                    seen_serials.add(serial.lower())

                category = categories.get(row.get("category", "").lower())
                if row.get("category") and category is None:
                    problems.append(f'category "{row["category"]}" does not exist')

                department = departments.get(row.get("department", "").lower())
                if row.get("department") and department is None:
                    problems.append(f'department "{row["department"]}" does not exist')

                location = locations.get(normalize_path(row.get("location", "")))
                if row.get("location") and location is None:
                    problems.append(f'location "{row["location"]}" does not exist')

                supplier = None
                if row.get("supplier"):
                    supplier = suppliers.get(row["supplier"].lower())
                    if supplier is None:
                        problems.append(f'supplier "{row["supplier"]}" does not exist')

                custodian = None
                if row.get("custodian"):
                    key = row["custodian"].lower()
                    custodian = custodians_by_number.get(key)
                    if custodian is None:
                        matches = custodians_by_name.get(key, [])
                        if len(matches) == 1:
                            custodian = matches[0]
                        elif matches:
                            problems.append(
                                f'custodian "{row["custodian"]}" matches several people, use the employee number'
                            )
                        else:
                            problems.append(
                                f'custodian "{row["custodian"]}" does not exist or is inactive'
                            )

                purchase_date = None
                if row.get("purchase_date"):
                    try:
                        purchase_date = datetime.date.fromisoformat(row["purchase_date"])
                    except ValueError:
                        problems.append("purchase_date must look like 2024-03-15")

                purchase_cost = None
                if row.get("purchase_cost"):
                    try:
                        purchase_cost = Decimal(row["purchase_cost"].replace(",", ""))
                    except InvalidOperation:
                        problems.append("purchase_cost must be a number")

                extra = {}
                if row.get("status"):
                    status = statuses.get(row["status"].lower())
                    if status is None:
                        problems.append(f'status "{row["status"]}" is not valid')
                    else:
                        extra["status"] = status

                if problems:
                    errors.append((line, problems))
                    continue

                asset = Asset(
                    asset_tag=tag,
                    name=row["name"],
                    category=category,
                    department=department,
                    location=location,
                    supplier=supplier,
                    serial_number=serial,
                    custodian=custodian,
                    purchase_date=purchase_date,
                    purchase_cost=purchase_cost,
                    notes=row.get("notes", ""),
                    **extra,
                )
                try:
                    asset.full_clean()
                except ValidationError as exc:
                    for field, messages in exc.message_dict.items():
                        problems.extend(f"{field}: {m}" for m in messages)
                    errors.append((line, problems))
                    continue
                assets.append(asset)

        if errors:
            for line, problems in errors:
                self.stderr.write(f"Row {line}: " + "; ".join(problems))
            raise CommandError(f"{len(errors)} row(s) have errors. Nothing was imported.")
        if not assets:
            raise CommandError("The file has no data rows.")

        if dry_run:
            self.stdout.write(self.style.SUCCESS(
                f"Dry run passed: {len(assets)} asset(s) would be imported."
            ))
            return

        with transaction.atomic():
            for asset in assets:
                asset._change_reason = f"CSV import {Path(path).name}"
                asset.save()
        self.stdout.write(self.style.SUCCESS(f"Imported {len(assets)} asset(s)."))
