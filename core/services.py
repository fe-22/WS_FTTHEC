import csv
import html
import io
import re
import zipfile
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from django.db.models import Q
from django.utils import timezone

from .models import EmpresaReceita, normalize_search_text

DATE_INPUT_FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%Y%m%d")
RELEASE_INPUT_FORMATS = ("%Y-%m-%d", "%Y-%m")
PERSONAL_EMAIL_DOMAINS = {
    "gmail.com",
    "hotmail.com",
    "hotmail.com.br",
    "outlook.com",
    "outlook.com.br",
    "yahoo.com",
    "yahoo.com.br",
    "icloud.com",
    "uol.com.br",
    "bol.com.br",
    "terra.com.br",
}
PHONE_RE = re.compile(r"(?:\+?55\s*)?(?:\(?\d{2}\)?\s*)?(?:9?\d{4})[-\s]?\d{4}")
EMAIL_RE = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
LINK_RE = re.compile(
    r"""href=["'](?P<href>[^"']+)["']""",
    re.IGNORECASE,
)
CONTACT_LINK_TERMS = ("contato", "contact", "fale-conosco", "atendimento", "sobre")
USER_AGENT = "FTHEC-CRM/1.0 (+https://fthec.com.br)"
RECEITA_BASE_URLS = [
    "https://arquivos.receitafederal.gov.br/dados/cnpj/dados_abertos_cnpj/",
    "https://arquivos.receitafederal.gov.br/cnpj/dados_abertos_cnpj/",
    "https://dados-abertos-rf-cnpj.casadosdados.com.br/arquivos/",
]
RELEASE_RE = re.compile(r'href="(?P<release>\d{4}-\d{2}(?:-\d{2})?)/"', re.IGNORECASE)
ZIP_LINK_RE = re.compile(r'href="(?P<name>[^"]+\.zip)"', re.IGNORECASE)


def normalize_digits(value):
    return re.sub(r"\D", "", value or "")


def normalize_cnae(value):
    return normalize_digits(value)[:7]


def parse_date_input(value):
    if not value:
        return None
    for fmt in DATE_INPUT_FORMATS:
        try:
            return timezone.datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def parse_situacao_cadastral(value):
    raw = (value or "").strip().lower()
    if not raw:
        return ""

    aliases = {
        "ativa": "02",
        "ativo": "02",
        "regular": "02",
        "02": "02",
        "suspensa": "03",
        "03": "03",
        "inapta": "04",
        "04": "04",
        "baixada": "08",
        "08": "08",
        "nula": "01",
        "01": "01",
    }
    return aliases.get(raw, raw.zfill(2) if raw.isdigit() else raw)


def parse_segmentos(value):
    if not value:
        return []
    if isinstance(value, str):
        raw_items = value.split(",")
    else:
        raw_items = value
    segmentos = []
    for item in raw_items:
        code = normalize_cnae(item)
        if code:
            segmentos.append(code)
    return list(dict.fromkeys(segmentos))


def parse_municipios(value):
    if not value:
        return []
    if isinstance(value, str):
        raw_items = value.split(",")
    else:
        raw_items = value
    municipios = []
    for item in raw_items:
        normalized = _normalize_municipio_name(item)
        if normalized:
            municipios.append(normalized)
    return list(dict.fromkeys(municipios))


def format_cnpj(value):
    digits = normalize_digits(value)
    if len(digits) != 14:
        return value
    return (
        f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/"
        f"{digits[8:12]}-{digits[12:]}"
    )


def split_secondary_cnaes(value):
    return [code for code in parse_segmentos((value or "").split(",")) if code]


def build_empresa_queryset(params):
    queryset = EmpresaReceita.objects.all()

    termo = (params.get("q") or "").strip()
    if termo:
        termo_normalizado = normalize_search_text(termo)
        termo_digitos = normalize_digits(termo)
        termos_cnae = parse_segmentos(termo)
        filter_q = (
            Q(razao_social__icontains=termo)
            | Q(nome_fantasia__icontains=termo)
            | Q(razao_social_normalizada__icontains=termo_normalizado)
            | Q(nome_fantasia_normalizado__icontains=termo_normalizado)
            | Q(cnpj__icontains=termo_digitos)
            | Q(municipio__icontains=termo)
            | Q(municipio_normalizado__icontains=termo_normalizado)
        )
        if termos_cnae:
            for segmento in termos_cnae:
                filter_q |= Q(cnae_principal=segmento) | Q(
                    cnaes_secundarios__icontains=segmento
                )
        queryset = queryset.filter(filter_q)

    data_inicio = parse_date_input(params.get("data_inicio"))
    if data_inicio:
        queryset = queryset.filter(data_abertura__gte=data_inicio)

    data_fim = parse_date_input(params.get("data_fim"))
    if data_fim:
        queryset = queryset.filter(data_abertura__lte=data_fim)

    uf = (params.get("uf") or "").strip().upper()
    if uf:
        queryset = queryset.filter(uf=uf)

    municipios = parse_municipios(params.get("municipios"))
    municipio = (params.get("municipio") or "").strip()
    if municipio:
        municipios.extend(parse_municipios(municipio))
    if municipios:
        filter_q = Q()
        for municipio_nome in dict.fromkeys(municipios):
            filter_q |= Q(municipio__icontains=municipio_nome) | Q(
                municipio_normalizado__icontains=municipio_nome
            )
        queryset = queryset.filter(filter_q)

    situacao_cadastral = (params.get("situacao_cadastral") or "").strip()
    if situacao_cadastral:
        queryset = queryset.filter(
            situacao_cadastral=parse_situacao_cadastral(situacao_cadastral)
        )

    segmentos = parse_segmentos(params.get("segmentos"))
    if segmentos:
        filter_q = Q()
        for segmento in segmentos:
            filter_q |= Q(cnae_principal=segmento) | Q(
                cnaes_secundarios__icontains=segmento
            )
        queryset = queryset.filter(filter_q)

    return queryset.distinct()


def serialize_empresa(empresa):
    return {
        "id": empresa.id,
        "cnpj": empresa.cnpj,
        "cnpj_formatado": format_cnpj(empresa.cnpj),
        "razao_social": empresa.razao_social,
        "nome_fantasia": empresa.nome_fantasia,
        "situacao_cadastral": empresa.situacao_cadastral,
        "data_abertura": (
            empresa.data_abertura.isoformat() if empresa.data_abertura else None
        ),
        "cnae_principal": empresa.cnae_principal,
        "cnaes_secundarios": split_secondary_cnaes(empresa.cnaes_secundarios),
        "uf": empresa.uf,
        "municipio": empresa.municipio,
        "telefone": empresa.telefone,
        "email": empresa.email,
        "site_url": empresa.site_url,
        "contatos_publicos": empresa.contatos_publicos,
        "enrichment_status": empresa.enrichment_status,
        "enrichment_checked_at": (
            empresa.enrichment_checked_at.isoformat()
            if empresa.enrichment_checked_at
            else None
        ),
    }


def _normalize_url(url):
    if not url:
        return ""
    if not url.startswith(("http://", "https://")):
        return f"https://{url}"
    return url


def _institutional_emails(emails, company_domain=""):
    filtered = []
    for email in sorted(set(email.lower() for email in emails)):
        domain = email.split("@", 1)[-1]
        if domain in PERSONAL_EMAIL_DOMAINS:
            continue
        if company_domain and company_domain not in domain:
            continue
        filtered.append(email)
    return filtered


def _extract_links(html, base_url):
    urls = []
    for match in LINK_RE.finditer(html or ""):
        href = match.group("href").strip()
        if not href or href.startswith(("mailto:", "tel:", "#", "javascript:")):
            continue
        urls.append(urljoin(base_url, href))
    return urls


def discover_site_candidates(empresa, max_results=3):
    urls = []
    if empresa.site_url:
        urls.append(_normalize_url(empresa.site_url))

    if urls:
        return urls[:max_results]

    query = f'"{empresa.razao_social}" {empresa.uf} site oficial'
    try:
        response = requests.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers={"User-Agent": USER_AGENT},
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException:
        return urls

    for href in _extract_links(response.text, "https://html.duckduckgo.com/"):
        parsed = urlparse(href)
        if not parsed.netloc:
            continue
        if "duckduckgo.com" in parsed.netloc:
            continue
        if href not in urls:
            urls.append(href)
        if len(urls) >= max_results:
            break
    return urls


def _fetch_page(url):
    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT},
        timeout=10,
    )
    response.raise_for_status()
    return response.text


def discover_public_contacts(empresa, discover_site=True):
    candidate_urls = discover_site_candidates(empresa) if discover_site else []
    if empresa.site_url:
        candidate_urls.insert(0, _normalize_url(empresa.site_url))

    normalized_candidates = []
    for url in candidate_urls:
        clean = _normalize_url(url)
        if clean and clean not in normalized_candidates:
            normalized_candidates.append(clean)

    emails = set()
    phones = set()
    forms = set()
    social_links = set()
    crawled_urls = []
    company_domain = ""

    for url in normalized_candidates[:3]:
        try:
            html = _fetch_page(url)
        except requests.RequestException:
            continue

        crawled_urls.append(url)
        parsed = urlparse(url)
        company_domain = parsed.netloc.replace("www.", "")
        emails.update(EMAIL_RE.findall(html))
        phones.update(match.group(0).strip() for match in PHONE_RE.finditer(html))

        for link in _extract_links(html, url):
            parsed_link = urlparse(link)
            if parsed_link.netloc and company_domain not in parsed_link.netloc:
                if "linkedin.com/company/" in link:
                    social_links.add(link)
                continue
            if any(term in link.lower() for term in CONTACT_LINK_TERMS):
                forms.add(link)

        for contact_url in list(forms)[:2]:
            try:
                contact_html = _fetch_page(contact_url)
            except requests.RequestException:
                continue
            crawled_urls.append(contact_url)
            emails.update(EMAIL_RE.findall(contact_html))
            phones.update(match.group(0).strip() for match in PHONE_RE.finditer(contact_html))

    contatos_publicos = {
        "emails": _institutional_emails(emails, company_domain=company_domain),
        "telefones": sorted(set(phones)),
        "formularios": sorted(forms),
        "redes_sociais": sorted(social_links),
    }
    return contatos_publicos, crawled_urls


IMPORT_FIELD_MAP = {
    "cnpj": "cnpj",
    "matriz_filial": "matriz_filial",
    "razao_social": "razao_social",
    "nome_fantasia": "nome_fantasia",
    "situacao_cadastral": "situacao_cadastral",
    "data_situacao_cadastral": "data_situacao_cadastral",
    "motivo_situacao_cadastral": "motivo_situacao_cadastral",
    "natureza_juridica": "natureza_juridica",
    "data_abertura": "data_abertura",
    "cnae_principal": "cnae_principal",
    "cnaes_secundarios": "cnaes_secundarios",
    "porte_empresa": "porte_empresa",
    "logradouro": "logradouro",
    "numero": "numero",
    "complemento": "complemento",
    "bairro": "bairro",
    "cep": "cep",
    "municipio": "municipio",
    "uf": "uf",
    "telefone": "telefone",
    "email": "email",
    "site_url": "site_url",
}
EXPORT_FIELDNAMES = list(IMPORT_FIELD_MAP.keys())


def detect_csv_dialect(content):
    sample = content[:4096]
    try:
        return csv.Sniffer().sniff(sample, delimiters=";,|\t")
    except csv.Error:
        return csv.excel


def import_empresas_from_csv(path, limit=None):
    created = 0
    updated = 0

    with open(path, "r", encoding="utf-8-sig", newline="") as file_handle:
        sample = file_handle.read(4096)
        file_handle.seek(0)
        reader = csv.DictReader(file_handle, dialect=detect_csv_dialect(sample))

        for index, row in enumerate(reader, start=1):
            if limit and index > limit:
                break

            payload = {}
            for source_name, target_name in IMPORT_FIELD_MAP.items():
                value = (row.get(source_name) or "").strip()
                if target_name == "cnpj":
                    value = normalize_digits(value)
                elif target_name in {"cnae_principal"}:
                    value = normalize_cnae(value)
                elif target_name in {"cnaes_secundarios"}:
                    value = ",".join(parse_segmentos(value.split(",")))
                elif target_name in {"data_abertura", "data_situacao_cadastral"}:
                    value = parse_date_input(value)
                elif target_name == "uf":
                    value = value.upper()
                payload[target_name] = value

            payload["razao_social_normalizada"] = normalize_search_text(
                payload.get("razao_social")
            )
            payload["nome_fantasia_normalizado"] = normalize_search_text(
                payload.get("nome_fantasia")
            )
            payload["municipio_normalizado"] = normalize_search_text(
                payload.get("municipio")
            )

            if len(payload.get("cnpj", "")) != 14:
                continue

            _, was_created = EmpresaReceita.objects.update_or_create(
                cnpj=payload["cnpj"],
                defaults=payload,
            )
            if was_created:
                created += 1
            else:
                updated += 1

    return {"created": created, "updated": updated}


def fetch_receita_latest_release(session=None):
    http = session or requests.Session()
    _, response = _fetch_receita_base_listing(http)
    releases = _extract_release_names(response.text)
    if not releases:
        raise ValueError("Nao foi possivel localizar as referencias da Receita.")
    return releases[-1]


def fetch_receita_release_files(release, session=None):
    http = session or requests.Session()
    base_url, response = _fetch_receita_base_listing(http)
    resolved_release = _resolve_receita_release(
        requested_release=release,
        available_releases=_extract_release_names(response.text),
    )
    release_url = urljoin(base_url, f"{resolved_release}/")
    response = http.get(
        release_url,
        headers={"User-Agent": USER_AGENT},
        timeout=30,
    )
    response.raise_for_status()

    files = []
    for name in ZIP_LINK_RE.findall(response.text):
        if name not in files:
            files.append(html.unescape(name))
    return resolved_release, release_url, files


def _fetch_receita_base_listing(http):
    last_error = None
    for base_url in RECEITA_BASE_URLS:
        try:
            response = http.get(
                base_url,
                headers={"User-Agent": USER_AGENT},
                timeout=30,
            )
            if response.ok and not _is_serpro_error_page(response.text):
                return base_url, response
            response.raise_for_status()
            return base_url, response
        except requests.RequestException as exc:
            last_error = exc
    if last_error:
        raise last_error
    raise ValueError("Nao foi possivel acessar a base publica da Receita.")


def download_file(url, destination, session=None):
    http = session or requests.Session()
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_destination = destination.with_suffix(f"{destination.suffix}.part")

    with http.get(url, headers={"User-Agent": USER_AGENT}, timeout=60, stream=True) as response:
        response.raise_for_status()
        with temp_destination.open("wb") as output:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    output.write(chunk)
    temp_destination.replace(destination)
    return destination


def ensure_valid_zip_download(url, destination, session=None):
    destination = Path(destination)
    if destination.exists() and _is_valid_zip_file(destination):
        return destination
    if destination.exists():
        try:
            destination.unlink()
        except OSError:
            destination = destination.with_name(
                f"{destination.stem}__refresh{destination.suffix}"
            )
    downloaded = download_file(url, destination, session=session)
    if not _is_valid_zip_file(downloaded):
        if downloaded.exists():
            downloaded.unlink()
        raise ValueError(f"Arquivo baixado invalido para {downloaded.name}.")
    return downloaded


def _extract_release_names(html_content):
    releases = sorted(set(RELEASE_RE.findall(html_content or "")), key=_release_sort_key)
    return releases


def _release_sort_key(value):
    for fmt in RELEASE_INPUT_FORMATS:
        try:
            return timezone.datetime.strptime(value, fmt)
        except ValueError:
            continue
    return timezone.datetime.min


def _resolve_receita_release(requested_release, available_releases):
    if not available_releases:
        raise ValueError("Nao ha referencias disponiveis para a fonte configurada.")

    if not requested_release:
        return available_releases[-1]

    requested_release = requested_release.strip()
    if requested_release in available_releases:
        return requested_release

    if re.fullmatch(r"\d{4}-\d{2}", requested_release):
        same_month = [item for item in available_releases if item.startswith(f"{requested_release}-")]
        if same_month:
            return same_month[-1]

    raise ValueError(
        "Referencia da Receita nao encontrada. "
        f"Solicitada: {requested_release}. Ultima disponivel: {available_releases[-1]}."
    )


def _is_serpro_error_page(html_content):
    normalized = (html_content or "").lower()
    return "serpro+" in normalized and "requer" not in normalized


def _open_first_zip_member(zip_path):
    archive = zipfile.ZipFile(zip_path)
    members = [item for item in archive.namelist() if not item.endswith("/")]
    if not members:
        archive.close()
        raise ValueError(f"Arquivo ZIP sem conteudo: {zip_path}")
    return archive, members[0]


def _is_valid_zip_file(zip_path):
    try:
        with zipfile.ZipFile(zip_path) as archive:
            return archive.testzip() is None
    except (OSError, zipfile.BadZipFile, zipfile.LargeZipFile):
        return False


def iter_receita_zip_rows(zip_path):
    archive, member_name = _open_first_zip_member(zip_path)
    try:
        with archive.open(member_name) as raw_stream:
            with io.TextIOWrapper(raw_stream, encoding="latin-1", newline="") as decoded:
                reader = csv.reader(decoded, delimiter=";")
                for row in reader:
                    yield row
    finally:
        archive.close()


def load_receita_municipios(zip_path):
    municipios = {}
    for row in iter_receita_zip_rows(zip_path):
        if len(row) < 2:
            continue
        codigo = normalize_digits(row[0])
        descricao = (row[1] or "").strip()
        if codigo and descricao:
            municipios[codigo] = descricao
    return municipios


def _normalize_municipio_name(value):
    return " ".join((value or "").strip().lower().split())


def _build_phone(ddd, number):
    ddd = normalize_digits(ddd)
    number = normalize_digits(number)
    if not number:
        return ""
    if ddd:
        return f"({ddd}) {number}"
    return number


def _match_estabelecimento_row(row, filters, municipios_map):
    if len(row) < 30:
        return False

    if filters["matriz_only"] and (row[3] or "").strip() != "1":
        return False

    data_abertura = parse_date_input(row[10])
    if filters["data_inicio"] and (not data_abertura or data_abertura < filters["data_inicio"]):
        return False
    if filters["data_fim"] and (not data_abertura or data_abertura > filters["data_fim"]):
        return False

    if filters["uf"] and row[19].strip().upper() != filters["uf"]:
        return False

    situacao = parse_situacao_cadastral(row[5])
    if filters["situacao_cadastral"] and situacao != filters["situacao_cadastral"]:
        return False

    municipio_nome = municipios_map.get(normalize_digits(row[20]), row[20]).strip()
    if filters["municipios"]:
        municipio_normalizado = _normalize_municipio_name(municipio_nome)
        if not any(item in municipio_normalizado for item in filters["municipios"]):
            return False

    if filters["segmentos"]:
        cnaes = {normalize_cnae(row[11])}
        cnaes.update(parse_segmentos((row[12] or "").split(",")))
        if not any(segmento in cnaes for segmento in filters["segmentos"]):
            return False

    return True


def _serialize_estabelecimento_row(row, municipios_map):
    municipio_codigo = normalize_digits(row[20])
    telefone_1 = _build_phone(row[21], row[22])
    telefone_2 = _build_phone(row[23], row[24])
    telefones = [item for item in [telefone_1, telefone_2] if item]

    return {
        "cnpj": f"{normalize_digits(row[0])}{normalize_digits(row[1])}{normalize_digits(row[2])}",
        "cnpj_basico": normalize_digits(row[0]),
        "matriz_filial": (row[3] or "").strip(),
        "nome_fantasia": (row[4] or "").strip(),
        "situacao_cadastral": parse_situacao_cadastral(row[5]),
        "data_situacao_cadastral": parse_date_input(row[6]),
        "motivo_situacao_cadastral": (row[7] or "").strip(),
        "data_abertura": parse_date_input(row[10]),
        "cnae_principal": normalize_cnae(row[11]),
        "cnaes_secundarios": ",".join(parse_segmentos((row[12] or "").split(","))),
        "logradouro": " ".join(
            part.strip() for part in [row[13], row[14]] if (part or "").strip()
        ),
        "numero": (row[15] or "").strip(),
        "complemento": (row[16] or "").strip(),
        "bairro": (row[17] or "").strip(),
        "cep": normalize_digits(row[18]),
        "uf": (row[19] or "").strip().upper(),
        "municipio": municipios_map.get(municipio_codigo, (row[20] or "").strip()),
        "telefone": " / ".join(telefones),
        "email": (row[27] or "").strip().lower(),
    }


def _collect_receita_filtered_records(
    cache_dir,
    release=None,
    data_inicio=None,
    data_fim=None,
    segmentos=None,
    uf="",
    municipio="",
    municipios=None,
    situacao_cadastral="",
    matriz_only=False,
    limit=None,
    session=None,
):
    http = session or requests.Session()
    resolved_release, release_url, release_files = fetch_receita_release_files(
        release,
        session=http,
    )

    cache_path = Path(cache_dir) / resolved_release
    cache_path.mkdir(parents=True, exist_ok=True)

    municipios_zip_name = "Municipios.zip"
    estabelecimentos_zip_names = sorted(
        [name for name in release_files if name.startswith("Estabelecimentos")]
    )
    empresas_zip_names = sorted([name for name in release_files if name.startswith("Empresas")])

    if not estabelecimentos_zip_names or not empresas_zip_names or municipios_zip_name not in release_files:
        raise ValueError("Arquivos obrigatorios da Receita nao encontrados na referencia.")

    municipios_zip_path = cache_path / municipios_zip_name
    municipios_zip_path = ensure_valid_zip_download(
        urljoin(release_url, municipios_zip_name),
        municipios_zip_path,
        session=http,
    )
    municipios_map = load_receita_municipios(municipios_zip_path)

    municipios_filtrados = parse_municipios(municipios)
    if municipio:
        municipios_filtrados.extend(parse_municipios(municipio))

    filters = {
        "data_inicio": parse_date_input(data_inicio),
        "data_fim": parse_date_input(data_fim),
        "segmentos": parse_segmentos(segmentos or ""),
        "uf": (uf or "").strip().upper(),
        "municipios": list(dict.fromkeys(municipios_filtrados)),
        "situacao_cadastral": parse_situacao_cadastral(situacao_cadastral),
        "matriz_only": matriz_only,
    }

    matched_records = []
    matched_basicos = set()
    downloaded_files = [str(municipios_zip_path)]

    for zip_name in estabelecimentos_zip_names:
        zip_path = cache_path / zip_name
        zip_path = ensure_valid_zip_download(
            urljoin(release_url, zip_name),
            zip_path,
            session=http,
        )
        downloaded_files.append(str(zip_path))

        for row in iter_receita_zip_rows(zip_path):
            if not _match_estabelecimento_row(row, filters, municipios_map):
                continue
            record = _serialize_estabelecimento_row(row, municipios_map)
            if len(record["cnpj"]) != 14:
                continue
            matched_records.append(record)
            matched_basicos.add(record["cnpj_basico"])
            if limit and len(matched_records) >= limit:
                break
        if limit and len(matched_records) >= limit:
            break

    if not matched_records:
        return {
            "release": resolved_release,
            "downloaded_files": downloaded_files,
            "matched": 0,
            "records": [],
            "empresas_por_basico": {},
        }

    empresas_por_basico = {}
    for zip_name in empresas_zip_names:
        zip_path = cache_path / zip_name
        zip_path = ensure_valid_zip_download(
            urljoin(release_url, zip_name),
            zip_path,
            session=http,
        )
        downloaded_files.append(str(zip_path))

        for row in iter_receita_zip_rows(zip_path):
            if len(row) < 7:
                continue
            cnpj_basico = normalize_digits(row[0])
            if cnpj_basico not in matched_basicos:
                continue
            empresas_por_basico[cnpj_basico] = {
                "razao_social": (row[1] or "").strip(),
                "natureza_juridica": (row[2] or "").strip(),
                "porte_empresa": (row[5] or "").strip(),
            }
        if len(empresas_por_basico) >= len(matched_basicos):
            break

    return {
        "release": resolved_release,
        "downloaded_files": downloaded_files,
        "matched": len(matched_records),
        "records": matched_records,
        "empresas_por_basico": empresas_por_basico,
    }


def _build_normalized_record(record, empresas_por_basico):
    company_data = empresas_por_basico.get(record["cnpj_basico"], {})
    return {
        "cnpj": record["cnpj"],
        "matriz_filial": record["matriz_filial"],
        "razao_social": company_data.get(
            "razao_social", record["nome_fantasia"] or record["cnpj"]
        ),
        "nome_fantasia": record["nome_fantasia"],
        "situacao_cadastral": record["situacao_cadastral"],
        "data_situacao_cadastral": (
            record["data_situacao_cadastral"].isoformat()
            if record["data_situacao_cadastral"]
            else ""
        ),
        "motivo_situacao_cadastral": record["motivo_situacao_cadastral"],
        "natureza_juridica": company_data.get("natureza_juridica", ""),
        "data_abertura": (
            record["data_abertura"].isoformat() if record["data_abertura"] else ""
        ),
        "cnae_principal": record["cnae_principal"],
        "cnaes_secundarios": record["cnaes_secundarios"],
        "porte_empresa": company_data.get("porte_empresa", ""),
        "logradouro": record["logradouro"],
        "numero": record["numero"],
        "complemento": record["complemento"],
        "bairro": record["bairro"],
        "cep": record["cep"],
        "municipio": record["municipio"],
        "uf": record["uf"],
        "telefone": record["telefone"],
        "email": record["email"],
        "site_url": "",
    }


def export_receita_filtered_csv(
    output_path,
    cache_dir,
    release=None,
    data_inicio=None,
    data_fim=None,
    segmentos=None,
    uf="",
    municipio="",
    municipios=None,
    situacao_cadastral="",
    matriz_only=False,
    limit=None,
    session=None,
):
    summary = _collect_receita_filtered_records(
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
        session=session,
    )

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8", newline="") as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=EXPORT_FIELDNAMES, delimiter=";")
        writer.writeheader()
        for record in summary["records"]:
            writer.writerow(
                _build_normalized_record(record, summary["empresas_por_basico"])
            )

    summary["output_path"] = str(output)
    return summary


def sync_receita_filtered_import(
    cache_dir,
    release=None,
    data_inicio=None,
    data_fim=None,
    segmentos=None,
    uf="",
    municipio="",
    municipios=None,
    situacao_cadastral="",
    matriz_only=False,
    limit=None,
    session=None,
):
    summary = _collect_receita_filtered_records(
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
        session=session,
    )

    created = 0
    updated = 0

    for record in summary["records"]:
        normalized_record = _build_normalized_record(
            record, summary["empresas_por_basico"]
        )
        defaults = {
            "razao_social": normalized_record["razao_social"],
            "razao_social_normalizada": normalize_search_text(
                normalized_record["razao_social"]
            ),
            "natureza_juridica": normalized_record["natureza_juridica"],
            "porte_empresa": normalized_record["porte_empresa"],
            "matriz_filial": record["matriz_filial"],
            "nome_fantasia": record["nome_fantasia"],
            "nome_fantasia_normalizado": normalize_search_text(
                record["nome_fantasia"]
            ),
            "situacao_cadastral": record["situacao_cadastral"],
            "data_situacao_cadastral": record["data_situacao_cadastral"],
            "motivo_situacao_cadastral": record["motivo_situacao_cadastral"],
            "data_abertura": record["data_abertura"],
            "cnae_principal": record["cnae_principal"],
            "cnaes_secundarios": record["cnaes_secundarios"],
            "logradouro": record["logradouro"],
            "numero": record["numero"],
            "complemento": record["complemento"],
            "bairro": record["bairro"],
            "cep": record["cep"],
            "municipio": record["municipio"],
            "municipio_normalizado": normalize_search_text(record["municipio"]),
            "uf": record["uf"],
            "telefone": record["telefone"],
            "email": record["email"],
            "enrichment_status": "pending",
        }
        _, was_created = EmpresaReceita.objects.update_or_create(
            cnpj=record["cnpj"],
            defaults=defaults,
        )
        if was_created:
            created += 1
        else:
            updated += 1

    return {
        "release": summary["release"],
        "downloaded_files": summary["downloaded_files"],
        "matched": summary["matched"],
        "created": created,
        "updated": updated,
    }
