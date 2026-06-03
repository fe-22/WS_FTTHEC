from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.utils.crypto import get_random_string

from core.models import CRMAccessRequest


TEMP_PASSWORD_CHARS = (
    "ABCDEFGHJKLMNPQRSTUVWXYZ"
    "abcdefghijkmnopqrstuvwxyz"
    "23456789"
    "!@#$%*?"
)


def generate_temporary_password(user=None, length=16):
    for _ in range(30):
        password = get_random_string(length, allowed_chars=TEMP_PASSWORD_CHARS)
        try:
            validate_password(password, user)
        except ValidationError:
            continue
        return password
    raise CommandError("Nao foi possivel gerar uma senha valida.")


class Command(BaseCommand):
    help = "Cria ou redefine a senha de um usuario do CRM e imprime a senha temporaria."

    def add_arguments(self, parser):
        parser.add_argument("identifier", help="Usuario ou e-mail do acesso CRM.")
        parser.add_argument(
            "--password",
            default="",
            help="Senha a definir. Se omitida, uma senha temporaria sera gerada.",
        )
        parser.add_argument(
            "--create",
            action="store_true",
            help="Cria o usuario se ele ainda nao existir.",
        )
        parser.add_argument("--email", default="", help="E-mail do usuario.")
        parser.add_argument("--name", default="", help="Nome do usuario.")
        parser.add_argument("--empresa", default="", help="Empresa vinculada ao CRM.")
        parser.add_argument("--telefone", default="", help="Telefone do usuario.")
        parser.add_argument(
            "--staff",
            action="store_true",
            help="Marca o usuario como staff.",
        )
        parser.add_argument(
            "--superuser",
            action="store_true",
            help="Marca o usuario como superuser e staff.",
        )
        parser.add_argument(
            "--no-crm-request",
            action="store_true",
            help="Nao cria/atualiza o registro CRMAccessRequest.",
        )
        parser.add_argument(
            "--hide-password",
            action="store_true",
            help="Nao imprime a senha no stdout. Use em rotinas de startup.",
        )

    def handle(self, *args, **options):
        User = get_user_model()
        identifier = options["identifier"].strip()
        if not identifier:
            raise CommandError("Informe um usuario ou e-mail.")

        user = (
            User.objects.filter(Q(username__iexact=identifier) | Q(email__iexact=identifier))
            .order_by("id")
            .first()
        )
        created = False
        if user is None:
            if not options["create"]:
                raise CommandError(
                    "Usuario nao encontrado. Use --create para criar um novo acesso."
                )
            user = User(username=identifier.lower() if "@" in identifier else identifier)
            created = True

        email = options["email"].strip().lower()
        if email:
            user.email = email
        elif not user.email and "@" in identifier:
            user.email = identifier.lower()

        name = options["name"].strip()
        if name:
            user.first_name = name

        if options["superuser"]:
            user.is_superuser = True
            user.is_staff = True
        elif options["staff"]:
            user.is_staff = True

        user.is_active = True
        password = options["password"].strip() or generate_temporary_password(user)
        try:
            validate_password(password, user)
        except ValidationError as exc:
            raise CommandError("Senha invalida: " + " ".join(exc.messages)) from exc

        user.set_password(password)
        user.save()

        if not options["no_crm_request"]:
            try:
                current_access = user.crm_access_request
            except CRMAccessRequest.DoesNotExist:
                current_access = None
            CRMAccessRequest.objects.update_or_create(
                user=user,
                defaults={
                    "empresa": options["empresa"].strip()
                    or (current_access.empresa if current_access else "")
                    or "Acesso CRM",
                    "telefone": options["telefone"].strip()
                    or (current_access.telefone if current_access else ""),
                    "status": "active",
                },
            )

        self.stdout.write(self.style.SUCCESS("Acesso CRM atualizado."))
        self.stdout.write(f"Acao: {'criado' if created else 'atualizado'}")
        self.stdout.write(f"Usuario: {user.username}")
        self.stdout.write(f"E-mail: {user.email or '-'}")
        if options["hide_password"]:
            self.stdout.write("Senha temporaria: [oculta]")
        else:
            self.stdout.write(f"Senha temporaria: {password}")
