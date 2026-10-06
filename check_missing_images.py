import os
from pathlib import Path
from urllib.parse import unquote

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LIYAURA.settings")

import django
django.setup()

from django.conf import settings
from OWNER.models import Product, CategoryOne, CategoryTwo


MEDIA_ROOT = Path(settings.MEDIA_ROOT)

print("=" * 60)
print("MEDIA IMAGE CHECK")
print("=" * 60)
print()
print("MEDIA_ROOT:", MEDIA_ROOT.resolve())
print("MEDIA_ROOT EXISTS:", MEDIA_ROOT.exists())
print()


missing = []
existing = []
cloudinary = []


def check_image(value, model_name, obj_id, field_name):
    if not value:
        return

    value = str(value)

    # Already migrated to Cloudinary
    if "res.cloudinary.com" in value or "cloudinary.com" in value:
        cloudinary.append(
            (model_name, obj_id, field_name, value)
        )
        return

    # Normalize path
    relative = value.replace("\\", "/").lstrip("/")

    # Remove /media/ prefix
    if relative.startswith("media/"):
        relative = relative[6:]

    # Decode URL encoded characters such as %20
    relative = unquote(relative)

    path = MEDIA_ROOT / relative

    if path.exists():
        existing.append(
            (model_name, obj_id, field_name, value, str(path))
        )
    else:
        missing.append(
            (model_name, obj_id, field_name, value, str(path))
        )


# ============================================================
# CATEGORY ONE
# ============================================================

for obj in CategoryOne.objects.all():
    check_image(
        obj.image,
        "CategoryOne",
        obj.id,
        "image"
    )


# ============================================================
# CATEGORY TWO
# ============================================================

for obj in CategoryTwo.objects.all():
    check_image(
        obj.image,
        "CategoryTwo",
        obj.id,
        "image"
    )


# ============================================================
# PRODUCTS
# ============================================================

for obj in Product.objects.all():

    for field in ["image1", "image2", "image3"]:

        if hasattr(obj, field):

            image = getattr(obj, field)

            check_image(
                image,
                "Product",
                obj.id,
                field
            )


# ============================================================
# RESULTS
# ============================================================

print("=" * 60)
print("RESULT")
print("=" * 60)
print()

print("Cloudinary images :", len(cloudinary))
print("Local images      :", len(existing))
print("Missing images    :", len(missing))
print()


if missing:

    print("=" * 60)
    print("MISSING IMAGES")
    print("=" * 60)

    for item in missing:
        print()
        print("Model :", item[0])
        print("ID    :", item[1])
        print("Field :", item[2])
        print("DB    :", item[3])
        print("Path  :", item[4])

else:

    print("NO MISSING IMAGES FOUND.")


print()
print("=" * 60)
print("TOTAL REFERENCED IMAGES")
print("=" * 60)

print(
    "Total:",
    len(cloudinary) + len(existing) + len(missing)
)