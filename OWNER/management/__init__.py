@'
import os
import gzip
import base64
import tempfile

from django.core.management.base import BaseCommand
from django.core.management import call_command
from OWNER.models import Product


class Command(BaseCommand):
    help = "Import catalog fixture from CATALOG_FIXTURE_B64"

    def handle(self, *args, **options):
        encoded = os.environ.get("CATALOG_FIXTURE_B64")

        if not encoded:
            self.stdout.write(
                self.style.WARNING(
                    "CATALOG_FIXTURE_B64 not set. Skipping catalog import."
                )
            )
            return

        if Product.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"Catalog already exists ({Product.objects.count()} products). "
                    "Skipping import."
                )
            )
            return

        fixture_path = None

        try:
            compressed = base64.b64decode(encoded)
            fixture_data = gzip.decompress(compressed)

            with tempfile.NamedTemporaryFile(
                mode="wb",
                suffix=".json",
                delete=False
            ) as temp_file:
                temp_file.write(fixture_data)
                fixture_path = temp_file.name

            self.stdout.write("Loading catalog fixture...")

            call_command("loaddata", fixture_path, verbosity=1)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Catalog imported successfully. "
                    f"Products: {Product.objects.count()}"
                )
            )

        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f"Catalog import failed: {e}")
            )
            raise

        finally:
            if fixture_path and os.path.exists(fixture_path):
                os.remove(fixture_path)
'@ | Set-Content -Path OWNER\management\commands\import_catalog.py -Encoding utf8