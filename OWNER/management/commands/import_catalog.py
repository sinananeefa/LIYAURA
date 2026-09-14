import os
import gzip
import base64
import json
import tempfile

from django.core.management.base import BaseCommand
from django.db import transaction

from OWNER.models import CategoryOne, CategoryTwo, Product, Section, Offer


class Command(BaseCommand):
    help = "Import or update catalog from CATALOG_FIXTURE_B64"

    def handle(self, *args, **options):
        encoded = os.environ.get("CATALOG_FIXTURE_B64")

        if not encoded:
            self.stdout.write(
                self.style.WARNING(
                    "CATALOG_FIXTURE_B64 not set. Skipping catalog import."
                )
            )
            return

        try:
            compressed = base64.b64decode(encoded)
            fixture_data = gzip.decompress(compressed)
            data = json.loads(fixture_data.decode("utf-8-sig"))

            counts = {
                "categoryone": 0,
                "categorytwo": 0,
                "section": 0,
                "offer": 0,
                "product": 0,
            }

            with transaction.atomic():

                # 1. Sections
                for item in data:
                    if item["model"].lower() == "owner.section":
                        obj, created = Section.objects.update_or_create(
                            pk=item["pk"],
                            defaults=item["fields"],
                        )
                        counts["section"] += 1

                # 2. CategoryOne
                for item in data:
                    if item["model"].lower() == "owner.categoryone":
                        obj, created = CategoryOne.objects.update_or_create(
                            pk=item["pk"],
                            defaults=item["fields"],
                        )
                        counts["categoryone"] += 1

                # 3. CategoryTwo
                for item in data:
                    if item["model"].lower() == "owner.categorytwo":
                        fields = item["fields"].copy()

                       if "category_1" in fields:
    fields["category_1_id"] = fields.pop("category_1")

                        obj, created = CategoryTwo.objects.update_or_create(
                            pk=item["pk"],
                            defaults=fields,
                        )
                        counts["categorytwo"] += 1

                # 4. Offers
                for item in data:
                    if item["model"].lower() == "owner.offer":
                        obj, created = Offer.objects.update_or_create(
                            pk=item["pk"],
                            defaults=item["fields"],
                        )
                        counts["offer"] += 1

                # 5. Products
                for item in data:
                    if item["model"].lower() == "owner.product":
                        fields = item["fields"].copy()

                        if "category_1" in fields:
                            fields["category_1_id"] = fields.pop("category_1")

                        if "category_2" in fields:
                            fields["category_2_id"] = fields.pop("category_2")

                        if "section" in fields:
                            fields["section_id"] = fields.pop("section")

                        obj, created = Product.objects.update_or_create(
                            pk=item["pk"],
                            defaults=fields,
                        )
                        counts["product"] += 1

            self.stdout.write("")
            self.stdout.write("========== CATALOG IMPORT SUMMARY ==========")
            self.stdout.write(
                f"CategoryOne: {counts['categoryone']}"
            )
            self.stdout.write(
                f"CategoryTwo: {counts['categorytwo']}"
            )
            self.stdout.write(
                f"Section:     {counts['section']}"
            )
            self.stdout.write(
                f"Offer:       {counts['offer']}"
            )
            self.stdout.write(
                f"Products:    {counts['product']}"
            )
            self.stdout.write("============================================")
            self.stdout.write(
                self.style.SUCCESS(
                    "Catalog imported/updated successfully."
                )
            )

        except Exception as e:
            self.stderr.write(
                self.style.ERROR(
                    f"Catalog import failed: {e}"
                )
            )
            raise