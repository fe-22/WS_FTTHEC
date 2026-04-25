from django.db import migrations, models


def populate_normalized_fields(apps, schema_editor):
    EmpresaReceita = apps.get_model("core", "EmpresaReceita")

    for empresa in EmpresaReceita.objects.all().iterator():
        empresa.razao_social_normalizada = normalize_search_text(
            empresa.razao_social
        )
        empresa.nome_fantasia_normalizado = normalize_search_text(
            empresa.nome_fantasia
        )
        empresa.municipio_normalizado = normalize_search_text(empresa.municipio)
        empresa.save(
            update_fields=[
                "razao_social_normalizada",
                "nome_fantasia_normalizado",
                "municipio_normalizado",
            ]
        )


def normalize_search_text(value):
    import unicodedata

    if not value:
        return ""
    normalized = unicodedata.normalize("NFKD", value)
    without_accents = "".join(
        char for char in normalized if not unicodedata.combining(char)
    )
    return " ".join(without_accents.lower().split())


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_empresareceita"),
    ]

    operations = [
        migrations.AddField(
            model_name="empresareceita",
            name="municipio_normalizado",
            field=models.CharField(blank=True, db_index=True, max_length=120),
        ),
        migrations.AddField(
            model_name="empresareceita",
            name="nome_fantasia_normalizado",
            field=models.CharField(blank=True, db_index=True, max_length=255),
        ),
        migrations.AddField(
            model_name="empresareceita",
            name="razao_social_normalizada",
            field=models.CharField(blank=True, db_index=True, max_length=255),
        ),
        migrations.RunPython(
            populate_normalized_fields,
            migrations.RunPython.noop,
        ),
    ]
