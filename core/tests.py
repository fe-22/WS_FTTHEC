import tempfile
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .models import EmpresaReceita
from .services import (
    _match_estabelecimento_row,
    build_empresa_queryset,
    export_receita_filtered_csv,
    _extract_release_names,
    _resolve_receita_release,
    parse_municipios,
    parse_segmentos,
    parse_situacao_cadastral,
)


class CrmEmpresasApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="crmuser",
            password="senha-forte-123",
        )
        self.client = Client()
        self.client.login(username="crmuser", password="senha-forte-123")

        EmpresaReceita.objects.create(
            cnpj="12345678000190",
            razao_social="ACME SOFTWARE LTDA",
            nome_fantasia="ACME",
            data_abertura="2024-01-10",
            cnae_principal="6201500",
            cnaes_secundarios="6202300,6203100",
            uf="SP",
            municipio="Campinas",
            situacao_cadastral="02",
        )
        EmpresaReceita.objects.create(
            cnpj="98765432000110",
            razao_social="BETA LOGISTICA LTDA",
            data_abertura="2023-05-20",
            cnae_principal="4930202",
            uf="MG",
            municipio="Belo Horizonte",
            situacao_cadastral="02",
        )

    def test_api_filtra_por_data_uf_e_segmento(self):
        response = self.client.get(
            reverse("crm_empresas_api"),
            {
                "data_inicio": "2024-01-01",
                "segmentos": "6201500",
                "uf": "sp",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["results"][0]["razao_social"], "ACME SOFTWARE LTDA")

    def test_api_filtra_por_cnae_secundario(self):
        response = self.client.get(
            reverse("crm_empresas_api"),
            {"segmentos": "6202300"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["results"][0]["cnpj"], "12345678000190")

    def test_api_filtra_por_multiplos_municipios(self):
        response = self.client.get(
            reverse("crm_empresas_api"),
            {"municipios": "Campinas, Belo Horizonte"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["count"], 2)

    def test_api_busca_textual_aceita_cnpj_formatado(self):
        response = self.client.get(
            reverse("crm_empresas_api"),
            {"q": "12.345.678/0001-90"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["results"][0]["cnpj"], "12345678000190")

    def test_api_filtra_municipio_sem_acentos(self):
        EmpresaReceita.objects.create(
            cnpj="11122233000144",
            razao_social="COMERCIO DO ABC LTDA",
            razao_social_normalizada="comercio do abc ltda",
            nome_fantasia="ABC",
            nome_fantasia_normalizado="abc",
            municipio="São Bernardo do Campo",
            municipio_normalizado="sao bernardo do campo",
            uf="SP",
            situacao_cadastral="02",
        )

        response = self.client.get(
            reverse("crm_empresas_api"),
            {"municipio": "Sao bernardo do campo"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["results"][0]["municipio"], "São Bernardo do Campo")

    def test_api_busca_textual_aceita_cnae_mascarado(self):
        response = self.client.get(
            reverse("crm_empresas_api"),
            {"q": "6201-5/00"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["results"][0]["cnpj"], "12345678000190")

    @patch("core.views.sync_receita_filtered_import")
    def test_crm_sincroniza_receita_com_filtros(self, sync_mock):
        sync_mock.return_value = {
            "release": "2026-04",
            "matched": 1,
            "created": 1,
            "updated": 0,
        }

        response = self.client.post(
            reverse("crm"),
            {
                "action": "sincronizar_receita",
                "uf": "sp",
                "segmentos": "6201500",
                "limit": "250",
                "situacao_cadastral": "ativa",
                "matriz_only": "on",
            },
        )

        self.assertEqual(response.status_code, 302)
        sync_mock.assert_called_once_with(
            cache_dir=Path("C:/Users/Usuário/OneDrive/ws_fthec/var/receita_cache"),
            release=None,
            data_inicio="",
            data_fim="",
            segmentos="6201500",
            uf="SP",
            municipio="",
            municipios="",
            situacao_cadastral="ativa",
            matriz_only=True,
            limit=250,
        )

    @patch("core.views.sync_receita_filtered_import")
    def test_crm_nao_sincroniza_sem_recorte(self, sync_mock):
        response = self.client.post(
            reverse("crm"),
            {
                "action": "sincronizar_receita",
                "limit": "250",
            },
        )

        self.assertEqual(response.status_code, 302)
        sync_mock.assert_not_called()


class ReceitaHelpersTests(TestCase):
    def test_extract_release_names_aceita_mes_e_data(self):
        html = """
        <a href="2026-01/">2026-01/</a>
        <a href="2026-02-14/">2026-02-14/</a>
        <a href="2025-12/">2025-12/</a>
        """
        self.assertEqual(
            _extract_release_names(html),
            ["2025-12", "2026-01", "2026-02-14"],
        )

    def test_resolve_receita_release_usa_data_mais_recente_do_mes(self):
        resolved = _resolve_receita_release(
            "2026-02",
            ["2026-01", "2026-02-10", "2026-02-14"],
        )
        self.assertEqual(resolved, "2026-02-14")

    def test_parse_segmentos_normaliza_codigo_mascarado(self):
        self.assertEqual(parse_segmentos("4781-4/00"), ["4781400"])

    def test_parse_situacao_cadastral_aceita_alias(self):
        self.assertEqual(parse_situacao_cadastral("regular"), "02")
        self.assertEqual(parse_situacao_cadastral("ativa"), "02")
        self.assertEqual(parse_situacao_cadastral("8"), "08")

    def test_parse_municipios_normaliza_lista(self):
        self.assertEqual(
            parse_municipios("Santo André, São Bernardo do Campo,  Diadema "),
            ["santo andré", "são bernardo do campo", "diadema"],
        )

    def test_export_receita_filtered_csv_gera_arquivo_normalizado(self):
        collected = {
            "release": "2026-04",
            "downloaded_files": [],
            "matched": 1,
            "records": [
                {
                    "cnpj": "11222333000181",
                    "cnpj_basico": "11222333",
                    "matriz_filial": "1",
                    "nome_fantasia": "LOJA TESTE",
                    "situacao_cadastral": "02",
                    "data_situacao_cadastral": None,
                    "motivo_situacao_cadastral": "",
                    "data_abertura": None,
                    "cnae_principal": "4781400",
                    "cnaes_secundarios": "4782201",
                    "logradouro": "RUA A",
                    "numero": "10",
                    "complemento": "",
                    "bairro": "CENTRO",
                    "cep": "13000000",
                    "municipio": "Campinas",
                    "uf": "SP",
                    "telefone": "(19) 999999999",
                    "email": "contato@lojateste.com.br",
                }
            ],
            "empresas_por_basico": {
                "11222333": {
                    "razao_social": "LOJA TESTE LTDA",
                    "natureza_juridica": "2062",
                    "porte_empresa": "03",
                }
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "receita_normalizada.csv"
            with patch("core.services._collect_receita_filtered_records", return_value=collected):
                summary = export_receita_filtered_csv(
                    output_path=output_path,
                    cache_dir=temp_dir,
                    uf="SP",
                    limit=1,
                )

            self.assertEqual(summary["matched"], 1)
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("cnpj;matriz_filial;razao_social;nome_fantasia", content)
            self.assertIn("11222333000181;1;LOJA TESTE LTDA;LOJA TESTE;02", content)

    def test_match_estabelecimento_row_filtra_matriz(self):
        row = [
            "11222333",
            "0001",
            "81",
            "2",
            "LOJA TESTE",
            "02",
            "20260410",
            "",
            "",
            "",
            "20260410",
            "4781400",
            "4782201",
            "RUA",
            "A",
            "10",
            "",
            "CENTRO",
            "13000000",
            "SP",
            "3509502",
            "19",
            "99999999",
            "",
            "",
            "",
            "",
            "contato@lojateste.com.br",
            "",
            "",
        ]
        result = _match_estabelecimento_row(
            row,
            {
                "data_inicio": None,
                "data_fim": None,
                "segmentos": [],
                "uf": "",
                "municipios": [],
                "situacao_cadastral": "02",
                "matriz_only": True,
            },
            {"3509502": "Campinas"},
        )

        self.assertFalse(result)

    def test_build_empresa_queryset_filtra_por_municipios(self):
        EmpresaReceita.objects.create(
            cnpj="11111111000111",
            razao_social="EMPRESA A LTDA",
            municipio="Campinas",
            uf="SP",
            situacao_cadastral="02",
        )
        EmpresaReceita.objects.create(
            cnpj="22222222000122",
            razao_social="EMPRESA B LTDA",
            municipio="Belo Horizonte",
            uf="MG",
            situacao_cadastral="02",
        )
        queryset = build_empresa_queryset({"municipios": "Campinas, Belo Horizonte"})
        self.assertEqual(queryset.count(), 2)
