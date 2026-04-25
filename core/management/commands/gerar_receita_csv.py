from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from core.services import export_receita_filtered_csv


class Command(BaseCommand):
    help = (
        "Baixa os arquivos oficiais da Receita, aplica os filtros e gera um CSV "
        "normalizado para exportacao ou validacao local."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "output_path",
            help="Caminho do CSV de saida com cabecalho normalizado.",
        )
        parser.add_argument(
            "--mes",
            dest="release",
            help="Referencia mensal da Receita no formato YYYY-MM. Padrao: ultima disponivel.",
        )
        parser.add_argument("--data-inicio", default="", help="Filtro de abertura.")
        parser.add_argument("--data-fim", default="", help="Filtro de abertura.")
        parser.add_argument(
            "--segmentos",
            default="",
            help="Lista de CNAEs separada por virgula.",
        )
        parser.add_argument("--uf", default="", help="UF do estabelecimento.")
        parser.add_argument("--municipio", default="", help="Municipio do estabelecimento.")
        parser.add_argument(
            "--municipios",
            default="",
            help="Lista de municipios separada por virgula.",
        )
        parser.add_argument(
            "--situacao-cadastral",
            default="02",
            help="Codigo ou alias da situacao cadastral. Ex.: 02, ativa, regular.",
        )
        parser.add_argument(
            "--matriz-only",
            action="store_true",
            help="Exporta apenas estabelecimentos matriz.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=500,
            help="Quantidade maxima de estabelecimentos no CSV gerado.",
        )
        parser.add_argument(
            "--cache-dir",
            default=str(Path(settings.BASE_DIR) / "var" / "receita_cache"),
            help="Diretorio local para armazenar os ZIPs baixados.",
        )

    def handle(self, *args, **options):
        if not any(
            [
                options["data_inicio"],
                options["data_fim"],
                options["segmentos"],
                options["uf"],
                options["municipio"],
                options["municipios"],
            ]
        ):
            raise CommandError(
                "Informe ao menos um filtro de recorte para evitar gerar uma base massiva. "
                "Ex.: --uf SP --segmentos 4781400"
            )

        try:
            summary = export_receita_filtered_csv(
                output_path=options["output_path"],
                cache_dir=options["cache_dir"],
                release=options["release"],
                data_inicio=options["data_inicio"],
                data_fim=options["data_fim"],
                segmentos=options["segmentos"],
                uf=options["uf"],
                municipio=options["municipio"],
                municipios=options["municipios"],
                situacao_cadastral=options["situacao_cadastral"],
                matriz_only=options["matriz_only"],
                limit=options["limit"],
            )
        except Exception as exc:
            raise CommandError(f"Falha ao gerar CSV da Receita: {exc}") from exc

        self.stdout.write(
            self.style.SUCCESS(
                "CSV gerado com sucesso. "
                f"Referencia: {summary['release']}. "
                f"Correspondencias: {summary['matched']}. "
                f"Arquivo: {summary['output_path']}."
            )
        )
