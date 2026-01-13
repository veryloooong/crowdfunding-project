from __future__ import annotations

from django.db import migrations, models


class Migration(migrations.Migration):

  dependencies = [
    ("groups", "0002_remove_donorgroup_join_code"),
  ]

  operations = [
    migrations.AddField(
      model_name="donorgroup",
      name="image_url",
      field=models.URLField(blank=True),
    ),
  ]
