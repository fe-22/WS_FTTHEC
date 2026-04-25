from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from core.services import sync_receita_filtered_import


class Command(BaseCommand):
    help = (
        "Baixa automaticamente a referencia mensal oficial da Receita e importa "
        "empresas filtradas para a tabela EmpresaReceita."
    )

    def add_arguments(self, parser):
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
            help="Importa apenas estabelecimentos matriz.",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=500,
            help="Quantidade maxima de estabelecimentos a importar nesta execucao.",
        )
        parser.add_argument(
            "--cache-dir",
            default=str(Path(settings.BASE_DIR) / "var" / "receita_cache"),
            help="Diretorio local para armazenar os ZIPs baixados.",
        )

    def handle(self, *args, **options):
        release = options["release"]
        data_inicio = options["data_inicio"]
        data_fim = options["data_fim"]
        segmentos = options["segmentos"]
        uf = options["uf"]
        municipio = options["municipio"]
        municipios = options["municipios"]
        situacao_cadastral = options["situacao_cadastral"]
        matriz_only = options["matriz_only"]
        limit = options["limit"]
        cache_dir = options["cache_dir"]

        if not any([data_inicio, data_fim, segmentos, uf, municipio, municipios]):
            raise CommandError(
                "Informe ao menos um filtro de recorte para evitar importacao massiva. "
                "Ex.: --uf SP --segmentos 4781400"
            )

        try:
            summary = sync_receita_filtered_import(
                cache_dir=cache_dir,
                release=release,
                data_inicio=data_inicio,
                data_fim=data_fim,
                segmentos=segmentos,
                uf=uf,
                municipio=municipio,
                municipios=municipios,
                situacao_cadastral=situacao_cadastral,
                matriz_only=matriz_only,
                limit=limit,
            )
        except Exception as exc:
            raise CommandError(f"Falha na sincronizacao automatica da Receita: {exc}") from exc

        self.stdout.write(
            self.style.SUCCESS(
                "Sincronizacao concluida. "
                f"Referencia: {summary['release']}. "
                f"Correspondencias: {summary['matched']}. "
                f"Criados: {summary['created']}. "
                f"Atualizados: {summary['updated']}."
            )
        )
