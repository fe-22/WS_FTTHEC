from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_crmaccessrequest"),
    ]

    operations = [
        migrations.CreateModel(
            name="SiteVisit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("visitor_id", models.CharField(db_index=True, max_length=64)),
                ("ip_address", models.CharField(blank=True, max_length=45)),
                ("path", models.CharField(max_length=500)),
                ("referrer", models.CharField(blank=True, max_length=500)),
                ("user_agent", models.CharField(blank=True, max_length=500)),
                ("country", models.CharField(blank=True, max_length=10)),
                ("region", models.CharField(blank=True, max_length=100)),
                ("city", models.CharField(blank=True, max_length=100)),
                ("visited_at", models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
            options={
                "verbose_name": "Visita do site",
                "verbose_name_plural": "Visitas do site",
                "ordering": ["-visited_at"],
            },
        ),
    ]
