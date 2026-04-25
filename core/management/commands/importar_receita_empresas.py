from django.core.management.base import BaseCommand, CommandError

from core.services import import_empresas_from_csv


class Command(BaseCommand):
    help = (
        "Importa empresas de um CSV normalizado da Receita para a tabela EmpresaReceita."
    )

    def add_arguments(self, parser):
        parser.add_argument("csv_path", help="Caminho do arquivo CSV com cabecalho.")
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Quantidade maxima de linhas a importar.",
        )

    def handle(self, *args, **options):
        csv_path = options["csv_path"]
        limit = options["limit"]

        try:
            summary = import_empresas_from_csv(csv_path, limit=limit)
        except FileNotFoundError as exc:
            raise CommandError(f"Arquivo nao encontrado: {csv_path}") from exc
        except Exception as exc:
            raise CommandError(f"Falha na importacao: {exc}") from exc

        self.stdout.write(
            self.style.SUCCESS(
                "Importacao concluida. "
                f"Criados: {summary['created']}. "
                f"Atualizados: {summary['updated']}."
            )
        )
