from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("campaigns", "0003_campaign_donate_qr_image_url"),
    ]

    operations = [
        migrations.AlterField(
            model_name="campaign",
            name="goal_amount",
            field=models.DecimalField(decimal_places=2, max_digits=18),
        ),
    ]
