import os
from pathlib import Path
from urllib.parse import unquote

import cloudinary
import cloudinary.uploader

from django.conf import settings
from django.core.management.base import BaseCommand

from OWNER.models import CategoryOne, CategoryTwo, Product


class Command(BaseCommand):
    help = "Upload database-referenced local images to Cloudinary and update database URLs."

    def handle(self, *args, **options):

        # ============================================================
        # CLOUDINARY CONFIGURATION
        # ============================================================

        cloudinary.config(
            cloud_name=os.environ["CLOUDINARY_CLOUD_NAME"],
            api_key=os.environ["CLOUDINARY_API_KEY"],
            api_secret=os.environ["CLOUDINARY_API_SECRET"],
            secure=True,
        )

        # ============================================================
        # MEDIA ROOT
        # ============================================================

        media_root = Path(settings.MEDIA_ROOT)

        self.stdout.write(
            f"MEDIA_ROOT: {media_root.resolve()}"
        )

        # ============================================================
        # COUNTERS
        # ============================================================

        uploaded = 0
        skipped = 0
        missing = 0
        failed = 0

        # ============================================================
        # IMAGE UPLOAD FUNCTION
        # ============================================================

        def upload_image(value, folder):

            nonlocal uploaded, skipped, missing, failed

            if not value:
                return value

            value = str(value)

            # --------------------------------------------------------
            # Already migrated to Cloudinary
            # --------------------------------------------------------

            if (
                "res.cloudinary.com" in value
                or "cloudinary.com" in value
            ):
                skipped += 1
                return value

            # --------------------------------------------------------
            # Normalize path
            # --------------------------------------------------------

            relative = value.replace("\\", "/").lstrip("/")

            # Remove /media/ prefix
            if relative.startswith("media/"):
                relative = relative[6:]

            # Decode URL encoding:
            # %20 -> space
            # %28 -> (
            # %29 -> )
            relative = unquote(relative)

            # --------------------------------------------------------
            # Ignore static references
            # --------------------------------------------------------

            if relative.startswith("static/"):
                self.stdout.write(
                    self.style.WARNING(
                        f"Static reference not migrated: {value}"
                    )
                )
                missing += 1
                return value

            # --------------------------------------------------------
            # Local file path
            # --------------------------------------------------------

            local_path = media_root / relative

            if not local_path.is_file():

                self.stdout.write(
                    self.style.WARNING(
                        f"Missing: {local_path}"
                    )
                )

                missing += 1

                return value

            # --------------------------------------------------------
            # Upload to Cloudinary
            # --------------------------------------------------------

            try:

                filename = Path(relative)

                # Use filename without extension as public ID
                public_id = filename.stem

                result = cloudinary.uploader.upload(
                    str(local_path),
                    folder=folder,
                    public_id=public_id,
                    overwrite=True,
                    resource_type="image",
                )

                secure_url = result["secure_url"]

                uploaded += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Uploaded: {relative}"
                    )
                )

                return secure_url

            except Exception as exc:

                failed += 1

                self.stdout.write(
                    self.style.ERROR(
                        f"Failed: {relative} -> {exc}"
                    )
                )

                return value

        # ============================================================
        # CATEGORY ONE
        # ============================================================

        self.stdout.write("")
        self.stdout.write("========== CATEGORY ONE ==========")

        for category in CategoryOne.objects.all():

            new_image = upload_image(
                category.image,
                "liyaura/category_images",
            )

            if new_image != category.image:

                category.image = new_image

                category.save(
                    update_fields=["image"]
                )

        # ============================================================
        # CATEGORY TWO
        # ============================================================

        self.stdout.write("")
        self.stdout.write("========== CATEGORY TWO ==========")

        for category in CategoryTwo.objects.all():

            new_image = upload_image(
                category.image,
                "liyaura/category_two_images",
            )

            if new_image != category.image:

                category.image = new_image

                category.save(
                    update_fields=["image"]
                )

        # ============================================================
        # PRODUCTS
        # ============================================================

        self.stdout.write("")
        self.stdout.write("========== PRODUCTS ==========")

        for product in Product.objects.all():

            changed = False

            for field in (
                "image_1",
                "image_2",
                "image_3",
            ):

                old_value = getattr(
                    product,
                    field,
                    None,
                )

                new_value = upload_image(
                    old_value,
                    "liyaura/product_images",
                )

                if new_value != old_value:

                    setattr(
                        product,
                        field,
                        new_value,
                    )

                    changed = True

            if changed:

                product.save(
                    update_fields=[
                        "image_1",
                        "image_2",
                        "image_3",
                    ]
                )

        # ============================================================
        # SUMMARY
        # ============================================================

        self.stdout.write("")
        self.stdout.write(
            "========== MIGRATION SUMMARY =========="
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Uploaded: {uploaded}"
            )
        )

        self.stdout.write(
            f"Skipped:  {skipped}"
        )

        self.stdout.write(
            self.style.WARNING(
                f"Missing:  {missing}"
            )
        )

        self.stdout.write(
            self.style.ERROR(
                f"Failed:   {failed}"
            )
        )

        self.stdout.write(
            "========================================"
        )