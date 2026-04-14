from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("reservations", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="OtaEmail",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("source_channel", models.CharField(max_length=80)),
                ("subject", models.CharField(blank=True, max_length=255, null=True)),
                ("sender_email", models.CharField(blank=True, max_length=255, null=True)),
                ("raw_content", models.TextField()),
                ("parsed_payload", models.JSONField(blank=True, null=True)),
                (
                    "processing_status",
                    models.CharField(
                        choices=[("pending", "Pending"), ("parsed", "Parsed"), ("failed", "Failed")],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("failure_reason", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "reservation",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="ota_emails",
                        to="reservations.reservation",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]
