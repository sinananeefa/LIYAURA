from django.db import migrations, models
from django.utils import timezone


def populate_feedback_created_at(apps, schema_editor):
    Feedback = apps.get_model("USER", "Feedback")
    Feedback.objects.filter(created_at__isnull=True).update(created_at=timezone.now())


class Migration(migrations.Migration):

    dependencies = [
        ("USER", "0007_booking_status_created_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="feedback",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.RunPython(
            populate_feedback_created_at,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="feedback",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]