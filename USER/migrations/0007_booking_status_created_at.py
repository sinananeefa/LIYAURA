from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("USER", "0006_address"),
    ]

    operations = [
        migrations.AddField(
            model_name="booking",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("confirmed", "Confirmed"),
                    ("completed", "Completed"),
                    ("cancelled", "Cancelled"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="booking",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
