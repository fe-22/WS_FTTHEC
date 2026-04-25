import unicodedata

from django.db import models


class Inscricao(models.Model):
    nome = models.CharField(max_length=100)
    email = models.EmailField()
    telefone = models.CharField(max_length=20, blank=True)
    empresa = models.CharField(max_length=100, blank=True)
    cargo = models.CharField(max_length=100, blank=True)
    mensagem = models.TextField(blank=True)
    data_inscricao = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nome} - {self.email}"


class EmpresaReceita(models.Model):
    ENRICHMENT_STATUS_CHOICES = [
        ("pending", "Pendente"),
        ("done", "Concluido"),
        ("failed", "Falhou"),
    ]

    cnpj = models.CharField(max_length=14, unique=True, db_index=True)
    matriz_filial = models.CharField(max_length=1, blank=True)
    razao_social = models.CharField(max_length=255, db_index=True)
    razao_social_normalizada = models.CharField(max_length=255, blank=True, db_index=True)
    nome_fantasia = models.CharField(max_length=255, blank=True)
    nome_fantasia_normalizado = models.CharField(max_length=255, blank=True, db_index=True)
    situacao_cadastral = models.CharField(max_length=2, blank=True, db_index=True)
    data_situacao_cadastral = models.DateField(null=True, blank=True)
    motivo_situacao_cadastral = models.CharField(max_length=2, blank=True)
    natureza_juridica = models.CharField(max_length=4, blank=True, db_index=True)
    data_abertura = models.DateField(null=True, blank=True, db_index=True)
    cnae_principal = models.CharField(max_length=7, blank=True, db_index=True)
    cnaes_secundarios = models.TextField(blank=True)
    porte_empresa = models.CharField(max_length=2, blank=True)
    logradouro = models.CharField(max_length=255, blank=True)
    numero = models.CharField(max_length=20, blank=True)
    complemento = models.CharField(max_length=255, blank=True)
    bairro = models.CharField(max_length=120, blank=True)
    cep = models.CharField(max_length=8, blank=True)
    municipio = models.CharField(max_length=120, blank=True, db_index=True)
    municipio_normalizado = models.CharField(max_length=120, blank=True, db_index=True)
    uf = models.CharField(max_length=2, blank=True, db_index=True)
    telefone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    site_url = models.URLField(blank=True)
    contatos_publicos = models.JSONField(default=dict, blank=True)
    enrichment_source_urls = models.JSONField(default=list, blank=True)
    enrichment_status = models.CharField(
        max_length=10,
        choices=ENRICHMENT_STATUS_CHOICES,
        default="pending",
    )
    enrichment_checked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-data_abertura", "razao_social"]
        verbose_name = "Empresa Receita"
        verbose_name_plural = "Empresas Receita"

    def __str__(self):
        return f"{self.razao_social} ({self.cnpj})"

    def save(self, *args, **kwargs):
        self.razao_social_normalizada = normalize_search_text(self.razao_social)
        self.nome_fantasia_normalizado = normalize_search_text(self.nome_fantasia)
        self.municipio_normalizado = normalize_search_text(self.municipio)
        super().save(*args, **kwargs)


def normalize_search_text(value):
    if not value:
        return ""
    normalized = unicodedata.normalize("NFKD", value)
    without_accents = "".join(
        char for char in normalized if not unicodedata.combining(char)
    )
    return " ".join(without_accents.lower().split())
