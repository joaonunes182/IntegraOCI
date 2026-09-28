from ninja import NinjaAPI, File, UploadedFile
from ninja.errors import HttpError
from core.auth import JWTCookieAuth
import pandas as pd
import openpyxl
from datetime import datetime
import io
import tempfile
import os
import json
import re
from django.http import FileResponse
from typing import Dict, Iterable, Iterator, List, Optional, Tuple
from dataclasses import dataclass
from functools import lru_cache
from .models import BpaApacImportHistory, OciComboAnalysisHistory, IntegraOciAuditLog
from .integra_oci_audit import (
    log_integra_oci_audit,
    require_integra_oci_item,
    serialize_integra_oci_audit_log,
)
from .details_storage import (
    load_bpa_details,
    load_oci_details,
    maybe_run_retention_cleanup,
    save_bpa_details,
    save_oci_details,
)
from difflib import SequenceMatcher
import uuid
from django.http import HttpResponse
from pathlib import Path
from django.utils import timezone
from datetime import timedelta
from core.audit import log_audit_event
from decouple import config
import pymysql
from pymysql.cursors import DictCursor
from decimal import Decimal, InvalidOperation
import unicodedata
import threading
import time
import hashlib
from django.http import StreamingHttpResponse
from django.db import connection
from django.core.cache import cache

api_bpa_apac = NinjaAPI(title="BpaApac", urls_namespace="bpa_apac", auth=JWTCookieAuth())

MAX_UPLOAD_SIZE = 50 * 1024 * 1024
TEMP_EXPORT_MAX_AGE_SECONDS = 24 * 60 * 60
UPLOAD_RATE_LIMIT_WINDOW_SECONDS = 60
UPLOAD_RATE_LIMIT_MAX_REQUESTS = 10
TEMP_DOWNLOAD_CACHE_PREFIX = "bpa_apac:temp_download:"
TEMP_DOWNLOAD_CACHE_TIMEOUT = 24 * 60 * 60
ANALYZE_FILE_CACHE_PREFIX = "bpa_apac:analyze:v1:"
ANALYZE_FILE_CACHE_TIMEOUT = 4 * 60 * 60
_PROC_LOOKUP_ALLOWED_TABLES = {
    "procedimento_sigtap",
    "vw_procedimento_sigtap",
    "sisreg_dim_procedimento_interno",
    "dim_procedimento",
    "procedimento",
    "sigtap_procedimento",
}
_PROC_LOOKUP_ALLOWED_CODE_COLUMNS = {"codigo_interno", "codigo_sigtap", "codigo", "procedimento", "cod_proc"}
_PROC_LOOKUP_ALLOWED_NAME_COLUMNS = {
    "nome_procedimento",
    "procedimento",
    "procedimento_interno",
    "descricao",
    "descricao_procedimento",
    "nome",
    "procedimento_nome",
    "ds_procedimento",
}
_CNES_CACHE_LOCK = threading.RLock()
_PROC_NAME_CACHE_LOCK = threading.Lock()
CNES_UNITS_CACHE_TIMEOUT = 24 * 60 * 60
CNES_UNITS_ROWS_CACHE_PREFIX = "bpa_apac:cnes_units:rows:"
CNES_UNITS_MAP_CACHE_PREFIX = "bpa_apac:cnes_units:map:"


def _safe_error_message(message: str) -> str:
    return str(message or "Não foi possível concluir a operação.").strip()


def _sanitize_exception_for_client(default_message: str, error: Exception) -> HttpError:
    print(f"{default_message}: {error}")
    return HttpError(400, default_message)


def _sanitize_download_filename(filename: str) -> str:
    base_name = os.path.basename(str(filename or "arquivo.bin").strip()) or "arquivo.bin"
    safe_name = re.sub(r'["\r\n\\\/]+', "_", base_name)
    safe_name = re.sub(r"[\x00-\x1f\x7f]+", "_", safe_name)
    return safe_name or "arquivo.bin"


def _validate_download_file_id(file_id: str) -> str:
    normalized = str(file_id or "").strip()
    if not normalized:
        raise HttpError(400, "Identificador de arquivo inválido.")
    try:
        uuid.UUID(normalized)
        return normalized
    except ValueError:
        if normalized.isdigit():
            return normalized
    raise HttpError(400, "Identificador de arquivo inválido.")


def _resolve_temp_download_path(file_id: str) -> str:
    safe_file_id = _validate_download_file_id(file_id)
    path = os.path.join(tempfile.gettempdir(), safe_file_id)
    resolved = os.path.realpath(path)
    temp_root = os.path.realpath(tempfile.gettempdir())
    if not resolved.startswith(f"{temp_root}{os.sep}"):
        raise HttpError(400, "Caminho de arquivo inválido.")
    return resolved


def _cleanup_expired_temp_exports() -> None:
    temp_root = tempfile.gettempdir()
    now = time.time()
    try:
        for name in os.listdir(temp_root):
            try:
                uuid.UUID(name)
            except ValueError:
                continue
            path = os.path.join(temp_root, name)
            try:
                if os.path.isfile(path) and (now - os.path.getmtime(path)) > TEMP_EXPORT_MAX_AGE_SECONDS:
                    os.remove(path)
            except OSError:
                continue
    except OSError:
        return


def _validate_file_size(file: UploadedFile) -> None:
    if not file:
        raise HttpError(400, "Arquivo não enviado.")
    file_size = getattr(file, "size", None)
    if file_size is None:
        return
    if int(file_size) > MAX_UPLOAD_SIZE:
        raise HttpError(
            400,
            f"O arquivo '{file.name}' excede o limite de 50MB ({file_size / 1024 / 1024:.1f}MB).",
        )


def _validate_files_size(files: Iterable[UploadedFile]) -> None:
    for uploaded in files or []:
        _validate_file_size(uploaded)


def _get_request_identity(request) -> str:
    user_id = getattr(getattr(request, "user", None), "id", None)
    if user_id:
        return f"user:{user_id}"
    remote_addr = request.META.get("HTTP_X_FORWARDED_FOR") or request.META.get("REMOTE_ADDR") or "anon"
    return f"ip:{str(remote_addr).split(',')[0].strip()}"


def _enforce_rate_limit(request, scope: str, limit: int = UPLOAD_RATE_LIMIT_MAX_REQUESTS, window_seconds: int = UPLOAD_RATE_LIMIT_WINDOW_SECONDS) -> None:
    cache_key = f"bpa_apac:ratelimit:{scope}:{_get_request_identity(request)}"
    current = cache.get(cache_key)
    if current is None:
        cache.set(cache_key, 1, timeout=window_seconds)
        return
    current = int(current) + 1
    cache.set(cache_key, current, timeout=window_seconds)
    if current > limit:
        raise HttpError(429, "Muitas requisições em sequência. Aguarde alguns instantes e tente novamente.")


def _get_request_unit_cnes(request) -> str:
    user = getattr(request, "user", None)
    if not user:
        return ""
    if getattr(user, "is_superuser", False) or getattr(user, "is_staff", False):
        return ""
    profile = getattr(user, "profile", None)
    unidade = getattr(profile, "unidade", None)
    return _normalize_cnes(getattr(unidade, "cnes", ""))


def _assert_unit_access(request, unit_cnes: str) -> None:
    requested_unit_cnes = _normalize_cnes(unit_cnes)
    user_unit_cnes = _get_request_unit_cnes(request)
    if user_unit_cnes and requested_unit_cnes and user_unit_cnes != requested_unit_cnes:
        raise HttpError(403, "Você não tem permissão para acessar dados de outra unidade.")


def _history_unit_cnes(details: Dict[str, object]) -> str:
    metadata = details.get("metadata", {}) if isinstance(details, dict) else {}
    resolved_unit = metadata.get("resolved_unit") or {}
    return _normalize_cnes(resolved_unit.get("cnes"))


def _assert_history_access(request, history_id: int) -> Dict[str, object]:
    details = _load_history_details_raw(history_id)
    unit_cnes = _history_unit_cnes(details)
    if not unit_cnes:
        history_record = BpaApacImportHistory.objects.filter(id=history_id).only("unit_cnes").first()
        unit_cnes = _normalize_cnes(getattr(history_record, "unit_cnes", ""))
    _assert_unit_access(request, unit_cnes)
    return details


def _temp_download_cache_key(file_id: str) -> str:
    return f"{TEMP_DOWNLOAD_CACHE_PREFIX}{file_id}"


def _register_temp_download_access(request, file_id: str, file_name: str, unit_cnes: str = "") -> None:
    cache.set(
        _temp_download_cache_key(file_id),
        {
            "user_id": getattr(getattr(request, "user", None), "id", None),
            "unit_cnes": _normalize_cnes(unit_cnes),
            "file_name": _sanitize_download_filename(file_name),
        },
        timeout=TEMP_DOWNLOAD_CACHE_TIMEOUT,
    )


def _assert_temp_download_access(request, file_id: str) -> Dict[str, object]:
    payload = cache.get(_temp_download_cache_key(file_id))
    if not isinstance(payload, dict):
        raise HttpError(404, "Arquivo temporário não encontrado ou já expirou.")
    expected_user_id = payload.get("user_id")
    current_user_id = getattr(getattr(request, "user", None), "id", None)
    if expected_user_id and current_user_id != expected_user_id:
        raise HttpError(403, "Você não tem permissão para baixar este arquivo temporário.")
    _assert_unit_access(request, payload.get("unit_cnes"))
    return payload

def keep_alive_json_streaming(func, *args, **kwargs):
    """
    Roda a função em background e faz yield de espaços em branco a cada 5 segundos.
    Evita timeout de proxy (como o erro 524 do Cloudflare de 120 segundos).
    """
    result_container = []
    error_container = []
    
    def target():
        try:
            res = func(*args, **kwargs)
            result_container.append(res)
        except Exception as e:
            if isinstance(e, HttpError):
                error_container.append({"error": str(e), "status_code": e.status_code})
            else:
                error_container.append({"error": str(e), "status_code": 500})
        finally:
            # Importante fechar a conexao do banco nesta thread
            connection.close()

    thread = threading.Thread(target=target)
    thread.start()
    
    def generator():
        while thread.is_alive():
            yield b" " * 4096 + b"\n"
            time.sleep(2)
            
        if error_container:
            # Retorna o JSON de erro para o frontend
            yield json.dumps(error_container[0], ensure_ascii=False).encode('utf-8')
        else:
            yield json.dumps(result_container[0], ensure_ascii=False).encode('utf-8')
            
    return StreamingHttpResponse(generator(), content_type="application/json")


CNES_UNITS_FILE = Path(__file__).resolve().with_name("cnes_units.json")
ALLOWED_OCI_CNES = {'5371120', '2290103', '6038913', '2270285', '2273225', '2288370', '2298120', '2271346', '2290588', '3081990', '2274361', '2294117', '2297876', '6716849', '3567508', '2277298', '3388794', '2269503', '6618863', '6635709', '0215112', '4092104', '2291304', '2271052', '3344169', '4170318', '0273619', '6407412', '5315050', '5621720', '6853242', '2269392', '2270471', '5358612', '4271890', '2269902', '2296306', '6029965', '6810969', '6664075', '2290502', '0864994', '2273411', '2280191', '5467136', '2270420', '6559735', '6618871', '6203515', '5263263', '2295032', '2270714', '2270161', '6855709', '3567567', '2285894', '2287862', '2280310', '0425974', '0428590', '2273489', '6618855', '2273632', '2270129', '0814423', '4214536', '5581273', '5476607', '5511607', '2270366', '2296594', '0214949', '3333167', '6298109', '2269724', '2270498', '0189200', '5879655', '5462835', '6808077', '2280779', '6852203', '2270293', '5621801', '2708183', '4337549', '6581994', '2267551', '5307864', '2270439', '0112348', '2280272', '2277263', '6321690', '2269848', '2269988', '5044685', '4404076', '5423996', '4056167', '2280787', '2270242', '0265233', '6272053', '2280736', '2270102', '2271362', '2280167', '2708426', '6804209', '6576524', '2269295', '6694330', '6159192', '0215066', '2270668', '2269376', '5476844', '6185045', '2270250', '6632831', '2273365', '4056310', '6542042', '2277328', '6496989', '2269759', '2270064', '2270021', '2273640', '4056221', '2270641', '5620287', '2280205', '5456932', '6521282', '3178447', '2269651', '2270234', '3785009', '2269678', '0199338', '2269627', '2295326', '6038891', '2270455', '2270560', '4046307', '4388623', '6435459', '2280728', '0716170', '5476585', '6571956', '2295067', '2295369', '2270269', '6683851', '2288362', '3164896', '5555667', '6647057', '3820599', '6023975', '2296543', '6694101', '2269945', '2268183', '2269309', '6843832', '2269481', '2269341', '2270277', '6460852', '3567516', '2708434', '3122786', '2295253', '2270803', '2280744', '4030990', '3982742', '2296616', '6432352', '3348431', '5476321', '6681379', '0193089', '6225152', '2270528', '2280132', '2708205', '6023916', '2270331', '2279398', '4721101', '6023320', '2273179', '0215015', '2296527', '6323413', '6793231', '2970619', '5677351', '2708418', '2270609', '2270633', '5440203', '2269368', '6706630', '2708167', '2296551', '6677304', '6422810', '5939720', '5465877', '6742130', '5955211', '2279754', '2270552', '6458181', '2298732', '6067522', '4404017', '3069729', '4388054', '6631169', '6460712', '5423430', '6610129', '2270382', '2280280', '2269953', '6033121', '6674291', '2270579', '2269805', '2970627', '6671020', '3784959', '6023983', '6664040', '6568491', '2970643', '5457009', '2291266', '4224361', '2269473', '6559727', '4046544', '2778696', '6591817', '2295407', '3017087', '2295237', '6648371', '2277301', '5581265', '3567540', '6575900', '2295423', '2269732', '5511690', '2279355', '0198528', '2806320', '6473245', '5955688', '2270315', '4337557', '4282353', '6029841', '2273187', '2276712', '2269937', '4672615', '6464491', '2269538', '2269562', '6761704', '2976706', '6422608', '4178602', '2295210', '6026737', '2269880', '3796310', '5482070', '5465885', '6488013', '0532886', '2273454', '2708175', '5598435', '6514022', '2296535', '2270617', '2270013', '0472239', '3785025', '0304107', '2269430', '6029825', '2273551', '2273276', '5462886', '2273616', '5671388', '6387152', '2296586', '4429486', '5955661', '6820018', '2280698', '4538390', '2273543', '2708361', '2291274', '2273349', '2269546', '6029922', '2938383', '2267381', '6506232', '2271338', '6037569', '2280760', '2270307', '5447798', '6660185', '3526097', '5468019', '2280248', '2283972', '2295490', '2937387', '3988724', '2270072', '2273357', '2270463', '2269384', '2271303', '3784975', '6426484', '5466032', '6570496', '2270048', '5483662', '6572014', '6784720', '5717256', '4325508', '2269929', '2288346', '5417708', '5670357', '2293900', '4269535', '4325516', '2269554', '2288338', '2269511', '6361307', '5315026', '3001202', '6716598', '5546591', '6774210', '2280795', '4297822', '3416356', '2708213', '6220584', '2273586', '2708159', '2269775', '2280299', '6664164', '0310409', '6389317', '6503772', '3567559', '5727855', '2273209', '2270153', '4716361', '2269899', '2270323', '2270056', '2276127', '5154197', '2295415', '5682819', '2269783', '6677711', '3416321', '6661904', '2269821', '2270137', '2270218', '6762042', '6688152', '4575474', '2270390', '2276623', '3353915', '3416372', '2708353', '6524486', '5179726', '2273578', '5546583', '2273659', '2280183', '0999490', '6028233', '4558014', '3069699', '6713564', '2698854'}

def _load_txt_cnes_database() -> Dict[str, str]:
    db_file = Path(__file__).resolve().parent / "unidade_202606191548.txt"
    units_map = {}
    
    if not db_file.exists():
        return units_map
        
    try:
        with open(db_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip() or line.startswith("|-") or "nome_unidade" in line:
                    continue
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 3:
                    cnes = _normalize_cnes(parts[1])
                    nome_unidade = parts[2]
                    if cnes:
                        units_map[cnes] = nome_unidade
    except Exception as e:
        print(f"Erro ao ler arquivo de unidades: {e}")
        
    return units_map

def _validate_cnes(cnes_summary: dict):
    units = cnes_summary.get("units") or []
    primary = cnes_summary.get("primary_unit") or {}
    
    cnes_to_check = set()
    primary_cnes = _normalize_cnes(primary.get("cnes"))
    if primary_cnes:
        cnes_to_check.add(primary_cnes)
        
    for unit in units:
        cnes = _normalize_cnes(unit.get("cnes"))
        if cnes:
            cnes_to_check.add(cnes)
            
    if not cnes_to_check:
        return
        
    valid_cnes_db = _load_txt_cnes_database()
        
    for cnes in cnes_to_check:
        if cnes not in valid_cnes_db:
            unit_name = primary.get("nome_unidade") if cnes == primary_cnes else None
            if not unit_name:
                for unit in units:
                    if _normalize_cnes(unit.get("cnes")) == cnes:
                        unit_name = unit.get("nome_unidade")
                        break
            unit_name_str = f" - {unit_name}" if unit_name else ""
            raise HttpError(
                400,
                f"A unidade não está cadastrada na base de dados (CNES {cnes}{unit_name_str}). Favor contatar o faturamento."
            )

OCI_CBO_CID_RULES_FILE = Path(__file__).resolve().with_name("oci_cbo_cid_rules.json")
OCI_PREFIXES = ("09", "05", "01")
OCI_TREATED_TARGET_CNES = "2970643"
OCI_TREATED_TARGETS: Tuple[Dict[str, str], ...] = (
    {
        "code": "CCE",
        "cnes": "2970643",
        "display_name": "CCE",
    },
    {
        "code": "CCD",
        "cnes": "2970627",
        "display_name": "SMS CENTRO CARIOCA DE DIAGNOSTICO AP 10",
    },
)
OCI_CBO_CID_CODE_ALIASES: Dict[str, Tuple[str, ...]] = {
    "0901010022": ("0901010090", "0901010103"),
    "0901010065": ("0901010111", "0901010120"),
}


_CNES_ROWS_CACHE = None
_CNES_MAP_CACHE = None
_CNES_ROWS_CACHE_VERSION = None
_CNES_MAP_CACHE_VERSION = None


def _get_cnes_cache_version() -> str:
    if not CNES_UNITS_FILE.exists():
        return "missing"

    try:
        stat = CNES_UNITS_FILE.stat()
        return f"{int(stat.st_mtime)}:{int(stat.st_size)}"
    except OSError:
        return "unavailable"


def _cnes_rows_cache_key() -> str:
    return f"{CNES_UNITS_ROWS_CACHE_PREFIX}{_get_cnes_cache_version()}"


def _cnes_map_cache_key() -> str:
    return f"{CNES_UNITS_MAP_CACHE_PREFIX}{_get_cnes_cache_version()}"


def _load_cnes_unit_rows() -> List[Dict[str, str]]:
    global _CNES_ROWS_CACHE, _CNES_ROWS_CACHE_VERSION
    cache_version = _get_cnes_cache_version()
    if _CNES_ROWS_CACHE is not None and _CNES_ROWS_CACHE_VERSION == cache_version:
        return _CNES_ROWS_CACHE
    with _CNES_CACHE_LOCK:
        if _CNES_ROWS_CACHE is not None and _CNES_ROWS_CACHE_VERSION == cache_version:
            return _CNES_ROWS_CACHE
        cached_rows = cache.get(_cnes_rows_cache_key())
        if isinstance(cached_rows, list):
            _CNES_ROWS_CACHE = cached_rows
            _CNES_ROWS_CACHE_VERSION = cache_version
            return _CNES_ROWS_CACHE
        if not CNES_UNITS_FILE.exists():
            _CNES_ROWS_CACHE = []
            _CNES_ROWS_CACHE_VERSION = cache_version
            return _CNES_ROWS_CACHE
        try:
            _CNES_ROWS_CACHE = json.loads(CNES_UNITS_FILE.read_text(encoding="utf-8"))
        except Exception:
            _CNES_ROWS_CACHE = []
        _CNES_ROWS_CACHE_VERSION = cache_version
        cache.set(_cnes_rows_cache_key(), _CNES_ROWS_CACHE, timeout=CNES_UNITS_CACHE_TIMEOUT)
    return _CNES_ROWS_CACHE


def _load_cnes_unit_map() -> Dict[str, str]:
    global _CNES_MAP_CACHE, _CNES_MAP_CACHE_VERSION
    cache_version = _get_cnes_cache_version()
    if _CNES_MAP_CACHE is not None and _CNES_MAP_CACHE_VERSION == cache_version:
        return _CNES_MAP_CACHE
    with _CNES_CACHE_LOCK:
        if _CNES_MAP_CACHE is not None and _CNES_MAP_CACHE_VERSION == cache_version:
            return _CNES_MAP_CACHE
        cached_map = cache.get(_cnes_map_cache_key())
        if isinstance(cached_map, dict):
            _CNES_MAP_CACHE = cached_map
            _CNES_MAP_CACHE_VERSION = cache_version
            return _CNES_MAP_CACHE
        _CNES_MAP_CACHE = {item["cnes"]: item["nome_unidade"] for item in _load_cnes_unit_rows()}
        _CNES_MAP_CACHE_VERSION = cache_version
        cache.set(_cnes_map_cache_key(), _CNES_MAP_CACHE, timeout=CNES_UNITS_CACHE_TIMEOUT)
    return _CNES_MAP_CACHE


def _normalize_cnes(value) -> str:
    digits = "".join(ch for ch in str(value or "") if ch.isdigit())
    if not digits:
        return ""
    return digits.zfill(7)[-7:]


from functools import lru_cache

@lru_cache(maxsize=2048)
def _normalize_text_cached(value) -> str:
    return str(value or "").strip()

def _normalize_text(value) -> str:
    if not isinstance(value, (str, int, float)) and value is not None:
        return str(value or "").strip()
    return _normalize_text_cached(value)


@lru_cache(maxsize=1024)
def _normalize_proc_code_cached(value) -> str:
    digits = "".join(ch for ch in str(value or "") if ch.isdigit())
    if not digits:
        return ""
    return digits.zfill(10)[-10:]

def _normalize_proc_code(value) -> str:
    if not isinstance(value, (str, int, float)) and value is not None:
        digits = "".join(ch for ch in str(value or "") if ch.isdigit())
        if not digits:
            return ""
        return digits.zfill(10)[-10:]
    return _normalize_proc_code_cached(value)


@lru_cache(maxsize=1024)
def _normalize_cbo_code_cached(value) -> str:
    return "".join(ch for ch in str(value or "") if ch.isdigit())

def _normalize_cbo_code(value) -> str:
    if not isinstance(value, (str, int, float)) and value is not None:
        return "".join(ch for ch in str(value or "") if ch.isdigit())
    return _normalize_cbo_code_cached(value)


@lru_cache(maxsize=2048)
def _normalize_cid_code_cached(value) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(value or "").upper())

def _normalize_cid_code(value) -> str:
    if not isinstance(value, (str, int, float)) and value is not None:
        return re.sub(r"[^A-Z0-9]", "", str(value or "").upper())
    return _normalize_cid_code_cached(value)


@lru_cache(maxsize=512)
def _normalize_competencia_code_cached(value) -> str:
    digits = "".join(ch for ch in str(value or "") if ch.isdigit())
    return digits[:6] if len(digits) >= 6 else ""

def _normalize_competencia_code(value) -> str:
    if not isinstance(value, (str, int, float)) and value is not None:
        digits = "".join(ch for ch in str(value or "") if ch.isdigit())
        return digits[:6] if len(digits) >= 6 else ""
    return _normalize_competencia_code_cached(value)


def _get_data_db_connection():
    return pymysql.connect(
        host=config("MYSQL_DATA_HOST", default=os.environ.get("MYSQL_DATA_HOST", "localhost")),
        user=config("MYSQL_DATA_USER", default=os.environ.get("MYSQL_DATA_USER", "root")),
        password=config("MYSQL_DATA_PASSWORD", default=os.environ.get("MYSQL_DATA_PASSWORD", "root")),
        database=config("MYSQL_DATA_DB", default=os.environ.get("MYSQL_DATA_DB", "sisreg")),
        port=config("MYSQL_DATA_PORT", default=os.environ.get("MYSQL_DATA_PORT", "3306"), cast=int),
        charset="utf8mb4",
        autocommit=True,
        cursorclass=DictCursor,
    )


def _get_data_db_name() -> str:
    return config("MYSQL_DATA_DB", default=os.environ.get("MYSQL_DATA_DB", "sisreg"))


@lru_cache(maxsize=1)
def _resolve_procedure_lookup_source() -> Optional[Tuple[str, str, str]]:
    candidate_tables = [
        "procedimento_sigtap",
        "vw_procedimento_sigtap",
        "sisreg_dim_procedimento_interno",
        "dim_procedimento",
        "procedimento",
        "sigtap_procedimento",
    ]
    candidate_code_columns = ["codigo_interno", "codigo_sigtap", "codigo", "procedimento", "cod_proc"]
    candidate_name_columns = [
        "nome_procedimento",
        "procedimento",
        "procedimento_interno",
        "descricao",
        "descricao_procedimento",
        "nome",
        "procedimento_nome",
        "ds_procedimento",
    ]

    placeholders = ", ".join(["%s"] * len(candidate_tables))
    try:
        with _get_data_db_connection() as connection_db:
            with connection_db.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT TABLE_NAME, COLUMN_NAME
                    FROM information_schema.COLUMNS
                    WHERE TABLE_SCHEMA = %s
                      AND TABLE_NAME IN ({placeholders})
                    """,
                    (_get_data_db_name(), *candidate_tables),
                )
                rows = cursor.fetchall()
    except Exception:
        return None

    columns_by_table: Dict[str, set] = {}
    for row in rows:
        table_name = str(row.get("TABLE_NAME") or "")
        column_name = str(row.get("COLUMN_NAME") or "")
        columns_by_table.setdefault(table_name, set()).add(column_name)

    for table_name in candidate_tables:
        columns = columns_by_table.get(table_name) or set()
        code_column = next((column for column in candidate_code_columns if column in columns), None)
        name_column = next((column for column in candidate_name_columns if column in columns), None)
        if code_column and name_column:
            return table_name, code_column, name_column
    return None


_PROC_NAME_CACHE: Dict[str, str] = {}

def _lookup_procedure_names(proc_codes: Iterable[str]) -> Dict[str, str]:
    global _PROC_NAME_CACHE
    normalized_codes = sorted({_normalize_proc_code(code) for code in proc_codes if _normalize_proc_code(code)})
    if not normalized_codes:
        return {}

    with _PROC_NAME_CACHE_LOCK:
        missing_codes = [code for code in normalized_codes if code not in _PROC_NAME_CACHE]
    if missing_codes:
        source = _resolve_procedure_lookup_source()
        if source:
            table_name, code_column, name_column = source
            if (
                table_name not in _PROC_LOOKUP_ALLOWED_TABLES
                or code_column not in _PROC_LOOKUP_ALLOWED_CODE_COLUMNS
                or name_column not in _PROC_LOOKUP_ALLOWED_NAME_COLUMNS
            ):
                source = None
        if source:
            placeholders = ", ".join(["%s"] * len(missing_codes))
            query = (
                f"SELECT `{code_column}` AS proc_code, `{name_column}` AS proc_name "
                f"FROM `{table_name}` "
                f"WHERE `{code_column}` IN ({placeholders})"
            )
            try:
                with _get_data_db_connection() as connection_db:
                    with connection_db.cursor() as cursor:
                        cursor.execute(query, missing_codes)
                        rows = cursor.fetchall()
                with _PROC_NAME_CACHE_LOCK:
                    for row in rows:
                        proc_code = _normalize_proc_code(row.get("proc_code"))
                        proc_name = str(row.get("proc_name") or "").strip()
                        if proc_code and proc_name:
                            _PROC_NAME_CACHE[proc_code] = proc_name
            except Exception:
                pass

    with _PROC_NAME_CACHE_LOCK:
        return {code: _PROC_NAME_CACHE[code] for code in normalized_codes if code in _PROC_NAME_CACHE}


def _build_procedure_detail_list(procedure_map: Dict[str, int]) -> List[Dict[str, object]]:
    if not procedure_map:
        return []

    names_by_code = _lookup_procedure_names(procedure_map.keys())
    details = []
    for proc_code in sorted(procedure_map.keys()):
        normalized_code = _normalize_proc_code(proc_code)
        details.append(
            {
                "code": normalized_code or str(proc_code),
                "name": names_by_code.get(normalized_code, ""),
                "qty": int(procedure_map.get(proc_code) or 0),
            }
        )
    return details


def _get_procedure_name(proc_code: str) -> str:
    normalized_code = _normalize_proc_code(proc_code)
    if not normalized_code:
        return ""
    return _lookup_procedure_names([normalized_code]).get(normalized_code, "")


def _is_oci_candidate(principal_proc: str, linked_procedures: Optional[Iterable[str]] = None) -> bool:
    principal_proc = _normalize_proc_code(principal_proc)
    if principal_proc.startswith(OCI_PREFIXES):
        return True

    linked_set = {
        _normalize_proc_code(proc)
        for proc in (linked_procedures or [])
        if _normalize_proc_code(proc)
    }
    if not linked_set:
        return False

    non_principal_procs = {proc for proc in linked_set if proc != principal_proc}
    return bool(non_principal_procs)


def _parse_quantity(value, default: int = 1) -> int:
    try:
        parsed = int(str(value or "").strip() or str(default))
    except (TypeError, ValueError):
        parsed = default
    return parsed or default


@dataclass(frozen=True)
class OciProcedureRule:
    label: str
    codes: Tuple[str, ...] = ()
    prefixes: Tuple[str, ...] = ()
    generic: bool = False


@dataclass(frozen=True)
class OciComboRule:
    combo_code: str
    combo_name: str
    required: Tuple[OciProcedureRule, ...]
    optional: Tuple[OciProcedureRule, ...] = ()
    notes: str = ""
    min_age_years: Optional[int] = None
    max_age_years: Optional[int] = None


def _exact_rule(label: str, *codes: str) -> OciProcedureRule:
    normalized_codes = tuple(
        code
        for code in (_normalize_proc_code(item) for item in codes)
        if code
    )
    return OciProcedureRule(label=label, codes=normalized_codes)


def _prefix_rule(label: str, *prefixes: str) -> OciProcedureRule:
    normalized_prefixes = tuple(
        prefix
        for prefix in ("".join(ch for ch in str(item or "") if ch.isdigit()) for item in prefixes)
        if prefix
    )
    return OciProcedureRule(label=label, prefixes=normalized_prefixes, generic=True)


def _load_oci_cbo_cid_rules() -> Dict[str, Dict[str, object]]:
    if not OCI_CBO_CID_RULES_FILE.exists():
        return {}
    try:
        rows = json.loads(OCI_CBO_CID_RULES_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

    rules: Dict[str, Dict[str, object]] = {}
    for row in rows if isinstance(rows, list) else []:
        source_code = "".join(ch for ch in str((row or {}).get("combo_code") or "") if ch.isdigit())
        if not source_code:
            continue

        normalized_rule = {
            "source_combo_code": source_code,
            "source_combo_name": _normalize_text((row or {}).get("combo_name")),
            "cbo_prefixes": tuple(
                sorted(
                    {
                        code
                        for code in (_normalize_cbo_code(item) for item in ((row or {}).get("cbo_prefixes") or []))
                        if code
                    }
                )
            ),
            "cid_prefixes": tuple(
                sorted(
                    {
                        code
                        for code in (_normalize_cid_code(item) for item in ((row or {}).get("cid_prefixes") or []))
                        if code
                    }
                )
            ),
        }
        target_codes = OCI_CBO_CID_CODE_ALIASES.get(source_code, (source_code,))
        for target_code in target_codes:
            rules[target_code] = normalized_rule
    return rules


OCI_COMBO_RULES: Tuple[OciComboRule, ...] = (
    OciComboRule(
        combo_code="0901010014",
        combo_name="OCI Avaliacao Diagnostica Inicial de Cancer de Mama",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Mamografia", "02.04.03.003-0"),
        ),
        optional=(
            _exact_rule("Ultrassonografia mamaria bilateral", "02.05.02.009-7"),
        ),
    ),
    OciComboRule(
        combo_code="0901010090",
        combo_name="OCI Progressao da Avaliacao Diagnostica de Cancer de Mama - I",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Puncao aspirativa de mama por agulha fina", "02.01.01.058-5"),
            _exact_rule("Citopatologico de mama OCI", "02.03.01.004-3"),
        ),
        optional=(
            _exact_rule("Biopsia/exerese de nodulo de mama", "02.01.01.056-9"),
        ),
    ),
    OciComboRule(
        combo_code="0901010103",
        combo_name="OCI Progressao da Avaliacao Diagnostica de Cancer de Mama - II",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Puncao de mama por agulha grossa", "02.01.01.060-7"),
            _exact_rule("Exame anatomopatologico de mama", "02.03.02.006-5"),
        ),
        optional=(
            _exact_rule("Biopsia/exerese de nodulo de mama", "02.01.01.056-9"),
        ),
    ),
    OciComboRule(
        combo_code="0901010057",
        combo_name="OCI Investigacao Diagnostica de Cancer de Colo de Utero",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Biopsia do colo uterino", "02.01.01.006-6"),
            _exact_rule("Exame anatomo-patologico do colo uterino - biopsia", "02.03.02.008-1"),
        ),
        optional=(
            _exact_rule("Colposcopia", "02.11.04.002-9"),
        ),
    ),
    OciComboRule(
        combo_code="0901010111",
        combo_name="OCI Avaliacao Diagnostica e Terapeutica de Cancer de Colo do Utero - I",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Excisao tipo I do colo uterino", "04.09.06.008-9"),
            _exact_rule("Exame anatomopatologico do colo uterino - peca cirurgica", "02.03.02.002-2"),
        ),
        optional=(
            _exact_rule("Colposcopia", "02.11.04.002-9"),
        ),
    ),
    OciComboRule(
        combo_code="0901010120",
        combo_name="OCI Avaliacao Diagnostica e Terapeutica de Cancer de Colo do Utero - II",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Excisao tipo 2 do colo uterino", "04.09.06.030-5"),
            _exact_rule("Exame anatomopatologico do colo uterino - peca cirurgica", "02.03.02.002-2"),
        ),
        optional=(
            _exact_rule("Colposcopia", "02.11.04.002-9"),
        ),
    ),
    OciComboRule(
        combo_code="0901010049",
        combo_name="OCI Progressao da Avaliacao Diagnostica de Cancer de Prostata",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Ultrassonografia de prostata via transretal", "02.05.02.011-9"),
            _exact_rule("Biopsia de prostata via transretal", "02.01.01.041-0"),
            _exact_rule("Exame anatomopatologico por peca ou biopsia", "02.03.02.003-0"),
        ),
    ),
    OciComboRule(
        combo_code="0901010073",
        combo_name="OCI Avaliacao Diagnostica de Cancer Gastrico",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Esofagogastroduodenoscopia", "02.09.01.003-7"),
        ),
        optional=(
            _exact_rule("Exame anatomopatologico por peca ou biopsia", "02.03.02.003-0"),
        ),
    ),
    OciComboRule(
        combo_code="0901010081",
        combo_name="OCI Avaliacao Diagnostica de Cancer Colorretal",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Colonoscopia", "02.09.01.002-9"),
        ),
        optional=(
            _exact_rule("Exame anatomopatologico por peca ou biopsia", "02.03.02.003-0"),
        ),
    ),
    OciComboRule(
        combo_code="0902010018",
        combo_name="OCI Avaliacao de Risco Cirurgico",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Eletrocardiograma", "02.11.02.003-6"),
        ),
        optional=(
            _exact_rule("Radiografia de torax", "02.04.03.015-3"),
        ),
        notes="Exames laboratoriais opcionais nao sao inferidos nesta versao.",
    ),
    OciComboRule(
        combo_code="0902010026",
        combo_name="OCI Avaliacao Cardiologica",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Eletrocardiograma", "02.11.02.003-6"),
        ),
        optional=(
            _exact_rule("Radiografia de torax", "02.04.03.015-3"),
            _exact_rule("Ecocardiografia transtoracica", "02.05.01.003-2"),
        ),
        notes="Exames laboratoriais opcionais nao sao inferidos nesta versao.",
    ),
    OciComboRule(
        combo_code="0902010034",
        combo_name="OCI Avaliacao Diagnostica Inicial - Sindrome Coronariana Cronica",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Eletrocardiograma", "02.11.02.003-6"),
            _exact_rule("Teste de esforco", "02.11.02.006-0"),
        ),
        optional=(
            _exact_rule("Ecocardiografia transtoracica", "02.05.01.003-2"),
        ),
        notes="Exames laboratoriais opcionais nao sao inferidos nesta versao.",
    ),
    OciComboRule(
        combo_code="0902010042",
        combo_name="OCI Progressao da Avaliacao Diagnostica I - Sindrome Coronariana Cronica",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Ecocardiografia de estresse", "02.05.01.001-6"),
        ),
    ),
    OciComboRule(
        combo_code="0902010050",
        combo_name="OCI Progressao da Avaliacao Diagnostica II - Sindrome Coronariana Cronica",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Cintilografia de miocardio em repouso", "02.08.01.003-3"),
            _exact_rule("Cintilografia de miocardio em estresse", "02.08.01.002-5"),
        ),
    ),
    OciComboRule(
        combo_code="0902010069",
        combo_name="OCI Avaliacao Diagnostica - Insuficiencia Cardiaca",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Eletrocardiograma", "02.11.02.003-6"),
            _exact_rule("Teste de esforco", "02.11.02.006-0"),
            _exact_rule("Holter 24h", "02.11.02.004-4"),
            _exact_rule("Dosagem de peptideos natriureticos", "02.02.01.079-1"),
        ),
        optional=(
            _exact_rule("Ecocardiografia transtoracica", "02.05.01.003-2"),
        ),
        notes="Exames laboratoriais opcionais nao sao inferidos nesta versao.",
    ),
    OciComboRule(
        combo_code="0902010077",
        combo_name="OCI Gestao do Pre-operatorio",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Eletrocardiograma", "02.11.02.003-6"),
        ),
        optional=(
            _exact_rule("Radiografia de torax", "02.04.03.015-3"),
            _exact_rule("Consulta de enfermagem", "03.01.01.004-8"),
            _exact_rule("Teleconsulta medica", "03.01.01.030-7"),
        ),
        notes="Exames laboratoriais para avaliacao pre-operatoria nao sao inferidos nesta versao.",
    ),
    OciComboRule(
        combo_code="0903010011",
        combo_name="OCI Avaliacao Diagnostica em Ortopedia com Recursos de Radiologia",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _prefix_rule("Radiografia compativel", "0204"),
        ),
        notes="Radiografia compativel e identificada por prefixo SIGTAP 0204.",
    ),
    OciComboRule(
        combo_code="0903010020",
        combo_name="OCI Avaliacao Diagnostica em Ortopedia com Recursos de Radiologia e Ultrassonografia",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Ultrassonografia de articulacao", "02.05.02.006-2"),
        ),
    ),
    OciComboRule(
        combo_code="0903010038",
        combo_name="OCI Avaliacao Diagnostica em Ortopedia com Recursos de Radiologia e Tomografia Computadorizada",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _prefix_rule("Tomografia compativel", "0206"),
        ),
        notes="Tomografia compativel e identificada por prefixo SIGTAP 0206.",
    ),
    OciComboRule(
        combo_code="0903010046",
        combo_name="OCI Avaliacao Diagnostica em Ortopedia com Recursos de Radiologia e Ressonancia Magnetica",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _prefix_rule("Ressonancia magnetica compativel", "0207"),
        ),
        notes="Ressonancia compativel e identificada por prefixo SIGTAP 0207.",
    ),
    OciComboRule(
        combo_code="0904010015",
        combo_name="OCI Avaliacao Inicial Diagnostica de Deficit Auditivo",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Audiometria tonal limiar", "02.11.07.004-1"),
        ),
        optional=(
            _exact_rule("Imitanciometria", "02.11.07.020-3"),
        ),
    ),
    OciComboRule(
        combo_code="0904010023",
        combo_name="OCI Progressao da Avaliacao Diagnostica de Deficit Auditivo",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Audiometria tonal limiar", "02.11.07.004-1"),
            _exact_rule("Potencial evocado auditivo", "02.11.07.026-2"),
        ),
        optional=(
            _exact_rule("Imitanciometria", "02.11.07.020-3"),
        ),
    ),
    OciComboRule(
        combo_code="0904010031",
        combo_name="OCI Avaliacao Diagnostica de Nasofaringe e de Orofaringe",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Videolaringoscopia", "02.09.04.004-1"),
            _exact_rule("Laringoscopia", "02.09.04.002-5"),
        ),
    ),
    OciComboRule(
        combo_code="0905010019",
        combo_name="OCI Avaliacao Inicial em Oftalmologia - 0 a 8 anos",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Teste ortoptico", "02.11.06.023-2"),
            _exact_rule("Mapeamento de retina", "02.11.06.012-7"),
            _exact_rule("Biomicroscopia de fundo de olho", "02.11.06.002-0"),
        ),
        min_age_years=0,
        max_age_years=8,
    ),
    OciComboRule(
        combo_code="0905010027",
        combo_name="OCI Avaliacao de Estrabismo",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Teste ortoptico", "02.11.06.023-2"),
            _exact_rule("Mapeamento de retina", "02.11.06.012-7"),
            _exact_rule("Tonometria", "02.11.06.025-9"),
            _exact_rule("Biomicroscopia de fundo de olho", "02.11.06.002-0"),
        ),
        optional=(
            _exact_rule("Fundoscopia", "02.11.06.010-0"),
            _exact_rule("Retinografia colorida binocular", "02.11.06.017-8"),
        ),
    ),
    OciComboRule(
        combo_code="0905010035",
        combo_name="OCI Avaliacao Inicial em Oftalmologia - A partir de 9 anos",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Tonometria", "02.11.06.025-9"),
            _exact_rule("Mapeamento de retina", "02.11.06.012-7"),
            _exact_rule("Biomicroscopia de fundo de olho", "02.11.06.002-0"),
        ),
        optional=(
            _exact_rule("Teste ortoptico", "02.11.06.023-2"),
        ),
        min_age_years=9,
    ),
    OciComboRule(
        combo_code="0905010043",
        combo_name="OCI Avaliacao de Retinopatia Diabetica",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Mapeamento de retina", "02.11.06.012-7"),
            _exact_rule("Retinografia colorida binocular", "02.11.06.017-8"),
            _exact_rule("Biomicroscopia de fundo de olho", "02.11.06.002-0"),
            _exact_rule("Tonometria", "02.11.06.025-9"),
        ),
    ),
    OciComboRule(
        combo_code="0905010051",
        combo_name="OCI Avaliacao Inicial para Oncologia Oftalmologica",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Ultrassonografia de globo ocular/orbita", "02.05.02.008-9"),
            _exact_rule("Mapeamento de retina", "02.11.06.012-7"),
            _exact_rule("Biomicroscopia de fundo de olho", "02.11.06.002-0"),
            _exact_rule("Tonometria", "02.11.06.025-9"),
        ),
        optional=(
            _exact_rule("Retinografia colorida binocular", "02.11.06.017-8"),
        ),
    ),
    OciComboRule(
        combo_code="0905010060",
        combo_name="OCI Avaliacao Diagnostica em Neuro Oftalmologia",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Campimetria", "02.11.06.003-8"),
            _exact_rule("Tonometria", "02.11.06.025-9"),
            _exact_rule("Teste de visao de cores", "02.11.06.022-4"),
            _exact_rule("Mapeamento de retina", "02.11.06.012-7"),
            _exact_rule("Retinografia colorida binocular", "02.11.06.017-8"),
            _exact_rule("Biomicroscopia de fundo de olho", "02.11.06.002-0"),
        ),
    ),
    OciComboRule(
        combo_code="0905010078",
        combo_name="OCI Exames Oftalmologicos sob Sedacao",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Sedacao", "04.17.01.006-0"),
        ),
        optional=(
            _exact_rule("Tonometria", "02.11.06.025-9"),
            _exact_rule("Mapeamento de retina", "02.11.06.012-7"),
        ),
    ),
    OciComboRule(
        combo_code="0906010012",
        combo_name="GIN1 - Avaliacao Diagnostica Inicial de Saude da Mulher I",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Ultrassonografia transvaginal", "02.05.02.018-6"),
        ),
    ),
    OciComboRule(
        combo_code="0906010020",
        combo_name="GIN1 - Avaliacao Diagnostica Inicial de Saude da Mulher II",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Ultrassonografia pelvica", "02.05.02.016-0"),
        ),
    ),
    OciComboRule(
        combo_code="0906010039",
        combo_name="GIN2 - Progressao da Avaliacao Diagnostica - Sangramento Uterino Anormal I",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Histeroscopia cirurgica", "02.09.03.001-1"),
            _exact_rule("Exame anatomo-patologico para congelamento", "02.03.02.003-0"),
            _exact_rule("Sedacao", "04.17.01.006-0"),
            _exact_rule("Telediagnostico", "08.04.02.002-7"),
        ),
    ),
    OciComboRule(
        combo_code="0906010047",
        combo_name="GIN2 - Progressao da Avaliacao Diagnostica - Sangramento Uterino Anormal II",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _exact_rule("Biopsia de endometrio por aspiracao", "02.01.01.016-0"),
            _exact_rule("Sedacao", "04.17.01.006-0"),
            _exact_rule("Telediagnostico", "08.04.02.002-7"),
            _exact_rule("Exame anatomo-patologico para congelamento", "02.03.02.003-0"),
        ),
    ),
    OciComboRule(
        combo_code="0906010055",
        combo_name="GIN3 - Progressao da Avaliacao Diagnostica - Endometriose Profunda",
        required=(
            _exact_rule("Consulta", "03.01.01.007-2"),
            _prefix_rule("Ressonancia magnetica de pelve/bacia/abdomen inferior", "0207"),
        ),
        notes="Ressonancia compativel e identificada por prefixo SIGTAP 0207.",
    ),
)

OCI_CBO_CID_RULES = _load_oci_cbo_cid_rules()


def _normalize_proc_text_key(value) -> str:
    normalized = unicodedata.normalize("NFKD", str(value or "").strip().upper())
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
    compact_name = re.sub(r"[^A-Z0-9 ]+", " ", ascii_name)
    return re.sub(r"\s+", " ", compact_name).strip()


@lru_cache(maxsize=1)
def _build_oci_textual_proc_aliases() -> Dict[str, str]:
    aliases: Dict[str, str] = {}
    for combo in OCI_COMBO_RULES:
        for rule in (*combo.required, *combo.optional):
            if len(rule.codes) == 1:
                normalized_label = _normalize_proc_text_key(rule.label)
                if normalized_label:
                    aliases[normalized_label] = rule.codes[0]

    aliases.update(
        {
            _normalize_proc_text_key("Consulta de profissionais de nivel superior na atencao especializada"): _normalize_proc_code("03.01.01.007-2"),
            _normalize_proc_text_key("Consulta medica em atencao especializada"): _normalize_proc_code("03.01.01.007-2"),
            _normalize_proc_text_key("Excisao tipo 1 do colo uterino"): _normalize_proc_code("04.09.06.008-9"),
            _normalize_proc_text_key("Excisao tipo 2 do colo uterino"): _normalize_proc_code("04.09.06.030-5"),
        }
    )
    return aliases


OCI_TEXTUAL_PROC_KEYWORD_ALIASES: Tuple[Tuple[Tuple[str, ...], str], ...] = (
    (("CONSULTA", "PROFISSIONAIS", "NIVEL SUPERIOR", "ESPECIALIZADA"), _normalize_proc_code("03.01.01.007-2")),
    (("ULTRASSONOGRAFIA", "TRANSVAGINAL"), _normalize_proc_code("02.05.02.018-6")),
    (("ULTRASSONOGRAFIA", "PELV"), _normalize_proc_code("02.05.02.016-0")),
    (("COLPOSCOPIA",), _normalize_proc_code("02.11.04.002-9")),
    (("BIOPSIA", "COLO", "UTER"), _normalize_proc_code("02.01.01.006-6")),
    (("ANATOMO", "PATOLOGICO", "COLO", "UTERINO", "BIOPS"), _normalize_proc_code("02.03.02.008-1")),
    (("ANATOMO", "PATOLOGICO", "COLO", "UTERINO", "PECA"), _normalize_proc_code("02.03.02.002-2")),
    (("EXCISAO", "TIPO 1", "COLO", "UTERINO"), _normalize_proc_code("04.09.06.008-9")),
    (("EXCISAO", "TIPO I", "COLO", "UTERINO"), _normalize_proc_code("04.09.06.008-9")),
    (("EXCISAO", "TIPO 2", "COLO", "UTERINO"), _normalize_proc_code("04.09.06.030-5")),
    (("EXCISAO", "TIPO II", "COLO", "UTERINO"), _normalize_proc_code("04.09.06.030-5")),
    (("HISTEROSCOPIA", "CIRURG"), _normalize_proc_code("02.09.03.001-1")),
    (("ENDOMETRIO", "ASPIR"), _normalize_proc_code("02.01.01.016-0")),
    (("SEDACAO",), _normalize_proc_code("04.17.01.006-0")),
    (("TELEDIAGNOSTICO",), _normalize_proc_code("08.04.02.002-7")),
)


def _extract_direct_oci_proc_code(value) -> str:
    raw_value = str(value or "").strip()
    if not raw_value:
        return ""
    if re.search(r"[A-Za-z]", raw_value):
        return ""
    digits = "".join(ch for ch in raw_value if ch.isdigit())
    if len(digits) == 9:
        digits = "0" + digits
    if len(digits) != 10:
        return ""
    return _normalize_proc_code(digits)


def _split_oci_proc_cell_values(value) -> List[str]:
    raw_value = str(value or "").strip()
    if not raw_value:
        return []
    return [part.strip() for part in raw_value.split(",") if str(part).strip()]


def _resolve_single_oci_sheet_procedure_code(raw_value) -> str:
    direct_code = _extract_direct_oci_proc_code(raw_value)
    if direct_code:
        return direct_code

    normalized_label = _normalize_proc_text_key(raw_value)
    if not normalized_label:
        return ""

    textual_aliases = _build_oci_textual_proc_aliases()
    if normalized_label in textual_aliases:
        return textual_aliases[normalized_label]

    for fragments, code in OCI_TEXTUAL_PROC_KEYWORD_ALIASES:
        if all(fragment in normalized_label for fragment in fragments):
            return code

    return ""


def _resolve_oci_sheet_procedure_codes(
    row: pd.Series,
    procedure_code_col: str = "",
    procedure_text_col: str = "",
) -> List[str]:
    resolved_codes: List[str] = []
    seen_codes = set()

    for column_name in (procedure_code_col, procedure_text_col):
        if not column_name:
            continue
        for raw_value in _split_oci_proc_cell_values(row.get(column_name)):
            resolved_code = _resolve_single_oci_sheet_procedure_code(raw_value)
            if resolved_code and resolved_code not in seen_codes:
                seen_codes.add(resolved_code)
                resolved_codes.append(resolved_code)

    return resolved_codes


def _resolve_oci_sheet_procedure_code(
    row: pd.Series,
    procedure_code_col: str = "",
    procedure_text_col: str = "",
) -> str:
    resolved_codes = _resolve_oci_sheet_procedure_codes(row, procedure_code_col, procedure_text_col)
    if resolved_codes:
        return resolved_codes[0]

    return ""


def _build_apac_linked_proc_map_from_excel(df_proc: pd.DataFrame) -> Dict[str, Dict[str, int]]:
    if df_proc.empty:
        return {}

    proc_num_col = _extract_excel_column_name(df_proc.columns, ["pap_num", "numero_apac"])
    proc_cod_col = _extract_excel_column_name(df_proc.columns, ["pap_codproc", "cod_proc"])
    qtd_col = _extract_excel_column_name(df_proc.columns, ["pap_qtdprod", "quantidade"])
    if not proc_num_col or not proc_cod_col:
        return {}

    proc_map: Dict[str, Dict[str, int]] = {}
    for _, row in df_proc.iterrows():
        apac_num = _normalize_text(row.get(proc_num_col))
        proc_code = _normalize_proc_code(row.get(proc_cod_col))
        if not apac_num or not proc_code:
            continue

        proc_map.setdefault(apac_num, {})
        proc_map[apac_num][proc_code] = proc_map[apac_num].get(proc_code, 0) + _parse_quantity(row.get(qtd_col), default=1)

    return proc_map


def _extract_excel_column_name(columns, aliases: List[str]) -> Optional[str]:
    normalized = {normalize_header_name(column): column for column in columns}
    for alias in aliases:
        key = normalize_header_name(alias)
        if key in normalized:
            return normalized[key]
    return None


def _summarize_cnes_counts(cnes_counts: Dict[str, int]) -> Dict[str, object]:
    unit_map = _load_cnes_unit_map()
    units = []
    for cnes, count in sorted(cnes_counts.items(), key=lambda item: (-item[1], item[0])):
        units.append(
            {
                "cnes": cnes,
                "nome_unidade": unit_map.get(cnes, "Unidade não mapeada"),
                "registros": count,
            }
        )

    primary = units[0] if units else None
    return {
        "units": units,
        "primary_unit": primary,
        "mapped": len(units),
    }


def _analyze_apac_excel(file_name: str, file_bytes: bytes) -> Dict[str, object]:
    engine = "openpyxl" if file_name.lower().endswith(".xlsx") else None
    workbook = pd.ExcelFile(io.BytesIO(file_bytes), engine=engine)
    sheet_names = workbook.sheet_names
    if "CORPO" not in sheet_names:
        raise HttpError(400, "Aba 'CORPO' não encontrada no arquivo APAC.")

    df_corpo = pd.read_excel(workbook, sheet_name="CORPO", header=3, dtype=str)
    df_proc = pd.read_excel(workbook, sheet_name="PROCEDIMENTOS", header=3, dtype=str) if "PROCEDIMENTOS" in sheet_names else pd.DataFrame()

    cnes_col = _extract_excel_column_name(df_corpo.columns, ["cnes", "cnes_executante", "cnes_solicitante"])
    competencia_col = _extract_excel_column_name(df_corpo.columns, ["competencia"])
    apac_num_col = _extract_excel_column_name(df_corpo.columns, ["apa_num", "numero_apac"])
    proc_principal_col = _extract_excel_column_name(df_corpo.columns, ["apa_codprinc", "cod_proc_princ"])
    patient_col = _extract_excel_column_name(df_corpo.columns, ["apa_nomepcnte", "nome_paciente"])
    linked_proc_map = _build_apac_linked_proc_map_from_excel(df_proc)

    cnes_counts: Dict[str, int] = {}
    if cnes_col:
        for raw_value in df_corpo[cnes_col].dropna().tolist():
            cnes = _normalize_cnes(raw_value)
            if cnes:
                cnes_counts[cnes] = cnes_counts.get(cnes, 0) + 1

    competencias = []
    if competencia_col:
        competencias = sorted({_normalize_text(value) for value in df_corpo[competencia_col].dropna().tolist() if _normalize_text(value)})

    total_oci = 0
    if proc_principal_col:
        for _, row in df_corpo.iterrows():
            apac_num = _normalize_text(row.get(apac_num_col)) if apac_num_col else ""
            principal_proc = row.get(proc_principal_col)
            linked_procedures = (linked_proc_map.get(apac_num) or {}).keys()
            if _is_oci_candidate(principal_proc, linked_procedures):
                total_oci += 1

    return {
        "file_name": file_name,
        "kind": "apac",
        "detected_format": "excel",
        "sheet_names": sheet_names,
        "total_registros": int(len(df_corpo.index)),
        "total_pacientes": int(df_corpo[patient_col].fillna("").astype(str).str.strip().ne("").sum()) if patient_col else 0,
        "total_apacs": int(df_corpo[apac_num_col].fillna("").astype(str).str.strip().nunique()) if apac_num_col else 0,
        "total_procedimentos": int(len(df_proc.index)) if not df_proc.empty else 0,
        "apac_oci_count": total_oci,
        "competencias": competencias,
        "cnes_summary": _summarize_cnes_counts(cnes_counts),
    }


def _analyze_apac_txt(file_name: str, file_bytes: bytes) -> Dict[str, object]:
    body_records = _get_parsed_fixed_width_records(file_bytes, APAC_CORPO_LAYOUT, "14")
    proc_records = _get_parsed_fixed_width_records(file_bytes, APAC_PROC_LAYOUT, "13")
    
    cnes_counts: Dict[str, int] = {}
    competencias = set()
    total_corpo = len(body_records)
    total_proc = len(proc_records)
    total_oci = 0
    apac_numbers = set()
    patients = set()
    apac_proc_map: Dict[str, Dict[str, int]] = {}

    for rec in body_records:
        cnes = _normalize_cnes(rec.get("cnes"))
        if cnes:
            cnes_counts[cnes] = cnes_counts.get(cnes, 0) + 1
        competencia = _normalize_text(rec.get("competencia"))
        if competencia:
            competencias.add(competencia)
        apac_number = _normalize_text(rec.get("numero_apac"))
        if apac_number:
            apac_numbers.add(apac_number)
        patient_key = (_normalize_text(rec.get("nome_paciente")), _normalize_text(rec.get("data_nasc")))
        if patient_key[0]:
            patients.add(patient_key)

    for rec in proc_records:
        apac_number = _normalize_text(rec.get("numero_apac"))
        proc_code = _normalize_proc_code(rec.get("cod_proc"))
        if apac_number and proc_code:
            apac_proc_map.setdefault(apac_number, {})
            apac_proc_map[apac_number][proc_code] = apac_proc_map[apac_number].get(proc_code, 0) + _parse_quantity(rec.get("quantidade"), default=1)

    for rec in body_records:
        apac_number = _normalize_text(rec.get("numero_apac"))
        linked_procedures = (apac_proc_map.get(apac_number) or {}).keys()
        if _is_oci_candidate(rec.get("cod_proc_princ"), linked_procedures):
            total_oci += 1

    return {
        "file_name": file_name,
        "kind": "apac",
        "detected_format": "texto",
        "sheet_names": [],
        "total_registros": total_corpo,
        "total_pacientes": len(patients),
        "total_apacs": len(apac_numbers),
        "total_procedimentos": total_proc,
        "apac_oci_count": total_oci,
        "competencias": sorted(competencias),
        "cnes_summary": _summarize_cnes_counts(cnes_counts),
    }


def _analyze_bpa_excel(file_name: str, file_bytes: bytes) -> Dict[str, object]:
    engine = "openpyxl" if file_name.lower().endswith(".xlsx") else None
    workbook = pd.ExcelFile(io.BytesIO(file_bytes), engine=engine)
    sheet_names = workbook.sheet_names
    preferred_sheet = "bpa original" if "bpa original" in sheet_names else sheet_names[0]
    df_bpa = pd.read_excel(workbook, sheet_name=preferred_sheet, header=0, dtype=str)

    cnes_col = _extract_excel_column_name(df_bpa.columns, ["cnes"])
    competencia_col = _extract_excel_column_name(df_bpa.columns, ["competencia"])
    patient_col = _extract_excel_column_name(df_bpa.columns, ["prd-nmpac", "nome_paciente"])
    procedure_col = _extract_excel_column_name(df_bpa.columns, ["prd-pa", "prd_pa", "procedimento"])
    quantity_col = _extract_excel_column_name(df_bpa.columns, ["prd-qt", "prd_qt", "qtd", "quantidade"])

    cnes_counts: Dict[str, int] = {}
    if cnes_col:
        for raw_value in df_bpa[cnes_col].dropna().tolist():
            cnes = _normalize_cnes(raw_value)
            if cnes:
                cnes_counts[cnes] = cnes_counts.get(cnes, 0) + 1

    competencias = []
    if competencia_col:
        competencias = sorted({_normalize_text(value) for value in df_bpa[competencia_col].dropna().tolist() if _normalize_text(value)})

    total_quantidade = 0
    if quantity_col:
        total_quantidade = int(pd.to_numeric(df_bpa[quantity_col], errors="coerce").fillna(0).sum())

    return {
        "file_name": file_name,
        "kind": "bpa",
        "detected_format": "excel",
        "sheet_names": sheet_names,
        "total_registros": int(len(df_bpa.index)),
        "total_pacientes": int(df_bpa[patient_col].fillna("").astype(str).str.strip().ne("").sum()) if patient_col else 0,
        "total_procedimentos": int(df_bpa[procedure_col].fillna("").astype(str).str.strip().ne("").sum()) if procedure_col else 0,
        "total_quantidade": total_quantidade,
        "competencias": competencias,
        "cnes_summary": _summarize_cnes_counts(cnes_counts),
    }


def _analyze_bpa_txt(file_name: str, file_bytes: bytes) -> Dict[str, object]:
    records = _get_parsed_fixed_width_records(file_bytes, BPA_I_LAYOUT, "03")
    cnes_counts: Dict[str, int] = {}
    competencias = set()
    total_records = len(records)
    total_quantidade = 0
    patients = set()
    procedures = set()

    for rec in records:
        cnes = _normalize_cnes(rec.get("cnes"))
        if cnes:
            cnes_counts[cnes] = cnes_counts.get(cnes, 0) + 1
        competencia = _normalize_text(rec.get("competencia"))
        if competencia:
            competencias.add(competencia)
        patient_key = (_normalize_text(rec.get("nome_paciente")), _normalize_text(rec.get("data_nasc")))
        if patient_key[0]:
            patients.add(patient_key)
        proc = _normalize_text(rec.get("procedimento"))
        if proc:
            procedures.add(proc)
        try:
            total_quantidade += int(_normalize_text(rec.get("quantidade")) or "0")
        except ValueError:
            total_quantidade += 0

    return {
        "file_name": file_name,
        "kind": "bpa",
        "detected_format": "texto",
        "sheet_names": [],
        "total_registros": total_records,
        "total_pacientes": len(patients),
        "total_procedimentos": len(procedures),
        "total_quantidade": total_quantidade,
        "competencias": sorted(competencias),
        "cnes_summary": _summarize_cnes_counts(cnes_counts),
    }


def _iter_file_line_bytes(file_bytes: bytes) -> Iterator[bytes]:
    """Percorre linhas sem materializar splitlines() em arquivos grandes."""
    if not file_bytes:
        return

    start = 0
    size = len(file_bytes)
    while start < size:
        end = file_bytes.find(b"\n", start)
        if end == -1:
            line = file_bytes[start:size]
            if line.endswith(b"\r"):
                line = line[:-1]
            if line.strip():
                yield line
            break

        line = file_bytes[start:end]
        if line.endswith(b"\r"):
            line = line[:-1]
        if line.strip():
            yield line
        start = end + 1


def _parse_quantity_bytes(raw: bytes, default: int = 0) -> int:
    value = 0
    found = False
    for byte in raw or b"":
        if 48 <= byte <= 57:
            value = value * 10 + (byte - 48)
            found = True
    return value if found else default


def _normalize_cnes_bytes(raw: bytes) -> str:
    return _normalize_cnes(raw.decode("iso-8859-1", errors="ignore"))


def _read_bpa_txt_header_metrics(file_bytes: bytes) -> Dict[str, object]:
    if not file_bytes.startswith(b"01"):
        return {}

    header_map = _get_layout_slice_map(BPA_HEADER_LAYOUT)
    comp_start, comp_end, _ = header_map["competencia"]
    lines_start, lines_end, _ = header_map["num_linhas"]
    line_end = file_bytes.find(b"\n")
    header = file_bytes[: line_end if line_end != -1 else min(len(file_bytes), 256)]
    if header.endswith(b"\r"):
        header = header[:-1]

    return {
        "competencia": _normalize_text(header[comp_start:comp_end].decode("iso-8859-1", errors="ignore")),
        "num_linhas": _parse_quantity_bytes(header[lines_start:lines_end], default=0),
    }


def _analyze_file_cache_key(file_bytes: bytes, kind: str) -> str:
    digest = hashlib.sha256(file_bytes).hexdigest()
    return f"{ANALYZE_FILE_CACHE_PREFIX}{digest}:{_normalize_text(kind).lower()}"


def _analyze_apac_txt_preview(file_name: str, file_bytes: bytes) -> Dict[str, object]:
    slice_map = _get_layout_slice_map(APAC_CORPO_LAYOUT)
    cnes_start, cnes_end, _ = slice_map["cnes"]
    comp_start, comp_end, _ = slice_map["competencia"]
    cnes_counts: Dict[str, int] = {}
    competencias = set()
    total_corpo = 0
    total_proc = 0

    for raw_line in _iter_file_line_bytes(file_bytes):
        if raw_line.startswith(b"14"):
            total_corpo += 1
            cnes = _normalize_cnes_bytes(raw_line[cnes_start:cnes_end])
            if cnes:
                cnes_counts[cnes] = cnes_counts.get(cnes, 0) + 1
            competencia = _normalize_text(raw_line[comp_start:comp_end].decode("iso-8859-1", errors="ignore"))
            if competencia:
                competencias.add(competencia)
        elif raw_line.startswith(b"13"):
            total_proc += 1

    return {
        "file_name": file_name,
        "kind": "apac",
        "detected_format": "texto",
        "sheet_names": [],
        "total_registros": total_corpo,
        "total_pacientes": 0,
        "total_apacs": total_corpo,
        "total_procedimentos": total_proc,
        "apac_oci_count": 0,
        "competencias": sorted(competencias),
        "cnes_summary": _summarize_cnes_counts(cnes_counts),
        "preview_mode": True,
    }


def _analyze_bpa_txt_preview(file_name: str, file_bytes: bytes) -> Dict[str, object]:
    slice_map = _get_layout_slice_map(BPA_I_LAYOUT)
    cnes_start, cnes_end, _ = slice_map["cnes"]
    comp_start, comp_end, _ = slice_map["competencia"]
    qty_start, qty_end, _ = slice_map["quantidade"]
    header_metrics = _read_bpa_txt_header_metrics(file_bytes)
    cnes_counts: Dict[str, int] = {}
    competencias = set()
    total_records = 0
    total_quantidade = 0

    if header_metrics.get("competencia"):
        competencias.add(header_metrics["competencia"])

    for raw_line in _iter_file_line_bytes(file_bytes):
        if not raw_line.startswith(b"03"):
            continue
        total_records += 1
        cnes = _normalize_cnes_bytes(raw_line[cnes_start:cnes_end])
        if cnes:
            cnes_counts[cnes] = cnes_counts.get(cnes, 0) + 1
        competencia = _normalize_text(raw_line[comp_start:comp_end].decode("iso-8859-1", errors="ignore"))
        if competencia:
            competencias.add(competencia)
        total_quantidade += _parse_quantity_bytes(raw_line[qty_start:qty_end], default=0)

    header_line_count = int(header_metrics.get("num_linhas") or 0)
    if header_line_count > 0:
        total_records = header_line_count

    return {
        "file_name": file_name,
        "kind": "bpa",
        "detected_format": "texto",
        "sheet_names": [],
        "total_registros": total_records,
        "total_pacientes": 0,
        "total_procedimentos": total_records,
        "total_quantidade": total_quantidade,
        "competencias": sorted(competencias),
        "cnes_summary": _summarize_cnes_counts(cnes_counts),
        "preview_mode": True,
    }


def _analyze_bpa_excel_preview(file_name: str, file_bytes: bytes) -> Dict[str, object]:
    wb = openpyxl.load_workbook(io.BytesIO(file_bytes), read_only=True, data_only=True)
    sheet_names = wb.sheetnames
    preferred_sheet = "bpa original" if "bpa original" in sheet_names else sheet_names[0]
    ws = wb[preferred_sheet]

    header_row = next(ws.iter_rows(min_row=1, max_row=1, values_only=True), None)
    headers = [str(value).strip() if value is not None else "" for value in (header_row or [])]
    normalized_headers = {normalize_header_name(header): idx for idx, header in enumerate(headers) if header}

    def _find_col(aliases: Iterable[str]) -> Optional[int]:
        for alias in aliases:
            idx = normalized_headers.get(normalize_header_name(alias))
            if idx is not None:
                return idx
        return None

    cnes_col = _find_col(["cnes"])
    competencia_col = _find_col(["competencia"])
    quantity_col = _find_col(["prd-qt", "prd_qt", "qtd", "quantidade"])

    cnes_counts: Dict[str, int] = {}
    competencias = set()
    total_records = max((ws.max_row or 1) - 1, 0)
    total_quantidade = 0

    for row in ws.iter_rows(min_row=2, values_only=True):
        if cnes_col is not None and cnes_col < len(row):
            cnes = _normalize_cnes(row[cnes_col])
            if cnes:
                cnes_counts[cnes] = cnes_counts.get(cnes, 0) + 1
        if competencia_col is not None and competencia_col < len(row):
            competencia = _normalize_text(row[competencia_col])
            if competencia:
                competencias.add(competencia)
        if quantity_col is not None and quantity_col < len(row):
            total_quantidade += _parse_quantity(row[quantity_col], default=0)

    wb.close()

    return {
        "file_name": file_name,
        "kind": "bpa",
        "detected_format": "excel",
        "sheet_names": sheet_names,
        "total_registros": total_records,
        "total_pacientes": 0,
        "total_procedimentos": total_records,
        "total_quantidade": total_quantidade,
        "competencias": sorted(competencias),
        "cnes_summary": _summarize_cnes_counts(cnes_counts),
        "preview_mode": True,
    }


def analyze_uploaded_file(file_name: str, file_bytes: bytes, kind: str, quick_preview: bool = False) -> Dict[str, object]:
    kind = _normalize_text(kind).lower()
    is_excel = file_name.lower().endswith((".xlsx", ".xls"))

    if kind == "apac":
        if is_excel:
            analysis = _analyze_apac_excel(file_name, file_bytes)
        else:
            analysis = _analyze_apac_txt_preview(file_name, file_bytes) if quick_preview else _analyze_apac_txt(file_name, file_bytes)
    elif kind == "bpa":
        if is_excel:
            analysis = _analyze_bpa_excel_preview(file_name, file_bytes) if quick_preview else _analyze_bpa_excel(file_name, file_bytes)
        else:
            analysis = _analyze_bpa_txt_preview(file_name, file_bytes) if quick_preview else _analyze_bpa_txt(file_name, file_bytes)
    else:
        raise HttpError(400, "Tipo de analise invalido. Use 'apac' ou 'bpa'.")

    analysis["extension"] = Path(file_name).suffix.lower()
    analysis["multiple_units"] = len(analysis["cnes_summary"]["units"]) > 1
    return analysis


def _resolve_import_unit(apac_analysis: Dict[str, object], bpa_analysis: Dict[str, object]) -> Optional[Dict[str, object]]:
    apac_primary = (apac_analysis or {}).get("cnes_summary", {}).get("primary_unit")
    bpa_primary = (bpa_analysis or {}).get("cnes_summary", {}).get("primary_unit")
    if apac_primary and bpa_primary and apac_primary.get("cnes") == bpa_primary.get("cnes"):
        return apac_primary
    return apac_primary or bpa_primary


def _normalize_prefix(value: str) -> str:
    return "".join(ch for ch in str(value or "") if ch.isdigit())


def _patient_key(name: str, dob: str) -> Tuple[str, str]:
    return (normalize_name(name), normalize_date(dob))


def _ensure_patient_bucket(
    bucket: Dict[Tuple[str, str], Dict[str, object]],
    name: str,
    dob: str,
) -> Optional[Tuple[str, str]]:
    normalized_name = normalize_name(name)
    normalized_dob = normalize_date(dob)
    if not normalized_name:
        return None

    key = (normalized_name, normalized_dob)
    if key not in bucket:
        bucket[key] = {
            "name": normalized_name,
            "dob": normalized_dob,
            "cpf": "",
            "cns": "",
            "procedures": {},
            "procedure_contexts": {},
            "cbos": set(),
            "cids": set(),
            "cid_sources": set(),
            "service_dates": set(),
            "competencias": set(),
            "apac_numbers": set(),
            "autorizacoes": set(),
            "sources": set(),
            "source_origins": {},
        }
    return key


def _add_patient_procedure(
    bucket: Dict[Tuple[str, str], Dict[str, object]],
    patient_key: Optional[Tuple[str, str]],
    procedure_code: str,
    quantity: int = 1,
    source: str = "",
) -> None:
    if not patient_key:
        return

    normalized_code = _normalize_proc_code(procedure_code)
    if not normalized_code:
        return

    patient = bucket[patient_key]
    procedures = patient["procedures"]
    procedures[normalized_code] = procedures.get(normalized_code, 0) + _parse_quantity(quantity, default=1)
    patient.setdefault("procedure_contexts", {}).setdefault(
        normalized_code,
        {"cbos": set(), "cids": set()},
    )
    if source:
        patient["sources"].add(source)


def _add_patient_context(
    bucket: Dict[Tuple[str, str], Dict[str, object]],
    patient_key: Optional[Tuple[str, str]],
    procedure_code: str = "",
    cbo_code: str = "",
    cid_code: str = "",
    source: str = "",
) -> None:
    if not patient_key:
        return

    patient = bucket[patient_key]
    normalized_proc = _normalize_proc_code(procedure_code)
    normalized_cbo = _normalize_cbo_code(cbo_code)
    normalized_cid = _normalize_cid_code(cid_code)
    if normalized_cbo:
        patient["cbos"].add(normalized_cbo)
    if normalized_cid:
        patient["cids"].add(normalized_cid)
        if source:
            patient.setdefault("cid_sources", set()).add(source)
    if normalized_proc:
        procedure_context = patient.setdefault("procedure_contexts", {}).setdefault(
            normalized_proc,
            {"cbos": set(), "cids": set()},
        )
        if normalized_cbo:
            procedure_context["cbos"].add(normalized_cbo)
        if normalized_cid:
            procedure_context["cids"].add(normalized_cid)
    if source and (normalized_cbo or normalized_cid):
        patient["sources"].add(source)


def _add_patient_timing_context(
    bucket: Dict[Tuple[str, str], Dict[str, object]],
    patient_key: Optional[Tuple[str, str]],
    service_date: str = "",
    competencia: str = "",
) -> None:
    if not patient_key:
        return

    patient = bucket[patient_key]
    normalized_service_date = normalize_date(service_date)
    normalized_competencia = _normalize_competencia_code(competencia)
    if len(normalized_service_date) == 8 and normalized_service_date.isdigit():
        patient["service_dates"].add(normalized_service_date)
    if normalized_competencia:
        patient["competencias"].add(normalized_competencia)


def _add_patient_identifiers(
    bucket: Dict[Tuple[str, str], Dict[str, object]],
    patient_key: Optional[Tuple[str, str]],
    cpf: str = "",
    cns: str = "",
) -> None:
    if not patient_key:
        return

    patient = bucket[patient_key]
    normalized_cpf = normalize_cpf(cpf)
    normalized_cns = normalize_cns(cns)
    if normalized_cpf and not patient.get("cpf"):
        patient["cpf"] = normalized_cpf
    if normalized_cns and not patient.get("cns"):
        patient["cns"] = normalized_cns
        
def _add_patient_autorizacao(
    bucket: Dict[Tuple[str, str], Dict[str, object]],
    patient_key: Optional[Tuple[str, str]],
    autorizacao: str = "",
) -> None:
    if not patient_key:
        return

    patient = bucket[patient_key]
    auth_str = str(autorizacao or "").strip()
    if auth_str:
        patient["autorizacoes"].add(auth_str)

def _serialize_patient_bucket(patient: Dict[str, object]) -> Dict[str, object]:
    return {
        "name": patient["name"],
        "dob": patient["dob"],
        "cpf": patient.get("cpf") or "",
        "cns": patient.get("cns") or "",
        "procedures": dict(sorted((patient.get("procedures") or {}).items())),
        "procedure_contexts": {
            proc_code: {
                "cbos": sorted(context.get("cbos") or []),
                "cids": sorted(context.get("cids") or []),
            }
            for proc_code, context in sorted((patient.get("procedure_contexts") or {}).items())
        },
        "cbos": sorted(patient.get("cbos") or []),
        "cids": sorted(patient.get("cids") or []),
        "cid_sources": sorted(patient.get("cid_sources") or []),
        "service_dates": sorted(patient.get("service_dates") or []),
        "competencias": sorted(patient.get("competencias") or []),
        "apac_numbers": sorted(patient.get("apac_numbers") or []),
        "sources": sorted(patient.get("sources") or []),
        "source_origins": {
            source_key: sorted(source_files or [])
            for source_key, source_files in sorted((patient.get("source_origins") or {}).items())
        },
    }


def _register_patient_map_origin(
    patient_map: Dict[Tuple[str, str], Dict[str, object]],
    source_key: str,
    file_name: str,
) -> Dict[Tuple[str, str], Dict[str, object]]:
    normalized_source = _normalize_text(source_key).upper()
    normalized_file_name = os.path.basename(str(file_name or "").strip())
    if not normalized_source or not normalized_file_name:
        return patient_map

    for patient in patient_map.values():
        origins = patient.setdefault("source_origins", {})
        origins.setdefault(normalized_source, set()).add(normalized_file_name)
    return patient_map


def _aggregate_apac_patient_procedures_excel(file_name: str, file_bytes: bytes) -> Dict[Tuple[str, str], Dict[str, object]]:
    engine = "openpyxl" if file_name.lower().endswith(".xlsx") else None
    workbook = pd.ExcelFile(io.BytesIO(file_bytes), engine=engine)
    if "CORPO" not in workbook.sheet_names:
        raise HttpError(400, "Aba 'CORPO' nao encontrada no arquivo APAC.")

    df_corpo = pd.read_excel(workbook, sheet_name="CORPO", header=3, dtype=str)
    df_proc = pd.read_excel(workbook, sheet_name="PROCEDIMENTOS", header=3, dtype=str) if "PROCEDIMENTOS" in workbook.sheet_names else pd.DataFrame()

    name_col = _extract_excel_column_name(df_corpo.columns, ["apa_nomepcnte", "nome_paciente"])
    dob_col = _extract_excel_column_name(df_corpo.columns, ["apa_datanascim", "data_nasc"])
    apac_num_col = _extract_excel_column_name(df_corpo.columns, ["apa_num", "numero_apac"])
    proc_principal_col = _extract_excel_column_name(df_corpo.columns, ["apa_codprinc", "cod_proc_princ"])

    if not name_col or not dob_col:
        raise HttpError(400, "Colunas do paciente nao encontradas na aba CORPO do arquivo APAC.")

    patient_map: Dict[Tuple[str, str], Dict[str, object]] = {}
    apac_to_patient: Dict[str, Tuple[str, str]] = {}

    for _, row in df_corpo.iterrows():
        key = _ensure_patient_bucket(patient_map, row.get(name_col), row.get(dob_col))
        if not key:
            continue

        patient = patient_map[key]
        patient["sources"].add("APAC")
        apac_num = _normalize_text(row.get(apac_num_col)) if apac_num_col else ""
        if apac_num:
            patient["apac_numbers"].add(apac_num)
            apac_to_patient[apac_num] = key
        if proc_principal_col:
            _add_patient_procedure(patient_map, key, row.get(proc_principal_col), 1, "APAC")

    if not df_proc.empty:
        proc_num_col = _extract_excel_column_name(df_proc.columns, ["pap_num", "numero_apac"])
        proc_cod_col = _extract_excel_column_name(df_proc.columns, ["pap_codproc", "cod_proc"])
        qtd_col = _extract_excel_column_name(df_proc.columns, ["pap_qtdprod", "quantidade"])

        if proc_num_col and proc_cod_col:
            for _, row in df_proc.iterrows():
                apac_num = _normalize_text(row.get(proc_num_col))
                patient_key = apac_to_patient.get(apac_num)
                if not patient_key:
                    continue
                _add_patient_procedure(
                    patient_map,
                    patient_key,
                    row.get(proc_cod_col),
                    _parse_quantity(row.get(qtd_col), default=1),
                    "APAC",
                )

    return patient_map


def _aggregate_apac_patient_procedures_txt(file_bytes: bytes) -> Dict[Tuple[str, str], Dict[str, object]]:
    patient_map: Dict[Tuple[str, str], Dict[str, object]] = {}
    apac_to_patient: Dict[str, Tuple[str, str]] = {}
    
    body_records = _get_parsed_fixed_width_records(file_bytes, APAC_CORPO_LAYOUT, "14")
    proc_records = _get_parsed_fixed_width_records(file_bytes, APAC_PROC_LAYOUT, "13")

    for rec in body_records:
        key = _ensure_patient_bucket(patient_map, rec.get("nome_paciente"), rec.get("data_nasc"))
        if not key:
            continue

        patient = patient_map[key]
        patient["sources"].add("APAC")
        apac_num = _normalize_text(rec.get("numero_apac"))
        if apac_num:
            patient["apac_numbers"].add(apac_num)
            apac_to_patient[apac_num] = key
        _add_patient_procedure(patient_map, key, rec.get("cod_proc_princ"), 1, "APAC")

    for rec in proc_records:
        apac_num = _normalize_text(rec.get("numero_apac"))
        patient_key = apac_to_patient.get(apac_num)
        if not patient_key:
            continue
        _add_patient_procedure(
            patient_map,
            patient_key,
            rec.get("cod_proc"),
            _parse_quantity(rec.get("quantidade"), default=1),
            "APAC",
        )

    return patient_map


def _aggregate_bpa_patient_procedures_excel(file_name: str, file_bytes: bytes) -> Dict[Tuple[str, str], Dict[str, object]]:
    engine = "openpyxl" if file_name.lower().endswith(".xlsx") else None
    workbook = pd.ExcelFile(io.BytesIO(file_bytes), engine=engine)
    preferred_sheet = "bpa original" if "bpa original" in workbook.sheet_names else workbook.sheet_names[0]
    df_bpa = pd.read_excel(workbook, sheet_name=preferred_sheet, header=0, dtype=str)

    name_col = _extract_excel_column_name(df_bpa.columns, ["prd-nmpac", "nome_paciente"])
    dob_col = _extract_excel_column_name(df_bpa.columns, ["prd-dtnasc", "data_nasc"])
    proc_col = _extract_excel_column_name(df_bpa.columns, ["prd-pa", "prd_pa", "procedimento"])
    qtd_col = _extract_excel_column_name(df_bpa.columns, ["prd-qt", "prd_qt", "qtd", "quantidade"])
    cbo_col = _extract_excel_column_name(df_bpa.columns, ["prd-cbo", "prd_cbo", "cbo"])
    cid_col = _extract_excel_column_name(df_bpa.columns, ["prd-cid", "prd_cid", "cid10", "cid"])
    cns_col = _extract_excel_column_name(df_bpa.columns, BPA_I_EXCEL_ALIASES.get("cns_paciente", []))
    cpf_col = _extract_excel_column_name(df_bpa.columns, BPA_I_EXCEL_ALIASES.get("cpf_paciente", []))
    data_atend_col = _extract_excel_column_name(df_bpa.columns, ["data_atend", "data-atend", "prd-dataat", "prd_dataat"])
    competencia_col = _extract_excel_column_name(df_bpa.columns, ["competencia"])
    auth_col = _extract_excel_column_name(df_bpa.columns, BPA_I_EXCEL_ALIASES.get("n_autorizacao", [])) # COLUNA MAPEADA

    if not name_col or not dob_col or not proc_col:
        raise HttpError(400, "Colunas obrigatorias do BPA nao foram encontradas.")

    patient_map: Dict[Tuple[str, str], Dict[str, object]] = {}
    for _, row in df_bpa.iterrows():
        key = _ensure_patient_bucket(patient_map, row.get(name_col), row.get(dob_col))
        if not key:
            continue
        patient_map[key]["sources"].add("BPA")
        _add_patient_context(
            patient_map,
            key,
            row.get(proc_col),
            row.get(cbo_col) if cbo_col else "",
            row.get(cid_col) if cid_col else "",
            "BPA",
        )
        _add_patient_timing_context(patient_map, key, row.get(data_atend_col) if data_atend_col else "", row.get(competencia_col) if competencia_col else "")
        _add_patient_identifiers(
            patient_map,
            key,
            row.get(cpf_col) if cpf_col else "",
            row.get(cns_col) if cns_col else "",
        )
        _add_patient_autorizacao(patient_map, key, row.get(auth_col) if auth_col else "") # INSERE AUTORIZACAO
        _add_patient_procedure(
            patient_map,
            key,
            row.get(proc_col),
            _parse_quantity(row.get(qtd_col), default=1),
            "BPA",
        )

    return patient_map


def _aggregate_bpa_patient_procedures_txt(file_bytes: bytes) -> Dict[Tuple[str, str], Dict[str, object]]:
    patient_map: Dict[Tuple[str, str], Dict[str, object]] = {}
    records = _get_parsed_fixed_width_records(file_bytes, BPA_I_LAYOUT, "03")
    for rec in records:
        key = _ensure_patient_bucket(patient_map, rec.get("nome_paciente"), rec.get("data_nasc"))
        if not key:
            continue
        patient_map[key]["sources"].add("BPA")
        _add_patient_context(patient_map, key, rec.get("procedimento"), rec.get("cbo"), rec.get("cid10"), "BPA")
        _add_patient_timing_context(patient_map, key, rec.get("data_atend"), rec.get("competencia"))
        _add_patient_identifiers(patient_map, key, rec.get("cpf_paciente"), rec.get("cns_paciente"))
        _add_patient_autorizacao(patient_map, key, rec.get("n_autorizacao")) # INSERE AUTORIZACAO
        _add_patient_procedure(
            patient_map,
            key,
            rec.get("procedimento"),
            _parse_quantity(rec.get("quantidade"), default=1),
            "BPA",
        )
    return patient_map


def _get_oci_sheet_allowed_proc_codes() -> set:
    allowed_codes = set()
    for combo in OCI_COMBO_RULES:
        for rule in (*combo.required, *combo.optional):
            for code in (rule.codes or ()):
                normalized_code = _normalize_proc_code(code)
                if normalized_code:
                    allowed_codes.add(normalized_code)
    return allowed_codes


def _detect_procedures_sheet_header_row(df_raw: pd.DataFrame) -> int:
    patient_aliases = {"paciente", "nome-paciente", "nome-do-paciente"}
    dob_aliases = {"nascimento", "data-nasc", "data-nascimento"}
    procedure_aliases = {"procedimento", "procedimento-sigtap", "procedimento-id", "codigo-sigtap"}
    max_rows = min(len(df_raw.index), 12)
    for row_index in range(max_rows):
        row_values = {
            normalize_header_name(value)
            for value in df_raw.iloc[row_index].tolist()
            if normalize_header_name(value)
        }
        has_patient = bool(row_values.intersection(patient_aliases))
        has_dob = bool(row_values.intersection(dob_aliases))
        has_procedure = bool(row_values.intersection(procedure_aliases))
        if has_patient and has_procedure:
            return row_index
    return 0


def _get_oci_procedures_sheet_columns(df_sheet: pd.DataFrame) -> Dict[str, str]:
    return {
        "patient": _extract_excel_column_name(df_sheet.columns, ["paciente", "nome_paciente", "nome_do_paciente"]),
        "dob": _extract_excel_column_name(df_sheet.columns, ["nascimento", "data_nasc", "data_nascimento"]),
        "procedure_code": _extract_excel_column_name(df_sheet.columns, ["procedimento_id", "codigo_sigtap", "procedimento_sigtap"]),
        "procedure": _extract_excel_column_name(df_sheet.columns, ["procedimento", "procedimento_sigtap", "procedimento_id"]),
        "quantity": _extract_excel_column_name(df_sheet.columns, ["qtde", "quantidade", "qtd"]),
        "cpf_patient": _extract_excel_column_name(df_sheet.columns, ["cpf_paciente", "cpf paciente", "cpf_do_paciente"]),
        "cpf": _extract_excel_column_name(df_sheet.columns, ["cpf"]),
        "cns_patient": _extract_excel_column_name(df_sheet.columns, ["cns_paciente", "cns paciente"]),
        "service_date": _extract_excel_column_name(df_sheet.columns, ["data", "atendimento", "data_atendimento", "data_procedimento"]),
        "cbo": _extract_excel_column_name(df_sheet.columns, ["cbo", "codigo_cbo"]),
        "cid_principal": _extract_excel_column_name(df_sheet.columns, ["cid_principal_id", "cid principal id", "cid_id", "cid10", "cid", "cid_principal", "cid principal"]),
        "cid_secondary": _extract_excel_column_name(df_sheet.columns, ["cid_secundario_id", "cid secundario id", "cid_sec_id", "cid_secundario", "cid secundario", "cid_sec", "cid secundário"]),
        "provider": _extract_excel_column_name(df_sheet.columns, ["prestador", "nome_profissional", "profissional"]),
    }


def _read_cce_procedures_sheet(file_name: str, file_bytes: bytes) -> pd.DataFrame:
    lower_name = file_name.lower()
    engine = "openpyxl" if lower_name.endswith(".xlsx") else "xlrd" if lower_name.endswith(".xls") else None
    workbook = pd.ExcelFile(io.BytesIO(file_bytes), engine=engine)
    preferred_sheet = workbook.sheet_names[0]
    df_raw = pd.read_excel(workbook, sheet_name=preferred_sheet, header=None, dtype=str).fillna("")
    header_row = _detect_procedures_sheet_header_row(df_raw)
    headers = []
    for index, value in enumerate(df_raw.iloc[header_row].tolist()):
        label = str(value or "").strip()
        headers.append(label or f"coluna_{index + 1}")
    df_sheet = df_raw.iloc[header_row + 1 :].copy()
    df_sheet.columns = headers
    return df_sheet.fillna("")


def _build_cce_procedures_analysis(file_name: str, file_bytes: bytes) -> Dict[str, object]:
    df_sheet = _read_cce_procedures_sheet(file_name, file_bytes)
    columns = _get_oci_procedures_sheet_columns(df_sheet)
    patient_col = columns["patient"]
    dob_col = columns["dob"]
    procedure_code_col = columns["procedure_code"]
    procedure_text_col = columns["procedure"]
    proc_source_col = procedure_code_col or procedure_text_col
    qty_col = columns["quantity"]
    cpf_patient_col = columns["cpf_patient"]
    cpf_col = columns["cpf"]
    cns_patient_col = columns["cns_patient"]
    service_date_col = columns["service_date"]
    cbo_col = columns["cbo"]
    cid_principal_col = columns["cid_principal"]
    cid_secondary_col = columns["cid_secondary"]
    provider_col = columns["provider"]

    if not patient_col or not proc_source_col:
        raise HttpError(400, "A planilha complementar precisa conter as colunas PACIENTE e PROCEDIMENTO ou PROCEDIMENTO_ID.")

    allowed_proc_codes = _get_oci_sheet_allowed_proc_codes()
    relevant_rows = 0
    total_quantity = 0
    providers = set()

    for _, row in df_sheet.iterrows():
        normalized_procs = [
            proc_code
            for proc_code in _resolve_oci_sheet_procedure_codes(row, procedure_code_col, procedure_text_col)
            if proc_code in allowed_proc_codes
        ]
        if not normalized_procs:
            continue
        relevant_rows += 1
        total_quantity += _parse_quantity(row.get(qty_col) if qty_col else "", default=1) * len(normalized_procs)
        provider = _normalize_text(row.get(provider_col)) if provider_col else ""
        if provider:
            providers.add(provider)

    return {
        "file_name": file_name,
        "detected_format": "Planilha complementar",
        "detected_kind": "oci_procedures_sheet",
        "status": True,
        "total_rows": int(len(df_sheet.index)),
        "matched_rows": relevant_rows,
        "matched_quantity": total_quantity,
        "providers": sorted(providers),
        "scope": "OCI complementar",
        "column_map": {
            "patient": patient_col,
            "dob": dob_col,
            "procedure": proc_source_col,
            "quantity": qty_col or "",
            "cpf_patient": cpf_patient_col or "",
            "cpf": cpf_col or "",
            "cns_patient": cns_patient_col or "",
            "service_date": service_date_col or "",
            "cbo": cbo_col or "",
            "cid_principal": cid_principal_col or "",
            "cid_secondary": cid_secondary_col or "",
            "provider": provider_col or "",
        },
    }


def _aggregate_cce_procedures_sheet(file_name: str, file_bytes: bytes) -> Dict[Tuple[str, str], Dict[str, object]]:
    df_sheet = _read_cce_procedures_sheet(file_name, file_bytes)
    columns = _get_oci_procedures_sheet_columns(df_sheet)
    patient_col = columns["patient"]
    dob_col = columns["dob"]
    procedure_code_col = columns["procedure_code"]
    procedure_text_col = columns["procedure"]
    proc_source_col = procedure_code_col or procedure_text_col
    qty_col = columns["quantity"]
    cpf_patient_col = columns["cpf_patient"]
    cpf_col = columns["cpf"]
    cns_patient_col = columns["cns_patient"]
    service_date_col = columns["service_date"]
    cbo_col = columns["cbo"]
    cid_principal_col = columns["cid_principal"]
    cid_secondary_col = columns["cid_secondary"]

    if not patient_col or not proc_source_col:
        raise HttpError(400, "A planilha complementar precisa conter as colunas PACIENTE e PROCEDIMENTO ou PROCEDIMENTO_ID.")

    allowed_proc_codes = _get_oci_sheet_allowed_proc_codes()
    patient_map: Dict[Tuple[str, str], Dict[str, object]] = {}
    for _, row in df_sheet.iterrows():
        normalized_procs = []
        for proc_code in _resolve_oci_sheet_procedure_codes(row, procedure_code_col, procedure_text_col):
            normalized_procs.append(proc_code)
        if not normalized_procs:
            continue

        key = _ensure_patient_bucket(patient_map, row.get(patient_col), row.get(dob_col))
        if not key:
            continue

        patient_map[key]["sources"].add("PLANILHA_PROCEDIMENTOS")
        _add_patient_identifiers(
            patient_map,
            key,
            row.get(cpf_patient_col) if cpf_patient_col else row.get(cpf_col) if cpf_col else "",
            row.get(cns_patient_col) if cns_patient_col else "",
        )
        for normalized_proc in normalized_procs:
            _add_patient_context(
                patient_map,
                key,
                normalized_proc,
                row.get(cbo_col) if cbo_col else "",
                row.get(cid_principal_col) if cid_principal_col else "",
                "PLANILHA_PROCEDIMENTOS",
            )
        secondary_cid = row.get(cid_secondary_col) if cid_secondary_col else ""
        if _normalize_cid_code(secondary_cid):
            for normalized_proc in normalized_procs:
                _add_patient_context(
                    patient_map,
                    key,
                    normalized_proc,
                    row.get(cbo_col) if cbo_col else "",
                    secondary_cid,
                    "PLANILHA_PROCEDIMENTOS",
                )
        _add_patient_timing_context(patient_map, key, row.get(service_date_col) if service_date_col else "", "")
        for normalized_proc in normalized_procs:
            _add_patient_procedure(
                patient_map,
                key,
                normalized_proc,
                _parse_quantity(row.get(qty_col), default=1) if qty_col else 1,
                "PLANILHA_PROCEDIMENTOS",
            )

    return patient_map


def _aggregate_patient_procedures(kind: str, file_name: str, file_bytes: bytes) -> Dict[Tuple[str, str], Dict[str, object]]:
    normalized_kind = _normalize_text(kind).lower()
    is_excel = file_name.lower().endswith((".xlsx", ".xls"))
    if normalized_kind == "apac":
        patient_map = _aggregate_apac_patient_procedures_excel(file_name, file_bytes) if is_excel else _aggregate_apac_patient_procedures_txt(file_bytes)
        return _register_patient_map_origin(patient_map, "APAC", file_name)
    if normalized_kind == "bpa":
        patient_map = _aggregate_bpa_patient_procedures_excel(file_name, file_bytes) if is_excel else _aggregate_bpa_patient_procedures_txt(file_bytes)
        return _register_patient_map_origin(patient_map, "BPA", file_name)
    if normalized_kind == "oci_procedures_sheet":
        patient_map = _aggregate_cce_procedures_sheet(file_name, file_bytes)
        return _register_patient_map_origin(patient_map, "PLANILHA_PROCEDIMENTOS", file_name)
    raise HttpError(400, "Tipo invalido para agregacao de procedimentos.")


def _merge_patient_maps(
    base_map: Dict[Tuple[str, str], Dict[str, object]],
    extra_map: Dict[Tuple[str, str], Dict[str, object]],
) -> Dict[Tuple[str, str], Dict[str, object]]:
    return _merge_many_patient_maps([base_map, extra_map])


def _merge_many_patient_maps(patient_maps: Iterable[Dict[Tuple[str, str], Dict[str, object]]]) -> Dict[Tuple[str, str], Dict[str, object]]:
    merged: Dict[Tuple[str, str], Dict[str, object]] = {}
    cpf_index: Dict[str, Tuple[str, str]] = {}
    cns_index: Dict[str, Tuple[str, str]] = {}
    dob_index: Dict[str, List[Tuple[str, str]]] = {}
    name_index: Dict[str, List[Tuple[str, str]]] = {}

    for patient_map in patient_maps or []:
        if not patient_map:
            continue
        for patient_key, patient in patient_map.items():
            patient_name = patient.get("name") or patient_key[0]
            patient_dob = patient.get("dob") or patient_key[1]
            normalized_cpf = normalize_cpf(patient.get("cpf"))
            normalized_cns = normalize_cns(patient.get("cns"))

            merge_key = patient_key
            if normalized_cpf and normalized_cpf in cpf_index:
                merge_key = cpf_index[normalized_cpf]
            elif normalized_cns and normalized_cns in cns_index:
                merge_key = cns_index[normalized_cns]
            else:
                similar_key = None
                for existing_key in dob_index.get(patient_dob, []):
                    if is_similar(patient_name, existing_key[0]):
                        similar_key = existing_key
                        break
                if not similar_key:
                    norm_pname = normalize_name(patient_name)
                    for existing_key in name_index.get(norm_pname, []):
                        if not patient_dob or not existing_key[1]:
                            similar_key = existing_key
                            break
                if similar_key:
                    merge_key = similar_key

            is_new = (merge_key not in merged)
            current = merged.setdefault(
                merge_key,
                {
                    "name": patient.get("name") or patient_key[0],
                    "dob": patient.get("dob") or patient_key[1],
                    "cpf": patient.get("cpf") or "",
                    "cns": patient.get("cns") or "",
                    "procedures": {},
                    "procedure_contexts": {},
                    "cbos": set(),
                    "cids": set(),
                    "cid_sources": set(),
                    "service_dates": set(),
                    "competencias": set(),
                    "autorizacoes": set(),
                    "apac_numbers": set(),
                    "sources": set(),
                    "source_origins": {},
                },
            )
            
            if is_new:
                if normalized_cpf:
                    cpf_index[normalized_cpf] = merge_key
                if normalized_cns:
                    cns_index[normalized_cns] = merge_key
                if patient_dob:
                    dob_index.setdefault(patient_dob, []).append(merge_key)
                norm_pname = normalize_name(patient_name)
                if norm_pname:
                    name_index.setdefault(norm_pname, []).append(merge_key)

            # Update fields
            current["cbos"].update(patient.get("cbos") or set())
            current["cids"].update(patient.get("cids") or set())
            current["cid_sources"].update(patient.get("cid_sources") or set())
            current["service_dates"].update(patient.get("service_dates") or set())
            current["competencias"].update(patient.get("competencias") or set())
            current["apac_numbers"].update(patient.get("apac_numbers") or set())
            current["autorizacoes"].update(patient.get("autorizacoes") or set())
            current["sources"].update(patient.get("sources") or set())
            for source_key, source_files in (patient.get("source_origins") or {}).items():
                current["source_origins"].setdefault(source_key, set()).update(source_files or set())
            
            if not current.get("cpf") and patient.get("cpf"):
                new_cpf = patient.get("cpf")
                current["cpf"] = new_cpf
                norm_cpf = normalize_cpf(new_cpf)
                if norm_cpf:
                    cpf_index[norm_cpf] = merge_key
            if not current.get("cns") and patient.get("cns"):
                new_cns = patient.get("cns")
                current["cns"] = new_cns
                norm_cns = normalize_cns(new_cns)
                if norm_cns:
                    cns_index[norm_cns] = merge_key

            for proc_code, context in (patient.get("procedure_contexts") or {}).items():
                current_context = current["procedure_contexts"].setdefault(
                    proc_code,
                    {"cbos": set(), "cids": set()},
                )
                current_context["cbos"].update(context.get("cbos") or set())
                current_context["cids"].update(context.get("cids") or set())
            for proc_code, qty in (patient.get("procedures") or {}).items():
                current["procedures"][proc_code] = current["procedures"].get(proc_code, 0) + int(qty or 0)

    return merged


def _build_multi_file_cnes_summary(analyses: List[Dict[str, object]]) -> Dict[str, object]:
    units_by_cnes: Dict[str, Dict[str, object]] = {}
    for analysis in analyses or []:
        cnes_summary = analysis.get("cnes_summary") or {}
        for unit in cnes_summary.get("units") or []:
            normalized_cnes = _normalize_cnes(unit.get("cnes"))
            if not normalized_cnes:
                continue
            current = units_by_cnes.setdefault(
                normalized_cnes,
                {
                    "cnes": normalized_cnes,
                    "nome_unidade": unit.get("nome_unidade") or units_by_cnes.get(normalized_cnes, {}).get("nome_unidade") or "Unidade nao identificada",
                    "count": 0,
                },
            )
            current["count"] += int(unit.get("count") or 0)
            if not current.get("nome_unidade") and unit.get("nome_unidade"):
                current["nome_unidade"] = unit.get("nome_unidade")

    units = sorted(units_by_cnes.values(), key=lambda item: (-int(item.get("count") or 0), item.get("cnes") or ""))
    return {
        "primary_unit": units[0] if len(units) == 1 else None,
        "units": units,
    }


def _resolve_oci_consolidated_unit(analyses: List[Dict[str, object]]) -> Optional[Dict[str, object]]:
    multi_summary = _build_multi_file_cnes_summary(analyses)
    units = multi_summary.get("units") or []
    if not units:
        return None
    if len(units) == 1:
        return units[0]
    return {
        "cnes": "",
        "nome_unidade": f"Analise consolidada de {len(units)} CNES",
        "count": sum(int(item.get("count") or 0) for item in units),
    }


def _summarize_oci_bpa_analyses(analyses: List[Dict[str, object]]) -> Dict[str, object]:
    normalized_analyses = [analysis for analysis in (analyses or []) if isinstance(analysis, dict)]
    if not normalized_analyses:
        return {}
    if len(normalized_analyses) == 1:
        analysis = dict(normalized_analyses[0])
        analysis["file_count"] = 1
        analysis["analysis_mode"] = "single_bpa"
        analysis["input_files"] = [
            {
                "file_name": analysis.get("file_name") or "",
                "detected_format": analysis.get("detected_format") or "",
                "competencias": analysis.get("competencias") or [],
                "cnes_summary": analysis.get("cnes_summary") or {},
            }
        ]
        return analysis

    combined_summary = _build_multi_file_cnes_summary(normalized_analyses)
    return {
        "kind": "bpa",
        "file_name": f"{len(normalized_analyses)} arquivos BPA",
        "detected_format": "Multiplos arquivos",
        "detected_kind": "bpa",
        "status": True,
        "file_count": len(normalized_analyses),
        "analysis_mode": "multi_bpa",
        "input_files": [
            {
                "file_name": analysis.get("file_name") or "",
                "detected_format": analysis.get("detected_format") or "",
                "competencias": analysis.get("competencias") or [],
                "cnes_summary": analysis.get("cnes_summary") or {},
                "total_registros": analysis.get("total_registros") or 0,
                "total_procedimentos": analysis.get("total_procedimentos") or 0,
                "total_quantidade": analysis.get("total_quantidade") or 0,
            }
            for analysis in normalized_analyses
        ],
        "competencias": sorted(
            {
                competencia
                for analysis in normalized_analyses
                for competencia in (analysis.get("competencias") or [])
                if competencia
            }
        ),
        "total_registros": sum(int(analysis.get("total_registros") or 0) for analysis in normalized_analyses),
        "total_procedimentos": sum(int(analysis.get("total_procedimentos") or 0) for analysis in normalized_analyses),
        "total_quantidade": sum(int(analysis.get("total_quantidade") or 0) for analysis in normalized_analyses),
        "cnes_summary": combined_summary,
        "multiple_units": len(combined_summary.get("units") or []) > 1,
    }


def _get_oci_bpa_uploaded_files(request) -> List[UploadedFile]:
    files = [uploaded for uploaded in request.FILES.getlist("bpa_files") if uploaded]
    if files:
        return files
    single_file = request.FILES.get("bpa_file")
    return [single_file] if single_file else []


def _get_oci_procedures_uploaded_files(request) -> List[UploadedFile]:
    files = [uploaded for uploaded in request.FILES.getlist("procedures_files") if uploaded]
    if files:
        return files
    legacy_multi_files = [uploaded for uploaded in request.FILES.getlist("procedures_file") if uploaded]
    if legacy_multi_files:
        return legacy_multi_files
    single_file = request.FILES.get("procedures_file")
    return [single_file] if single_file else []


def _build_oci_history_filename_label(
    uploaded_files: List[UploadedFile],
    procedures_files: Optional[List[UploadedFile]] = None,
) -> str:
    bpa_files = [uploaded for uploaded in (uploaded_files or []) if uploaded]
    supplemental_files = [uploaded for uploaded in (procedures_files or []) if uploaded]
    total_files = len(bpa_files) + len(supplemental_files)

    if total_files == 0:
        return "N/A"
    if len(bpa_files) == 1 and not supplemental_files:
        return bpa_files[0].name
    if len(supplemental_files) == 1 and not bpa_files:
        return supplemental_files[0].name
    if bpa_files and supplemental_files:
        return f"{len(bpa_files)} BPA(s) + {len(supplemental_files)} planilha(s)"
    if len(bpa_files) > 1:
        return f"{len(bpa_files)} arquivos BPA"
    return f"{len(supplemental_files)} planilha(s) complementar(es)"


def _summarize_oci_supplemental_analyses(analyses: List[Dict[str, object]]) -> Optional[Dict[str, object]]:
    valid_analyses = [analysis for analysis in (analyses or []) if analysis]
    if not valid_analyses:
        return None
    if len(valid_analyses) == 1:
        return valid_analyses[0]

    providers = sorted(
        {
            str(provider).strip()
            for analysis in valid_analyses
            for provider in (analysis.get("providers") or [])
            if str(provider).strip()
        }
    )
    return {
        "file_name": f"{len(valid_analyses)} planilhas complementares",
        "file_names": [analysis.get("file_name") or "" for analysis in valid_analyses if analysis.get("file_name")],
        "detected_format": "Múltiplas planilhas complementares",
        "detected_kind": "oci_procedures_sheet",
        "status": True,
        "total_rows": sum(int(analysis.get("total_rows") or 0) for analysis in valid_analyses),
        "matched_rows": sum(int(analysis.get("matched_rows") or 0) for analysis in valid_analyses),
        "matched_quantity": sum(int(analysis.get("matched_quantity") or 0) for analysis in valid_analyses),
        "providers": providers,
        "scope": valid_analyses[0].get("scope") or "OCI complementar",
        "file_count": len(valid_analyses),
        "files": valid_analyses,
    }


_RULE_CACHE = {}

def _match_rule_procedures(
    procedures: Dict[str, int],
    rule: OciProcedureRule,
) -> Dict[str, int]:
    matches: Dict[str, int] = {}
    rule_id = id(rule)
    cached = _RULE_CACHE.get(rule_id)
    if cached is None:
        code_set = set(rule.codes)
        prefix_list = tuple(_normalize_prefix(prefix) for prefix in rule.prefixes)
        _RULE_CACHE[rule_id] = (code_set, prefix_list)
    else:
        code_set, prefix_list = cached
        
    for proc_code, qty in (procedures or {}).items():
        if proc_code in code_set or (prefix_list and any(proc_code.startswith(prefix) for prefix in prefix_list)):
            matches[proc_code] = matches.get(proc_code, 0) + int(qty or 0)
    return dict(sorted(matches.items()))


def _format_rule_match(rule: OciProcedureRule, matches: Dict[str, int]) -> Dict[str, object]:
    return {
        "label": rule.label,
        "generic": rule.generic,
        "matched_codes": matches,
        "total_quantity": sum(matches.values()),
    }


def _summarize_matched_procedures(*rule_groups: Iterable[Dict[str, object]]) -> Dict[str, int]:
    matched_proc_totals: Dict[str, int] = {}
    for rule_group in rule_groups:
        for item in rule_group or []:
            for proc_code, qty in (item.get("matched_codes") or {}).items():
                matched_proc_totals[proc_code] = matched_proc_totals.get(proc_code, 0) + int(qty or 0)
    return dict(sorted(matched_proc_totals.items()))


@lru_cache(maxsize=4096)
def _match_context_values_cached(values: Tuple[str, ...], allowed_prefixes: Tuple[str, ...]) -> Tuple[str, ...]:
    normalized_values = {
        _normalize_text(value)
        for value in values
        if _normalize_text(value)
    }
    normalized_prefixes = tuple(
        prefix
        for prefix in (_normalize_text(item) for item in allowed_prefixes)
        if prefix
    )
    if not normalized_values or not normalized_prefixes:
        return ()
    return tuple(sorted(
        value
        for value in normalized_values
        if any(value.startswith(prefix) for prefix in normalized_prefixes)
    ))

def _match_context_values(values: Iterable[str], allowed_prefixes: Iterable[str]) -> List[str]:
    val_tuple = tuple(sorted(values or []))
    pref_tuple = tuple(sorted(allowed_prefixes or []))
    return list(_match_context_values_cached(val_tuple, pref_tuple))


@lru_cache(maxsize=4096)
def _match_cid_values_cached(values: Tuple[str, ...], allowed_codes: Tuple[str, ...]) -> Tuple[str, ...]:
    normalized_values = {
        _normalize_cid_code(value)
        for value in values
        if _normalize_cid_code(value)
    }
    normalized_allowed = tuple(
        code
        for code in (_normalize_cid_code(item) for item in allowed_codes)
        if code
    )
    if not normalized_values or not normalized_allowed:
        return ()

    def _cid_matches(candidate: str, allowed: str) -> bool:
        if len(allowed) <= 3:
            return candidate.startswith(allowed[:3])
        return candidate == allowed

    return tuple(sorted(
        value
        for value in normalized_values
        if any(_cid_matches(value, allowed) for allowed in normalized_allowed)
    ))

def _match_cid_values(values: Iterable[str], allowed_codes: Iterable[str]) -> List[str]:
    val_tuple = tuple(sorted(values or []))
    allowed_tuple = tuple(sorted(allowed_codes or []))
    return list(_match_cid_values_cached(val_tuple, allowed_tuple))


def _collect_combo_context_values(
    patient: Dict[str, object],
    matched_procedures: Dict[str, int],
    context_key: str,
) -> List[str]:
    procedure_contexts = patient.get("procedure_contexts") or {}
    values = set()
    for proc_code in (matched_procedures or {}).keys():
        context = procedure_contexts.get(_normalize_proc_code(proc_code)) or {}
        values.update(
            _normalize_text(value)
            for value in (context.get(context_key) or [])
            if _normalize_text(value)
        )
    return sorted(values)


def _evaluate_combo_context(
    patient: Dict[str, object],
    combo: OciComboRule,
    matched_procedures: Optional[Dict[str, int]] = None,
    skip_cid: bool = False,
) -> Dict[str, object]:
    
    # 1. Valida a Autorização do BPA (9 chars e não começa com '0' - após remover zeros à esquerda do padding)
    auth_ok = False
    for auth in patient.get("autorizacoes") or []:
        auth_str = str(auth).strip().lstrip("0")
        if len(auth_str) == 9:
            auth_ok = True
            break

    context_rule = OCI_CBO_CID_RULES.get(combo.combo_code)
    if not context_rule:
        return {
            "applied": False,
            "cbo_ok": True,
            "cid_ok": True,
            "auth_ok": auth_ok, # REGISTRA REGRA
            "matched_cbos": [],
            "matched_cids": [],
            "combo_cids_evaluated": [],
            "required_cbo_prefixes": [],
            "required_cid_prefixes": [],
            "source_combo_code": "",
            "source_combo_name": "",
        }

    matched_cbos = _match_context_values(patient.get("cbos") or [], context_rule.get("cbo_prefixes") or [])
    cbo_prefixes = context_rule.get("cbo_prefixes") or ()
    cid_prefixes = context_rule.get("cid_prefixes") or ()
    
    if skip_cid:
        candidate_cids = []
        matched_cids = []
    else:
        combo_cids = _collect_combo_context_values(patient, matched_procedures or {}, "cids")
        candidate_cids = combo_cids or sorted(patient.get("cids") or [])
        matched_cids = _match_cid_values(candidate_cids, cid_prefixes)
        
    return {
        "applied": True,
        "cbo_ok": bool(matched_cbos) if cbo_prefixes else True,
        "cid_ok": bool(matched_cids) if cid_prefixes else True,
        "auth_ok": auth_ok, # REGISTRA REGRA
        "matched_cbos": matched_cbos,
        "matched_cids": matched_cids,
        "combo_cids_evaluated": candidate_cids,
        "required_cbo_prefixes": list(cbo_prefixes),
        "required_cid_prefixes": list(cid_prefixes),
        "source_combo_code": context_rule.get("source_combo_code") or "",
        "source_combo_name": context_rule.get("source_combo_name") or "",
    }


def _parse_patient_date(value: str) -> Optional[datetime]:
    normalized = normalize_date(value)
    if len(normalized) != 8 or not normalized.isdigit():
        return None
    try:
        return datetime.strptime(normalized, "%Y%m%d")
    except ValueError:
        return None


def _resolve_patient_reference_date(patient: Dict[str, object]) -> Optional[datetime]:
    service_dates = sorted(
        value
        for value in (patient.get("service_dates") or [])
        if len(str(value)) == 8 and str(value).isdigit()
    )
    for service_date in service_dates:
        parsed = _parse_patient_date(service_date)
        if parsed:
            return parsed

    competencias = sorted(
        value
        for value in (patient.get("competencias") or [])
        if len(str(value)) == 6 and str(value).isdigit()
    )
    for competencia in competencias:
        try:
            return datetime.strptime(f"{competencia}01", "%Y%m%d")
        except ValueError:
            continue
    return None


def _calculate_age_years(birth_date: datetime, reference_date: datetime) -> Optional[int]:
    if reference_date < birth_date:
        return None
    age = reference_date.year - birth_date.year
    if (reference_date.month, reference_date.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


def _evaluate_combo_age(patient: Dict[str, object], combo: OciComboRule) -> Dict[str, object]:
    if combo.min_age_years is None and combo.max_age_years is None:
        return {
            "applied": False,
            "age_ok": True,
            "patient_age_years": None,
            "reference_date": "",
        }

    birth_date = _parse_patient_date(patient.get("dob") or "")
    reference_date = _resolve_patient_reference_date(patient)
    if not birth_date or not reference_date:
        return {
            "applied": True,
            "age_ok": False,
            "patient_age_years": None,
            "reference_date": "",
        }

    age_years = _calculate_age_years(birth_date, reference_date)
    if age_years is None:
        return {
            "applied": True,
            "age_ok": False,
            "patient_age_years": None,
            "reference_date": reference_date.strftime("%Y%m%d"),
        }

    if combo.min_age_years is not None and age_years < combo.min_age_years:
        return {
            "applied": True,
            "age_ok": False,
            "patient_age_years": age_years,
            "reference_date": reference_date.strftime("%Y%m%d"),
        }
    if combo.max_age_years is not None and age_years > combo.max_age_years:
        return {
            "applied": True,
            "age_ok": False,
            "patient_age_years": age_years,
            "reference_date": reference_date.strftime("%Y%m%d"),
        }

    return {
        "applied": True,
        "age_ok": True,
        "patient_age_years": age_years,
        "reference_date": reference_date.strftime("%Y%m%d"),
    }


_COMBO_INDEX_BUILT = False
_PROC_CODE_TO_COMBOS = {}
_PROC_PREFIX_TO_COMBOS = {}

def _build_combo_rules_index():
    global _COMBO_INDEX_BUILT, _PROC_CODE_TO_COMBOS, _PROC_PREFIX_TO_COMBOS
    if _COMBO_INDEX_BUILT:
        return
    for combo in OCI_COMBO_RULES:
        for rule in list(combo.required) + list(combo.optional):
            for code in rule.codes or []:
                _PROC_CODE_TO_COMBOS.setdefault(code, set()).add(combo)
            for prefix in rule.prefixes or []:
                norm_prefix = _normalize_prefix(prefix)
                if norm_prefix:
                    _PROC_PREFIX_TO_COMBOS.setdefault(norm_prefix, set()).add(combo)
    _COMBO_INDEX_BUILT = True

def _get_candidate_combos(procedures: Dict[str, int]) -> set:
    _build_combo_rules_index()
    candidates = set()
    for proc_code in procedures:
        if proc_code in _PROC_CODE_TO_COMBOS:
            candidates.update(_PROC_CODE_TO_COMBOS[proc_code])
        for prefix, combos in _PROC_PREFIX_TO_COMBOS.items():
            if proc_code.startswith(prefix):
                candidates.update(combos)
    return candidates


def _evaluate_oci_combos(merged_patients: Dict[Tuple[str, str], Dict[str, object]]) -> Dict[str, object]:
    combo_summary_map: Dict[str, Dict[str, object]] = {
        combo.combo_code: {
            "combo_code": combo.combo_code,
            "combo_name": combo.combo_name,
            "patients_count": 0,
            "required_rules": len(combo.required),
            "optional_rules": len(combo.optional),
            "notes": combo.notes,
        }
        for combo in OCI_COMBO_RULES
    }

    patient_details: List[Dict[str, object]] = []
    invalid_cid_combo_patients: List[Dict[str, object]] = []
    invalid_auth_combo_patients: List[Dict[str, object]] = []
    almost_combo_patients: List[Dict[str, object]] = []
    notes = sorted({combo.notes for combo in OCI_COMBO_RULES if combo.notes})

    for _, patient in sorted(merged_patients.items(), key=lambda item: (item[0][0], item[0][1])):
        procedures = patient.get("procedures") or {}
        
        candidate_combos = _get_candidate_combos(procedures)
        if not candidate_combos:
            continue

        formed_combos: List[Dict[str, object]] = []
        invalid_cid_combos: List[Dict[str, object]] = []
        invalid_auth_combos: List[Dict[str, object]] = []
        almost_combos: List[Dict[str, object]] = []

        ordered_candidates = [c for c in OCI_COMBO_RULES if c in candidate_combos]
        for combo in ordered_candidates:
            matched_required = []
            missing_required = []

            for required_rule in combo.required:
                matches = _match_rule_procedures(procedures, required_rule)
                if matches:
                    matched_required.append(_format_rule_match(required_rule, matches))
                else:
                    missing_required.append(required_rule.label)

            if missing_required:
                if matched_required:
                    matched_proc_totals = _summarize_matched_procedures(matched_required, [])
                    context_match = _evaluate_combo_context(patient, combo, matched_proc_totals, skip_cid=True)
                    almost_combos.append(
                        {
                            "combo_code": combo.combo_code,
                            "combo_name": combo.combo_name,
                            "matched_required": matched_required,
                            "missing_required": missing_required,
                            "matched_required_count": len(matched_required),
                            "required_count": len(combo.required),
                            "missing_count": len(missing_required),
                            "context_rules_applied": context_match["applied"],
                            "auth_ok": context_match["auth_ok"],
                            "matched_cbos": context_match["matched_cbos"],
                            "required_cbo_prefixes": context_match["required_cbo_prefixes"],
                            "context_source_combo_code": context_match["source_combo_code"],
                            "context_source_combo_name": context_match["source_combo_name"],
                            "notes": combo.notes,
                        }
                    )
                continue

            matched_optional = []
            for optional_rule in combo.optional:
                matches = _match_rule_procedures(procedures, optional_rule)
                if matches:
                    matched_optional.append(_format_rule_match(optional_rule, matches))

            matched_proc_totals = _summarize_matched_procedures(matched_required, matched_optional)
            context_match = _evaluate_combo_context(patient, combo, matched_proc_totals)
            age_match = _evaluate_combo_age(patient, combo)

            # Track combos that would close by procedure but fail specifically on CID validation.

            if context_match["cbo_ok"] and not context_match["cid_ok"] and context_match["auth_ok"] and age_match["age_ok"]:
                invalid_cid_combos.append(
                    {
                        "combo_code": combo.combo_code,
                        "combo_name": combo.combo_name,
                        "matched_required": matched_required,
                        "matched_optional": matched_optional,
                        "matched_procedures": matched_proc_totals,
                        "matched_procedure_details": _build_procedure_detail_list(matched_proc_totals),
                        "context_rules_applied": context_match["applied"],
                        "auth_ok": context_match["auth_ok"],
                        "matched_cbos": context_match["matched_cbos"],
                        "matched_cids": context_match["matched_cids"],
                        "combo_cids_evaluated": context_match["combo_cids_evaluated"],
                        "required_cid_prefixes": context_match["required_cid_prefixes"],
                        "required_cbo_prefixes": context_match["required_cbo_prefixes"],
                        "context_source_combo_code": context_match["source_combo_code"],
                        "context_source_combo_name": context_match["source_combo_name"],
                        "patient_cids": sorted(patient.get("cids") or []),
                        "patient_cid_sources": sorted(patient.get("cid_sources") or []),
                        "age_rule_applied": age_match["applied"],
                        "patient_age_years": age_match["patient_age_years"],
                        "age_reference_date": age_match["reference_date"],
                        "notes": combo.notes,
                    }
                )

            # Track combos that would close by procedure but fail specifically on Authorization validation.
            if context_match["cbo_ok"] and context_match["cid_ok"] and not context_match["auth_ok"] and age_match["age_ok"]:
                invalid_auth_combos.append(
                    {
                        "combo_code": combo.combo_code,
                        "combo_name": combo.combo_name,
                        "matched_required": matched_required,
                        "matched_optional": matched_optional,
                        "matched_procedures": matched_proc_totals,
                        "matched_procedure_details": _build_procedure_detail_list(matched_proc_totals),
                        "context_rules_applied": context_match["applied"],
                        "auth_ok": context_match["auth_ok"],
                        "matched_cbos": context_match["matched_cbos"],
                        "matched_cids": context_match["matched_cids"],
                        "combo_cids_evaluated": context_match["combo_cids_evaluated"],
                        "required_cid_prefixes": context_match["required_cid_prefixes"],
                        "required_cbo_prefixes": context_match["required_cbo_prefixes"],
                        "context_source_combo_code": context_match["source_combo_code"],
                        "context_source_combo_name": context_match["source_combo_name"],
                        "patient_cids": sorted(patient.get("cids") or []),
                        "patient_cid_sources": sorted(patient.get("cid_sources") or []),
                        "age_rule_applied": age_match["applied"],
                        "patient_age_years": age_match["patient_age_years"],
                        "age_reference_date": age_match["reference_date"],
                        "notes": combo.notes,
                    }
                )

            if not (context_match["cbo_ok"] and context_match["cid_ok"] and context_match["auth_ok"]):
                continue

            if not age_match["age_ok"]:
                continue

            formed_combo = {
                "combo_code": combo.combo_code,
                "combo_name": combo.combo_name,
                "matched_required": matched_required,
                "matched_optional": matched_optional,
                "matched_procedures": dict(sorted(matched_proc_totals.items())),
                "matched_procedure_details": _build_procedure_detail_list(matched_proc_totals),
                "context_rules_applied": context_match["applied"],
                "auth_ok": context_match["auth_ok"],
                "matched_cbos": context_match["matched_cbos"],
                "matched_cids": context_match["matched_cids"],
                "combo_cids_evaluated": context_match["combo_cids_evaluated"],
                "required_cbo_prefixes": context_match["required_cbo_prefixes"],
                "required_cid_prefixes": context_match["required_cid_prefixes"],
                "patient_cid_sources": sorted(patient.get("cid_sources") or []),
                "context_source_combo_code": context_match["source_combo_code"],
                "context_source_combo_name": context_match["source_combo_name"],
                "age_rule_applied": age_match["applied"],
                "patient_age_years": age_match["patient_age_years"],
                "age_reference_date": age_match["reference_date"],
                "notes": combo.notes,
            }
            formed_combos.append(formed_combo)

            combo_bucket = combo_summary_map[combo.combo_code]
            combo_bucket["patients_count"] += 1

        if formed_combos:
            patient_details.append(
                {
                    "name": patient["name"],
                    "dob": patient["dob"],
                    "cpf": patient.get("cpf") or "",
                    "cns": patient.get("cns") or "",
                    "sources": sorted(patient.get("sources") or []),
                    "source_origins": {
                        source_key: sorted(source_files or [])
                        for source_key, source_files in sorted((patient.get("source_origins") or {}).items())
                    },
                    "cbos": sorted(patient.get("cbos") or []),
                    "cids": sorted(patient.get("cids") or []),
                    "autorizacoes": sorted(patient.get("autorizacoes") or []),
                    "cid_sources": sorted(patient.get("cid_sources") or []),
                    "service_dates": sorted(patient.get("service_dates") or []),
                    "competencias": sorted(patient.get("competencias") or []),
                    "apac_numbers": sorted(patient.get("apac_numbers") or []),
                    "procedures": dict(sorted(procedures.items())),
                    "formed_combos": formed_combos,
                    "formed_combo_count": len(formed_combos),
                }
            )

        if invalid_cid_combos:
            invalid_cid_combo_patients.append(
                {
                    "name": patient["name"],
                    "dob": patient["dob"],
                    "cpf": patient.get("cpf") or "",
                    "cns": patient.get("cns") or "",
                    "sources": sorted(patient.get("sources") or []),
                    "source_origins": {
                        source_key: sorted(source_files or [])
                        for source_key, source_files in sorted((patient.get("source_origins") or {}).items())
                    },
                    "cbos": sorted(patient.get("cbos") or []),
                    "cids": sorted(patient.get("cids") or []),
                    "cid_sources": sorted(patient.get("cid_sources") or []),
                    "service_dates": sorted(patient.get("service_dates") or []),
                    "competencias": sorted(patient.get("competencias") or []),
                    "apac_numbers": sorted(patient.get("apac_numbers") or []),
                    "autorizacoes": sorted(patient.get("autorizacoes") or []),
                    "procedures": dict(sorted(procedures.items())),
                    "invalid_cid_combos": invalid_cid_combos,
                    "invalid_cid_combo_count": len(invalid_cid_combos),
                }
            )

        if invalid_auth_combos:
            invalid_auth_combo_patients.append(
                {
                    "name": patient["name"],
                    "dob": patient["dob"],
                    "cpf": patient.get("cpf") or "",
                    "cns": patient.get("cns") or "",
                    "sources": sorted(patient.get("sources") or []),
                    "source_origins": {
                        source_key: sorted(source_files or [])
                        for source_key, source_files in sorted((patient.get("source_origins") or {}).items())
                    },
                    "cbos": sorted(patient.get("cbos") or []),
                    "cids": sorted(patient.get("cids") or []),
                    "cid_sources": sorted(patient.get("cid_sources") or []),
                    "service_dates": sorted(patient.get("service_dates") or []),
                    "competencias": sorted(patient.get("competencias") or []),
                    "apac_numbers": sorted(patient.get("apac_numbers") or []),
                    "autorizacoes": sorted(patient.get("autorizacoes") or []),
                    "procedures": dict(sorted(procedures.items())),
                    "invalid_auth_combos": invalid_auth_combos,
                    "invalid_auth_combo_count": len(invalid_auth_combos),
                }
            )

        if almost_combos:
            almost_combos.sort(key=lambda item: (item["missing_count"], -item["matched_required_count"], item["combo_code"]))
            almost_combo_patients.append(
                {
                    "name": patient["name"],
                    "dob": patient["dob"],
                    "cpf": patient.get("cpf") or "",
                    "cns": patient.get("cns") or "",
                    "sources": sorted(patient.get("sources") or []),
                    "apac_numbers": sorted(patient.get("apac_numbers") or []),
                    "procedures": dict(sorted(procedures.items())),
                    "almost_combos": almost_combos,
                    "almost_combo_count": len(almost_combos),
                }
            )

    combo_summary = [
        combo
        for combo in combo_summary_map.values()
        if combo["patients_count"] > 0
    ]
    combo_summary.sort(key=lambda item: (-item["patients_count"], item["combo_code"]))

    summary = {
        "total_patients_analyzed": len(merged_patients),
        "patients_with_combos": len(patient_details),
        "patients_with_invalid_cid_combos": len(invalid_cid_combo_patients),
        "patients_with_invalid_auth_combos": len(invalid_auth_combo_patients),
        "patients_almost_with_combos": len(almost_combo_patients),
        "combo_occurrences": sum(item["formed_combo_count"] for item in patient_details),
        "invalid_cid_combo_occurrences": sum(item["invalid_cid_combo_count"] for item in invalid_cid_combo_patients),
        "invalid_auth_combo_occurrences": sum(item["invalid_auth_combo_count"] for item in invalid_auth_combo_patients),
        "almost_combo_occurrences": sum(item["almost_combo_count"] for item in almost_combo_patients),
        "combo_types_identified": len(combo_summary),
        "rules_catalog_size": len(OCI_COMBO_RULES),
        "notes": notes,
    }

    return {
        "summary": summary,
        "combo_summary": combo_summary,
        "patient_details": patient_details,
        "invalid_cid_combo_patients": invalid_cid_combo_patients,
        "invalid_auth_combo_patients": invalid_auth_combo_patients,
        "almost_combo_patients": almost_combo_patients,
    }


def _outputs_dir() -> str:
    from django.conf import settings

    output_dir = os.path.join(settings.MEDIA_ROOT, "bpa_apac_outputs")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def _history_output_path(history_id: int, file_name: str) -> str:
    safe_name = os.path.basename(file_name or f"bpa_tratado_{history_id}.txt")
    return os.path.join(_outputs_dir(), f"{history_id}__{safe_name}")


def _display_user_name(user) -> str:
    if not user:
        return "Nao informado"

    full_name = f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip()
    if full_name:
        return full_name

    username = (getattr(user, "username", "") or "").strip()
    if username:
        return username

    email = (getattr(user, "email", "") or "").strip()
    if email:
        return email

    return "Nao informado"


def _load_history_details(history_id: int) -> Dict[str, object]:
    raw_details = load_bpa_details(history_id)
    return _enrich_bpa_history_details(raw_details)


def _load_history_details_raw(history_id: int) -> Dict[str, object]:
    return load_bpa_details(history_id)


def _load_oci_history_details(history_id: int) -> Dict[str, object]:
    return load_oci_details(history_id)


def _hydrate_procedure_details(
    detail_list: object,
    procedure_map: Optional[Dict[str, int]] = None,
) -> List[Dict[str, object]]:
    if isinstance(detail_list, list) and detail_list:
        code_qty_map: Dict[str, int] = {}
        for item in detail_list:
            if not isinstance(item, dict):
                continue
            code = _normalize_proc_code(item.get("code"))
            if not code:
                continue
            code_qty_map[code] = int(item.get("qty") or 0)
        hydrated = _build_procedure_detail_list(code_qty_map)
        if hydrated:
            return hydrated

    if procedure_map:
        normalized_map = {
            _normalize_proc_code(code): int(qty or 0)
            for code, qty in (procedure_map or {}).items()
            if _normalize_proc_code(code)
        }
        return _build_procedure_detail_list(normalized_map)

    return []


def _enrich_bpa_history_details(details: Dict[str, object]) -> Dict[str, object]:
    if not isinstance(details, dict):
        return {}

    for patient in details.get("not_found_patients") or []:
        if not isinstance(patient, dict):
            continue
        patient["procedure_details"] = _hydrate_procedure_details(
            patient.get("procedure_details"),
            patient.get("procedures"),
        )

    for patient in details.get("procs_not_found_patients") or []:
        if not isinstance(patient, dict):
            continue
        patient["leftover_details"] = _hydrate_procedure_details(
            patient.get("leftover_details"),
            patient.get("leftovers"),
        )

    for combo in details.get("oci_combo_details") or []:
        if not isinstance(combo, dict):
            continue
        combo["principal_proc_name"] = _get_procedure_name(combo.get("principal_proc")) or str(combo.get("principal_proc_name") or "").strip()
        combo["procedure_details"] = _hydrate_procedure_details(
            combo.get("procedure_details"),
            combo.get("procedures"),
        )
        combo["removed_procedure_details"] = _hydrate_procedure_details(
            combo.get("removed_procedure_details"),
            combo.get("removed_procedures"),
        )
        combo["remaining_procedure_details"] = _hydrate_procedure_details(
            combo.get("remaining_procedure_details"),
            combo.get("remaining_procedures"),
        )

    return details


OCI_HISTORY_PERIODS = {
    "7d": 7,
    "30d": 30,
    "90d": 90,
    "180d": 180,
    "365d": 365,
}


def _resolve_history_period(period: str) -> Tuple[str, Optional[datetime]]:
    normalized = _normalize_text(period).lower() or "30d"
    if normalized == "all":
        return "all", None
    days = OCI_HISTORY_PERIODS.get(normalized, 30)
    return normalized, timezone.now() - timedelta(days=days)

def is_similar(name1, name2, threshold=0.85):
    if not name1 or not name2:
        return False
    if name1 == name2:
        return True
    return SequenceMatcher(None, name1, name2).ratio() >= threshold

def normalize_cpf(cpf: str) -> str:
    if not cpf:
        return ""
    cleaned = re.sub(r"\D", "", str(cpf))
    if 0 < len(cleaned) < 11:
        cleaned = cleaned.zfill(11)
    if len(cleaned) == 11:
        return cleaned
    return ""

def normalize_name(name):
    if pd.isna(name):
        return ""
    normalized = unicodedata.normalize("NFKD", str(name).strip().upper())
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
    compact_name = re.sub(r"[^A-Z0-9 ]+", " ", ascii_name)
    return re.sub(r"\s+", " ", compact_name).strip()

def normalize_date(date_val):
    if pd.isna(date_val):
        return ""
    if isinstance(date_val, datetime):
        return date_val.strftime('%Y%m%d')
    raw_value = str(date_val).strip()
    if not raw_value:
        return ""

    digits_only = "".join(ch for ch in raw_value if ch.isdigit())
    if len(digits_only) == 8:
        for date_format in ("%Y%m%d", "%d%m%Y"):
            try:
                return datetime.strptime(digits_only, date_format).strftime("%Y%m%d")
            except ValueError:
                continue

    for date_format in (
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
    ):
        try:
            return datetime.strptime(raw_value, date_format).strftime("%Y%m%d")
        except ValueError:
            continue

    parsed = pd.to_datetime(raw_value, errors="coerce", dayfirst=True)
    if pd.notna(parsed):
        return parsed.strftime("%Y%m%d")

    parsed = pd.to_datetime(raw_value, errors="coerce", dayfirst=False)
    if pd.notna(parsed):
        return parsed.strftime("%Y%m%d")

    return raw_value


def _normalize_document_digits(value, expected_length: int) -> str:
    if value is None:
        return ""

    if isinstance(value, str):
        raw_value = value.strip()
    else:
        raw_value = str(value).strip()

    if not raw_value:
        return ""

    digits = "".join(ch for ch in raw_value if ch.isdigit())
    if len(digits) == expected_length:
        return digits

    # Excel may serialize long numeric identifiers in scientific notation.
    if any(marker in raw_value.lower() for marker in ("e+", "e-", ".")):
        try:
            decimal_value = Decimal(raw_value)
            if decimal_value == decimal_value.to_integral_value():
                normalized = format(decimal_value.quantize(Decimal("1")), "f").replace(".", "").replace("-", "")
                normalized_digits = "".join(ch for ch in normalized if ch.isdigit())
                if len(normalized_digits) == expected_length:
                    return normalized_digits
        except (InvalidOperation, ValueError):
            return ""

    return ""


def normalize_cpf(value):
    return _normalize_document_digits(value, 11)


def normalize_cns(value):
    return _normalize_document_digits(value, 15)


# DATASUS Layouts
BPA_HEADER_LAYOUT = [
    ("ident", "num", 2),
    ("tag", "txt", 5),
    ("competencia", "num", 6),
    ("num_linhas", "num", 6),
    ("num_folhas", "num", 6),
    ("controle", "num", 7),
    ("orgao_nome", "txt", 30),
    ("orgao_sigla", "txt", 6),
    ("cnpj_cpf_prestador", "num", 14),
    ("destino_nome", "txt", 40),
    ("destino_tipo", "txt", 1),
    ("versao", "txt", 10),
]

BPA_C_LAYOUT = [
    ("ident", "num", 2),
    ("cnes", "num", 7),
    ("competencia", "num", 6),
    ("cbo", "txt", 6),
    ("folha", "num", 3),
    ("sequencial", "num", 2),
    ("procedimento", "num", 10),
    ("idade", "num", 3),
    ("quantidade", "num", 6),
    ("origem", "txt", 3),
]

BPA_I_LAYOUT = [
    ("ident", "num", 2),
    ("cnes", "num", 7),
    ("competencia", "num", 6),
    ("cns_prof", "num", 15),
    ("cbo", "txt", 6),
    ("data_atend", "num", 8),
    ("folha", "num", 3),
    ("sequencial", "num", 2),
    ("procedimento", "num", 10),
    ("cns_paciente", "num", 15),
    ("sexo", "txt", 1),
    ("mun_ibge", "num", 6),
    ("cid10", "txt", 4),
    ("idade", "num", 3),
    ("quantidade", "num", 6),
    ("carater_atend", "num", 2),
    ("n_autorizacao", "num", 13),
    ("origem", "txt", 3),
    ("nome_paciente", "txt", 30),
    ("data_nasc", "num", 8),
    ("raca", "num", 2),
    ("etnia", "num", 4),
    ("nacionalidade", "num", 3),
    ("servico", "num", 3),
    ("classificacao", "num", 3),
    ("equipe_seq", "num", 8),
    ("equipe_area", "num", 4),
    ("cnpj", "num", 14),
    ("cep", "num", 8),
    ("tipo_logradouro", "num", 3),
    ("logradouro", "txt", 30),
    ("complemento", "txt", 10),
    ("numero", "txt", 5),
    ("bairro", "txt", 30),
    ("telefone", "num", 11),
    ("email", "txt", 40),
    ("ine", "num", 10),
    ("cpf_paciente", "num", 11),
    ("situacao_rua", "txt", 1),
    ("sem_cpf", "txt", 1),
]

BPA_I_EXCEL_ALIASES = {
    "ident": ["ident"],
    "cnes": ["cnes"],
    "competencia": ["competencia"],
    "cns_prof": ["cns_prof", "cns-prof", "cnsprof"],
    "cbo": ["cbo"],
    "data_atend": ["data_atend", "data-atend", "dataatend"],
    "folha": ["folha"],
    "sequencial": ["sequencial", "sequencia", "seq"],
    "procedimento": ["procedimento", "prd-pa", "prd_pa"],
    "cns_paciente": ["cns_paciente", "cns-paciente", "cns paciente", "prd-cns", "prd_cns", "cns_pac", "cns do paciente"],
    "sexo": ["sexo"],
    "mun_ibge": ["mun_ibge", "mun-ibge", "municipio_ibge", "ibge"],
    "cid10": ["cid10", "cid"],
    "idade": ["idade"],
    "quantidade": ["quantidade", "prd-qt", "prd_qt", "qtd"],
    "carater_atend": ["carater_atend", "carater-atend", "carater"],
    "n_autorizacao": ["n_autorizacao", "n-autorizacao", "autorizacao"],
    "origem": ["origem"],
    "nome_paciente": ["nome_paciente", "nome-paciente", "prd-nmpac", "prd_nmpac"],
    "data_nasc": ["data_nasc", "data-nasc", "prd-dtnasc", "prd_dtnasc"],
    "raca": ["raca"],
    "etnia": ["etnia"],
    "nacionalidade": ["nacionalidade"],
    "servico": ["servico"],
    "classificacao": ["classificacao"],
    "equipe_seq": ["equipe_seq", "equipe-seq"],
    "equipe_area": ["equipe_area", "equipe-area"],
    "cnpj": ["cnpj"],
    "cep": ["cep"],
    "tipo_logradouro": ["tipo_logradouro", "tipo-logradouro"],
    "logradouro": ["logradouro"],
    "complemento": ["complemento"],
    "numero": ["numero"],
    "bairro": ["bairro"],
    "telefone": ["telefone"],
    "email": ["email"],
    "ine": ["ine"],
    "cpf_paciente": [
        "cpf_paciente",
        "cpf-paciente",
        "cpf paciente",
        "cpf",
        "prd-cpf",
        "prd_cpf",
        "prd-cpf-pcnte",
        "prd_cpf_pcnte",
        "cpf do paciente",
    ],
    "situacao_rua": ["situacao_rua", "situacao-rua", "prd-situacao-rua", "prd_situacao_rua"],
    "sem_cpf": ["sem_cpf", "sem-cpf", "prd-sem-cpf", "prd_sem_cpf"],
    "nome_profissional": ["nome_profissional", "nome-profissional", "nome_prof"],
}


def _register_oci_patient_candidate(
    oci_by_dob: Dict[str, List[Dict[str, object]]],
    oci_by_cpf: Dict[str, set],
    oci_by_cns: Dict[str, set],
    oci_patient_registry: Dict[Tuple[str, str], Dict[str, object]],
    name: str,
    dob: str,
    apac_num: str = "",
    principal_proc: str = "",
    cpf: str = "",
    cns: str = "",
) -> Optional[Tuple[str, str]]:
    if not name or not dob:
        return None

    patient_key = (name, dob)
    patient_meta = oci_patient_registry.get(patient_key)
    if not patient_meta:
        patient_meta = {
            "name": name,
            "dob": dob,
            "apac_num": apac_num,
            "principal_proc": principal_proc,
            "cpf": cpf,
            "cns": cns,
            "found": False,
            "match_criterion": "",
        }
        oci_patient_registry[patient_key] = patient_meta
        oci_by_dob.setdefault(dob, []).append(patient_meta)
    else:
        if apac_num and not patient_meta.get("apac_num"):
            patient_meta["apac_num"] = apac_num
        if principal_proc and not patient_meta.get("principal_proc"):
            patient_meta["principal_proc"] = principal_proc
        if cpf and not patient_meta.get("cpf"):
            patient_meta["cpf"] = cpf
        if cns and not patient_meta.get("cns"):
            patient_meta["cns"] = cns

    if patient_meta.get("cpf"):
        oci_by_cpf.setdefault(patient_meta["cpf"], set()).add(patient_key)
    if patient_meta.get("cns"):
        oci_by_cns.setdefault(patient_meta["cns"], set()).add(patient_key)

    return patient_key


def _pick_unique_patient_key(candidates, name: str, dob: str):
    candidate_list = list(candidates or [])
    if not candidate_list:
        return None
    if len(candidate_list) == 1:
        return candidate_list[0]

    filtered = [key for key in candidate_list if key[1] == dob and is_similar(name, key[0])]
    if len(filtered) == 1:
        return filtered[0]
    return None


def _resolve_oci_patient_match(
    name: str,
    dob: str,
    cpf: str,
    cns: str,
    oci_by_dob: Dict[str, List[Dict[str, object]]],
    oci_by_cpf: Dict[str, set],
    oci_by_cns: Dict[str, set],
):
    normalized_name = normalize_name(name)
    normalized_dob = normalize_date(dob)
    normalized_cpf = normalize_cpf(cpf)
    normalized_cns = normalize_cns(cns)

    cpf_match = _pick_unique_patient_key(oci_by_cpf.get(normalized_cpf), normalized_name, normalized_dob) if normalized_cpf else None
    if cpf_match:
        return cpf_match, "cpf"

    cns_match = _pick_unique_patient_key(oci_by_cns.get(normalized_cns), normalized_name, normalized_dob) if normalized_cns else None
    if cns_match:
        return cns_match, "cns"

    if normalized_dob in oci_by_dob:
        for patient_meta in oci_by_dob[normalized_dob]:
            if is_similar(normalized_name, patient_meta["name"]):
                return (patient_meta["name"], normalized_dob), "name_dob"

    return None, ""

APAC_CORPO_LAYOUT = [
    ("ident", "num", 2),
    ("competencia", "num", 6),
    ("numero_apac", "num", 13),
    ("cod_uf", "num", 2),
    ("cnes", "txt", 7),
    ("data_proc", "num", 8),
    ("dt_ini_val", "num", 8),
    ("dt_fim_val", "num", 8),
    ("tipo_atend", "num", 2),
    ("tipo_apac", "num", 1),
    ("nome_paciente", "txt", 30),
    ("nome_mae", "txt", 30),
    ("logradouro", "txt", 30),
    ("numero_res", "txt", 5),
    ("complemento", "txt", 10),
    ("cep", "num", 8),
    ("mun_ibge", "num", 7),
    ("data_nasc", "num", 8),
    ("sexo", "txt", 1),
    ("nome_medico", "txt", 30),
    ("cod_proc_princ", "num", 10),
    ("motivo_saida", "num", 2),
    ("dt_obito_alta", "num", 8),
    ("nome_autorizador", "txt", 30),
    ("cns_paciente", "num", 15),
    ("cns_medico", "num", 15),
    ("cns_autorizador", "num", 15),
    ("cid_associado", "txt", 4),
    ("num_prontuario", "txt", 10),
    ("cnes_solicitante", "txt", 7),
    ("data_solicitacao", "num", 8),
    ("data_autorizacao", "num", 8),
    ("cod_emissor", "txt", 10),
    ("carater_atend", "num", 2),
    ("apac_anterior", "num", 13),
    ("raca", "num", 2),
    ("nome_responsavel", "txt", 30),
    ("nacionalidade", "num", 3),
    ("etnia", "txt", 4),
    ("cod_logradouro", "num", 3),
    ("bairro", "txt", 30),
    ("ddd", "num", 2),
    ("telefone", "num", 9),
    ("email", "txt", 40),
    ("cns_executante", "num", 15),
    ("cpf_paciente", "num", 11),
    ("ine", "num", 10),
    ("situacao_rua", "txt", 1),
    ("fonte_orcam", "num", 2),
    ("emendas_parl", "txt", 1),
]

APAC_PROC_LAYOUT = [
    ("ident", "num", 2),
    ("competencia", "num", 6),
    ("numero_apac", "num", 13),
    ("cod_proc", "num", 10),
    ("cbo", "txt", 6),
    ("quantidade", "num", 7),
    ("cnpj", "txt", 14),
    ("nota_fiscal", "num", 6),
    ("cid_principal", "txt", 4),
    ("cid_secundario", "txt", 4),
    ("cod_servico", "num", 3),
    ("cod_classif", "num", 3),
    ("equipe_seq", "txt", 8),
    ("equipe_area", "txt", 4),
    ("cnes_terceiro", "txt", 7),
]

_LAYOUT_SLICES_CACHE = {}

def _get_layout_slices(layout: List[Tuple[str, str, int]]) -> List[Tuple[str, int, int, bool]]:
    layout_id = id(layout)
    slices = _LAYOUT_SLICES_CACHE.get(layout_id)
    if slices is None:
        slices = []
        pos = 0
        for name, kind, width in layout:
            slices.append((name, pos, pos + width, kind == "num"))
            pos += width
        _LAYOUT_SLICES_CACHE[layout_id] = slices
    return slices


def _get_layout_slice_map(layout: List[Tuple[str, str, int]]) -> Dict[str, Tuple[int, int, bool]]:
    return {name: (start, end, is_num) for name, start, end, is_num in _get_layout_slices(layout)}


def _parse_selected_fixed_width_fields(
    line: str,
    layout: List[Tuple[str, str, int]],
    field_names: Iterable[str],
) -> Dict[str, str]:
    selected_fields = set(field_names or [])
    values: Dict[str, str] = {}
    for name, start, end, is_num in _get_layout_slices(layout):
        if name not in selected_fields:
            continue
        chunk = line[start:end]
        values[name] = chunk.strip() if is_num else chunk.rstrip()
    return values


def parse_fixed_width(line: str, layout: List[Tuple[str, str, int]]) -> Dict[str, str]:
    slices = _get_layout_slices(layout)

    out: Dict[str, str] = {}
    for name, start, end, is_num in slices:
        chunk = line[start:end]
        if is_num:
            out[name] = chunk.strip()
        else:
            out[name] = chunk.rstrip()
    return out


_PARSED_FILE_CACHE = {}

def _get_parsed_fixed_width_records(file_bytes: bytes, layout: List[Tuple[str, str, int]], record_prefix: str) -> List[Dict[str, str]]:
    import hashlib
    global _PARSED_FILE_CACHE
    if len(_PARSED_FILE_CACHE) > 20:
        _PARSED_FILE_CACHE.clear()
        
    file_hash = hashlib.md5(file_bytes).hexdigest()
    cache_key = (file_hash, id(layout), record_prefix)
    if cache_key in _PARSED_FILE_CACHE:
        return _PARSED_FILE_CACHE[cache_key]
        
    records = []
    lines = file_bytes.decode("iso-8859-1").splitlines()
    for line in lines:
        if line.startswith(record_prefix):
            records.append(parse_fixed_width(line, layout))
            
    _PARSED_FILE_CACHE[cache_key] = records
    return records


def normalize_header_name(name: str) -> str:
    normalized = str(name or "").strip().lower().replace("_", "-")
    normalized = re.sub(r"\s+", "-", normalized)
    normalized = re.sub(r"-{2,}", "-", normalized)
    return normalized.strip("-")


def format_fixed_width_record(
    record: Dict[str, str],
    layout: List[Tuple[str, str, int]],
    numeric_fields_as_spaces: Optional[Iterable[str]] = None,
) -> str:
    numeric_fields_as_spaces = set(numeric_fields_as_spaces or [])
    parts: List[str] = []

    for field_name, kind, width in layout:
        raw_value = "" if record.get(field_name) is None else str(record.get(field_name))
        raw_value = raw_value.strip()

        if kind == "num":
            digits = "".join(ch for ch in raw_value if ch.isdigit())
            if not digits and field_name in numeric_fields_as_spaces:
                parts.append(" " * width)
            else:
                parts.append(digits.rjust(width, "0")[-width:])
        else:
            parts.append(raw_value[:width].ljust(width, " "))

    return "".join(parts)


BPA_I_NUMERIC_FIELDS_AS_SPACES = frozenset(
    {"servico", "classificacao", "equipe_seq", "equipe_area", "cnpj", "ine", "etnia", "cns_paciente", "cpf_paciente"}
)


def _normalize_bpa_etnia(value: str) -> str:
    raw = str(value or "").strip()
    digits = "".join(ch for ch in raw if ch.isdigit())
    if not digits or int(digits) == 0:
        return ""
    return digits


def _normalize_bpa_cns_paciente(value: str) -> str:
    digits = "".join(ch for ch in str(value or "") if ch.isdigit())
    if not digits or int(digits) == 0:
        return ""
    return digits


def _normalize_bpa_cpf_paciente(value: str) -> str:
    digits = "".join(ch for ch in str(value or "") if ch.isdigit())
    if not digits or int(digits) == 0:
        return ""
    return digits[-11:]


def _normalize_bpa_flag(value: str, default: str = "") -> str:
    raw = str(value or "").strip().upper()
    if not raw:
        return default
    return raw[0]


def _recover_bpa_cpf_from_legacy_professional_field(record: Dict[str, str]) -> None:
    leftover = str(record.get("nome_profissional") or "").strip()
    if not leftover:
        return
    leftover_digits = "".join(ch for ch in leftover if ch.isdigit())
    leftover_flags = "".join(ch for ch in leftover if ch.isalpha())
    if leftover_digits and not record.get("cpf_paciente"):
        record["cpf_paciente"] = leftover_digits[-11:]
    if leftover_flags and not str(record.get("situacao_rua") or "").strip():
        record["situacao_rua"] = leftover_flags[0]
    if len(leftover_flags) > 1 and not str(record.get("sem_cpf") or "").strip():
        record["sem_cpf"] = leftover_flags[1]


def _prepare_bpa_i_record(record: Dict[str, str]) -> Dict[str, str]:
    prepared = dict(record)
    _recover_bpa_cpf_from_legacy_professional_field(prepared)
    prepared["etnia"] = _normalize_bpa_etnia(prepared.get("etnia", ""))
    prepared["cns_paciente"] = _normalize_bpa_cns_paciente(prepared.get("cns_paciente", ""))
    prepared["cpf_paciente"] = _normalize_bpa_cpf_paciente(prepared.get("cpf_paciente", ""))
    prepared["situacao_rua"] = _normalize_bpa_flag(prepared.get("situacao_rua", ""))
    prepared["sem_cpf"] = _normalize_bpa_flag(prepared.get("sem_cpf", ""))
    return prepared


def format_bpa_i_record(record: Dict[str, str]) -> str:
    return format_fixed_width_record(
        _prepare_bpa_i_record(record),
        BPA_I_LAYOUT,
        numeric_fields_as_spaces=BPA_I_NUMERIC_FIELDS_AS_SPACES,
    )


def build_bpa_header_record(records: List[Dict[str, str]]) -> Dict[str, str]:
    competencia = ""
    cnpj_prestador = ""
    if records:
        competencia = records[0].get("competencia", "")
        cnpj_prestador = records[0].get("cnpj", "")

    num_linhas = len(records)
    num_folhas = max(1, ((num_linhas - 1) // 99) + 1) if num_linhas else 1

    return {
        "ident": "01",
        "tag": "BPA",
        "competencia": competencia or datetime.now().strftime("%Y%m"),
        "num_linhas": str(num_linhas),
        "num_folhas": str(num_folhas),
        "controle": "0",
        "orgao_nome": "ARQUIVO GERADO PELO SISTEMA",
        "orgao_sigla": "CCDTI",
        "cnpj_cpf_prestador": cnpj_prestador,
        "destino_nome": "SMS RIO",
        "destino_tipo": "M",
        "versao": "1.0",
    }


def build_bpa_i_record_from_excel_row(row_data: Dict[str, str], output_index: int) -> Dict[str, str]:
    normalized_row = {normalize_header_name(key): "" if value is None else str(value).strip() for key, value in row_data.items()}

    def get_value(field_name: str) -> str:
        for alias in BPA_I_EXCEL_ALIASES.get(field_name, [field_name]):
            value = normalized_row.get(normalize_header_name(alias), "")
            if value != "":
                return value
        return ""

    folha = str(((output_index - 1) // 99) + 1)
    sequencial = str(((output_index - 1) % 99) + 1)

    record = {field_name: get_value(field_name) for field_name, _, _ in BPA_I_LAYOUT}
    record.update(
        {
            "ident": record.get("ident") or "03",
            "folha": record.get("folha") or folha,
            "sequencial": record.get("sequencial") or sequencial,
            "origem": record.get("origem") or "BPA",
            "carater_atend": record.get("carater_atend") or "01",
            "nacionalidade": record.get("nacionalidade") or "010",
            "quantidade": record.get("quantidade") or "1",
            "situacao_rua": record.get("situacao_rua") or "N",
            "sem_cpf": record.get("sem_cpf") or "N",
        }
    )
    return record


def _strip_row_meta(row_data: Dict[str, object]) -> Dict[str, str]:
    return {
        str(key): "" if value is None else str(value)
        for key, value in row_data.items()
        if not str(key).startswith("_")
    }


def _apply_removed_quantity(row_data: Dict[str, object], removed_qty: int, qtd_header: str = "") -> Dict[str, str]:
    export_row = _strip_row_meta(row_data)
    qty_value = max(int(removed_qty or 0), 1)
    qty_str = str(qty_value).zfill(6)

    if qtd_header:
        export_row[qtd_header] = qty_str
        return export_row

    if "quantidade" in export_row:
        export_row["quantidade"] = qty_str
        return export_row

    for key in export_row.keys():
        if normalize_header_name(key) in {
            normalize_header_name("prd-qt"),
            normalize_header_name("prd_qt"),
            normalize_header_name("qtd"),
        }:
            export_row[key] = qty_str
            break
    return export_row


def _build_removed_only_bpa_lines(
    affected_rows: List[Dict[str, object]],
    qtd_header: str = "",
) -> List[str]:
    export_rows: List[Dict[str, str]] = []
    for row in affected_rows:
        status = row.get("_status")
        if status not in {"removed", "altered"}:
            continue
        removed_qty = row.get("_removed_qty")
        if removed_qty is None:
            if status == "removed":
                removed_qty = 1
            else:
                continue
        try:
            removed_qty_int = int(removed_qty)
        except (TypeError, ValueError):
            removed_qty_int = 1
        if removed_qty_int <= 0:
            continue
        export_rows.append(_apply_removed_quantity(row, removed_qty_int, qtd_header=qtd_header))

    if not export_rows:
        return []

    first = export_rows[0]
    if "procedimento" in first or "nome_paciente" in first:
        output_records = export_rows
    else:
        output_records = [
            build_bpa_i_record_from_excel_row(row, output_index)
            for output_index, row in enumerate(export_rows, start=1)
        ]

    header_record = build_bpa_header_record(output_records)
    output_lines = [format_fixed_width_record(header_record, BPA_HEADER_LAYOUT)]
    output_lines.extend(format_bpa_i_record(record) for record in output_records)
    return output_lines


def _build_removed_only_filename(base_filename: str) -> str:
    name, ext = os.path.splitext(base_filename)
    ext = ext or ".txt"
    if "_tratado_oci" in name:
        return f"{name.replace('_tratado_oci', '_removidos_oci')}{ext}"
    if name.endswith("_tratado"):
        return f"{name[:-len('_tratado')]}_removidos{ext}"
    return f"{name}_removidos{ext}"


def _register_removed_only_bpa_file(
    request,
    affected_rows: List[Dict[str, object]],
    treated_filename: str,
    unit_cnes: str = "",
    qtd_header: str = "",
) -> Optional[Dict[str, str]]:
    output_lines = _build_removed_only_bpa_lines(affected_rows, qtd_header=qtd_header)
    if not output_lines:
        return None

    file_id = str(uuid.uuid4())
    path = os.path.join(tempfile.gettempdir(), file_id)
    with open(path, "w", encoding="iso-8859-1", newline="") as handle:
        for out_line in output_lines:
            handle.write(out_line + "\r\n")

    removed_filename = _build_removed_only_filename(treated_filename)
    _register_temp_download_access(request, file_id, removed_filename, unit_cnes)
    return {
        "file_id": file_id,
        "file_name": removed_filename,
        "path": path,
    }


def _select_oci_treated_bpa_source(
    sources: List[Dict[str, object]],
    target_cnes: str = OCI_TREATED_TARGET_CNES,
) -> Optional[Dict[str, object]]:
    normalized_target = _normalize_cnes(target_cnes)
    for item in sources or []:
        analysis = item.get("analysis") or {}
        cnes_summary = analysis.get("cnes_summary") or {}
        units = cnes_summary.get("units") or []
        if any(_normalize_cnes(unit.get("cnes")) == normalized_target for unit in units):
            return item
    return None


def _build_oci_cleanup_patient_indexes(
    patient_details: List[Dict[str, object]],
) -> Tuple[
    Dict[str, List[Dict[str, object]]],
    Dict[str, set],
    Dict[str, set],
    Dict[Tuple[str, str], Dict[str, object]],
    Dict[Tuple[str, str], Dict[str, int]],
    int,
]:
    oci_by_dob: Dict[str, List[Dict[str, object]]] = {}
    oci_by_cpf: Dict[str, set] = {}
    oci_by_cns: Dict[str, set] = {}
    oci_patient_registry: Dict[Tuple[str, str], Dict[str, object]] = {}
    patient_proc_budgets: Dict[Tuple[str, str], Dict[str, int]] = {}
    combo_occurrences = 0

    for patient in patient_details or []:
        if not isinstance(patient, dict):
            continue

        name = normalize_name(patient.get("name"))
        dob = normalize_date(patient.get("dob"))
        if not name or not dob:
            continue

        patient_key = _register_oci_patient_candidate(
            oci_by_dob,
            oci_by_cpf,
            oci_by_cns,
            oci_patient_registry,
            name,
            dob,
            cpf=patient.get("cpf") or "",
            cns=patient.get("cns") or "",
        )
        if not patient_key:
            continue

        actual_procedures = {
            _normalize_proc_code(proc_code): int(qty or 0)
            for proc_code, qty in (patient.get("procedures") or {}).items()
            if _normalize_proc_code(proc_code)
        }
        combo_proc_totals: Dict[str, int] = {}
        for combo in patient.get("formed_combos") or []:
            if not isinstance(combo, dict):
                continue
            combo_occurrences += 1
            for proc_code, qty in (combo.get("matched_procedures") or {}).items():
                normalized_proc = _normalize_proc_code(proc_code)
                if not normalized_proc:
                    continue
                combo_proc_totals[normalized_proc] = combo_proc_totals.get(normalized_proc, 0) + int(qty or 0)

        patient_budget = patient_proc_budgets.setdefault(patient_key, {})
        for proc_code, qty in combo_proc_totals.items():
            actual_qty = int(actual_procedures.get(proc_code) or 0)
            capped_qty = min(int(qty or 0), actual_qty) if actual_qty > 0 else int(qty or 0)
            if capped_qty <= 0:
                continue
            patient_budget[proc_code] = patient_budget.get(proc_code, 0) + capped_qty

    return (
        oci_by_dob,
        oci_by_cpf,
        oci_by_cns,
        oci_patient_registry,
        patient_proc_budgets,
        combo_occurrences,
    )


def _generate_treated_bpa_from_oci_analysis(
    request,
    bpa_file_name: str,
    bpa_bytes: bytes,
    patient_details: List[Dict[str, object]],
    target_cnes: str = OCI_TREATED_TARGET_CNES,
) -> Dict[str, object]:
    (
        oci_by_dob,
        oci_by_cpf,
        oci_by_cns,
        oci_patient_registry,
        patient_proc_budgets,
        combo_occurrences,
    ) = _build_oci_cleanup_patient_indexes(patient_details)

    is_bpa_excel = bpa_file_name.lower().endswith((".xlsx", ".xls"))
    bpa_lines_before = 0
    bpa_lines_after = 0
    oci_patients_removed = 0
    affected_rows = []
    status_counts = {
        "removed": 0,
        "altered": 0,
        "kept": 0,
    }
    patient_match_counts = {
        "cpf": 0,
        "cns": 0,
        "name_dob": 0,
    }
    identifier_availability = {
        "bpa_with_cpf": 0,
        "bpa_with_cns": 0,
    }

    file_id = str(uuid.uuid4())
    path = os.path.join(tempfile.gettempdir(), file_id)
    qtd_header_name = ""

    if is_bpa_excel:
        wb = openpyxl.load_workbook(io.BytesIO(bpa_bytes), read_only=True, data_only=True)
        sheet_name = "bpa original"
        if sheet_name not in wb.sheetnames:
            raise HttpError(400, f"Aba '{sheet_name}' não encontrada no arquivo BPA.")

        ws = wb[sheet_name]
        name_col_idx = None
        dob_col_idx = None
        proc_col_idx = None
        qtd_col_idx = None

        for idx, cell in enumerate(ws[1], 1):
            val = str(cell.value).strip().lower() if cell.value else ""
            if val == "prd-nmpac":
                name_col_idx = idx
            elif val == "prd-dtnasc":
                dob_col_idx = idx
            elif val == "prd-pa" or val == "prd_pa":
                proc_col_idx = idx
            elif val == "prd-qt" or val == "prd_qt" or val == "qtd":
                qtd_col_idx = idx

        if not name_col_idx or not dob_col_idx or not proc_col_idx or not qtd_col_idx:
            raise HttpError(400, "Colunas 'prd-nmpac', 'prd-dtnasc', 'prd-qt' e/ou 'prd-pa' não encontradas na aba 'bpa original'.")

        normalized_headers = {
            normalize_header_name(cell.value): idx
            for idx, cell in enumerate(ws[1], 1)
            if cell.value is not None
        }

        def _find_excel_header_index(aliases):
            for alias in aliases:
                if normalize_header_name(alias) in normalized_headers:
                    return normalized_headers[normalize_header_name(alias)]
            return None

        cns_col_idx = _find_excel_header_index(BPA_I_EXCEL_ALIASES.get("cns_paciente", []))
        cpf_col_idx = _find_excel_header_index(BPA_I_EXCEL_ALIASES.get("cpf_paciente", []))

        excel_rows = []
        bpa_lines_before = ws.max_row - 1 if ws.max_row > 1 else 0
        headers = [str(cell.value) if cell.value else f"Col{i}" for i, cell in enumerate(ws[1], 1)]
        qtd_header_name = headers[qtd_col_idx - 1] if qtd_col_idx else ""
        for row_idx in range(2, ws.max_row + 1):
            row_data = {}
            for c_idx in range(1, ws.max_column + 1):
                val = ws.cell(row=row_idx, column=c_idx).value
                row_data[headers[c_idx - 1]] = str(val) if val is not None else ""
            excel_rows.append({"row_idx": row_idx, "row_data": row_data, "include": True})

        rows_removed_count = 0
        for excel_row in reversed(excel_rows):
            row_idx = excel_row["row_idx"]
            name_val = ws.cell(row=row_idx, column=name_col_idx).value
            dob_val = ws.cell(row=row_idx, column=dob_col_idx).value
            proc_val = ws.cell(row=row_idx, column=proc_col_idx).value
            qtd_val = ws.cell(row=row_idx, column=qtd_col_idx).value

            name = normalize_name(name_val)
            dob = normalize_date(dob_val)
            proc = _normalize_proc_code(proc_val)
            qtd_str = str(qtd_val).strip() if qtd_val else ""
            cns_val = ws.cell(row=row_idx, column=cns_col_idx).value if cns_col_idx else ""
            cpf_val = ws.cell(row=row_idx, column=cpf_col_idx).value if cpf_col_idx else ""
            normalized_bpa_cns = normalize_cns(cns_val)
            normalized_bpa_cpf = normalize_cpf(cpf_val)
            if normalized_bpa_cpf:
                identifier_availability["bpa_with_cpf"] += 1
            if normalized_bpa_cns:
                identifier_availability["bpa_with_cns"] += 1

            matched_patient_key, matched_criterion = _resolve_oci_patient_match(
                name,
                dob,
                normalized_bpa_cpf,
                normalized_bpa_cns,
                oci_by_dob,
                oci_by_cpf,
                oci_by_cns,
            )
            if matched_patient_key:
                patient_meta = oci_patient_registry.get(matched_patient_key)
                if patient_meta:
                    patient_meta["found"] = True
                    if not patient_meta.get("match_criterion"):
                        patient_meta["match_criterion"] = matched_criterion
                        patient_match_counts[matched_criterion] = patient_match_counts.get(matched_criterion, 0) + 1

            if matched_patient_key:
                row_data = dict(excel_row["row_data"])
                is_oci_prefix = proc.startswith(OCI_PREFIXES)
                patient_budget = patient_proc_budgets.get(matched_patient_key, {})
                qtd_to_remove = patient_budget.get(proc, 0)

                if not is_oci_prefix and qtd_to_remove > 0:
                    qtd_bpa = 1
                    try:
                        qtd_bpa = int(qtd_str)
                    except Exception:
                        pass
                    if qtd_bpa == 0:
                        qtd_bpa = 1

                    if qtd_bpa <= qtd_to_remove:
                        excel_row["include"] = False
                        patient_budget[proc] -= qtd_bpa
                        row_data["_status"] = "removed"
                        row_data["_removed_qty"] = qtd_bpa
                        status_counts["removed"] += 1
                        rows_removed_count += 1
                        affected_rows.append(row_data)
                    else:
                        new_qtd = qtd_bpa - qtd_to_remove
                        patient_budget[proc] = 0
                        new_qtd_str = str(new_qtd).zfill(len(qtd_str) if len(qtd_str) > 1 else 1)
                        if len(qtd_str) > 1 and new_qtd_str == str(new_qtd):
                            new_qtd_str = str(new_qtd).zfill(6)
                        row_data[headers[qtd_col_idx - 1]] = new_qtd_str
                        excel_row["row_data"][headers[qtd_col_idx - 1]] = new_qtd_str
                        row_data["_status"] = "altered"
                        row_data["_removed_qty"] = qtd_to_remove
                        status_counts["altered"] += 1
                        affected_rows.append(row_data)
                else:
                    status_counts["kept"] += 1

        oci_patients_removed = rows_removed_count
        kept_excel_rows = [item for item in excel_rows if item["include"]]
        bpa_lines_after = len(kept_excel_rows)
        output_records = [
            build_bpa_i_record_from_excel_row(item["row_data"], output_index)
            for output_index, item in enumerate(kept_excel_rows, start=1)
        ]
        header_record = build_bpa_header_record(output_records)
        output_lines = [format_fixed_width_record(header_record, BPA_HEADER_LAYOUT)]
        output_lines.extend(format_bpa_i_record(record) for record in output_records)

        with open(path, "w", encoding="iso-8859-1", newline="") as handle:
            for out_line in output_lines:
                handle.write(out_line + "\r\n")

        wb.close()
        affected_rows.reverse()
        orig_name = os.path.splitext(bpa_file_name)[0]
        new_filename = f"{orig_name}_{target_cnes}_tratado_oci.txt"
    else:
        bpa_text = bpa_bytes.decode("iso-8859-1")
        lines = bpa_text.splitlines()
        output_lines = []

        for line in lines:
            if not line.strip():
                continue

            ident = line[0:2]
            if ident == "03":
                bpa_lines_before += 1
                rec = parse_fixed_width(line, BPA_I_LAYOUT)
                name = normalize_name(rec.get("nome_paciente"))
                dob = normalize_date(rec.get("data_nasc"))
                proc = _normalize_proc_code(rec.get("procedimento"))
                qtd_str = str(rec.get("quantidade", "")).strip()
                normalized_bpa_cns = normalize_cns(rec.get("cns_paciente"))
                normalized_bpa_cpf = normalize_cpf(rec.get("cpf_paciente"))
                if normalized_bpa_cpf:
                    identifier_availability["bpa_with_cpf"] += 1
                if normalized_bpa_cns:
                    identifier_availability["bpa_with_cns"] += 1

                matched_patient_key, matched_criterion = _resolve_oci_patient_match(
                    name,
                    dob,
                    normalized_bpa_cpf,
                    normalized_bpa_cns,
                    oci_by_dob,
                    oci_by_cpf,
                    oci_by_cns,
                )
                if matched_patient_key:
                    patient_meta = oci_patient_registry.get(matched_patient_key)
                    if patient_meta:
                        patient_meta["found"] = True
                        if not patient_meta.get("match_criterion"):
                            patient_meta["match_criterion"] = matched_criterion
                            patient_match_counts[matched_criterion] = patient_match_counts.get(matched_criterion, 0) + 1

                rewritten = False
                if matched_patient_key:
                    row_data = rec.copy()
                    is_oci_prefix = proc.startswith(OCI_PREFIXES)
                    patient_budget = patient_proc_budgets.get(matched_patient_key, {})
                    qtd_to_remove = patient_budget.get(proc, 0)

                    if not is_oci_prefix and qtd_to_remove > 0:
                        qtd_bpa = 1
                        try:
                            qtd_bpa = int(qtd_str)
                        except Exception:
                            pass
                        if qtd_bpa == 0:
                            qtd_bpa = 1

                        if qtd_bpa <= qtd_to_remove:
                            patient_budget[proc] -= qtd_bpa
                            oci_patients_removed += 1
                            row_data["_status"] = "removed"
                            row_data["_removed_qty"] = qtd_bpa
                            status_counts["removed"] += 1
                            affected_rows.append(row_data)
                            continue

                        new_qtd = qtd_bpa - qtd_to_remove
                        patient_budget[proc] = 0
                        new_qtd_str = str(new_qtd).zfill(len(qtd_str) if len(qtd_str) > 1 else 6)
                        rec["quantidade"] = new_qtd_str
                        row_data["quantidade"] = new_qtd_str
                        row_data["_status"] = "altered"
                        row_data["_removed_qty"] = qtd_to_remove
                        status_counts["altered"] += 1
                        affected_rows.append(row_data)
                        rewritten = True
                    else:
                        status_counts["kept"] += 1

                output_lines.append(format_bpa_i_record(rec) if rewritten else line)
            else:
                output_lines.append(line)

        bpa_lines_after = bpa_lines_before - oci_patients_removed
        ext = os.path.splitext(bpa_file_name)[1] or ".txt"
        with open(path, "w", encoding="iso-8859-1", newline="") as handle:
            for out_line in output_lines:
                handle.write(out_line + "\r\n")
        orig_name = os.path.splitext(bpa_file_name)[0]
        new_filename = f"{orig_name}_{target_cnes}_tratado_oci{ext}"

    not_found_patients = []
    leftover_patients = []
    for dob, patients in oci_by_dob.items():
        for patient in patients:
            patient_key = (patient["name"], dob)
            remaining_budget = {
                proc: qty
                for proc, qty in (patient_proc_budgets.get(patient_key) or {}).items()
                if qty > 0 and not str(proc).startswith(OCI_PREFIXES)
            }
            if not patient.get("found"):
                not_found_patients.append(
                    {
                        "name": patient["name"].upper(),
                        "dob": dob,
                        "leftovers": remaining_budget,
                        "leftover_details": _build_procedure_detail_list(remaining_budget),
                        "total_leftover": sum(remaining_budget.values()),
                    }
                )
            elif remaining_budget:
                leftover_patients.append(
                    {
                        "name": patient["name"].upper(),
                        "dob": dob,
                        "leftovers": remaining_budget,
                        "leftover_details": _build_procedure_detail_list(remaining_budget),
                        "total_leftover": sum(remaining_budget.values()),
                    }
                )

    stats = {
        "target_cnes": _normalize_cnes(target_cnes),
        "combo_patients_considered": len(oci_patient_registry),
        "combo_occurrences_considered": combo_occurrences,
        "combo_patients_found_in_bpa": sum(1 for item in oci_patient_registry.values() if item.get("found")),
        "bpa_lines_before": bpa_lines_before,
        "bpa_lines_after": bpa_lines_after,
        "oci_patients_removed": oci_patients_removed,
        "matched_by_cpf": patient_match_counts.get("cpf", 0),
        "matched_by_cns": patient_match_counts.get("cns", 0),
        "matched_by_name_dob": patient_match_counts.get("name_dob", 0),
        "bpa_with_cpf": identifier_availability.get("bpa_with_cpf", 0),
        "bpa_with_cns": identifier_availability.get("bpa_with_cns", 0),
        "status_counts": status_counts,
        "patients_not_found_in_target_bpa": len(not_found_patients),
        "patients_with_leftover_budget": len(leftover_patients),
    }

    _register_temp_download_access(
        request,
        file_id,
        new_filename,
        target_cnes,
    )

    removed_export = _register_removed_only_bpa_file(
        request,
        affected_rows,
        new_filename,
        target_cnes,
        qtd_header=qtd_header_name,
    )

    result = {
        "generated": True,
        "file_id": file_id,
        "file_name": new_filename,
        "source_bpa_file_name": bpa_file_name,
        "target_cnes": _normalize_cnes(target_cnes),
        "stats": stats,
        "not_found_patients": not_found_patients,
        "leftover_patients": leftover_patients,
        "affected_rows": affected_rows,
    }
    if removed_export:
        result["removed_only_file_id"] = removed_export["file_id"]
        result["removed_only_file_name"] = removed_export["file_name"]
    return result


@api_bpa_apac.get("/history/{history_id}/details/")
def get_history_details(request, history_id: int):
    _assert_history_access(request, history_id)
    details = _load_history_details(history_id)
    if not details:
        return {"error": "Detalhes não encontrados"}
    return details


@api_bpa_apac.get("/units/")
def get_units_catalog(request):
    units = _load_cnes_unit_rows()
    return {
        "list": units,
        "total": len(units),
    }


@api_bpa_apac.post("/analyze-file/")
def analyze_file(request, kind: str, file: UploadedFile = File(...)):
    _enforce_rate_limit(request, "analyze-file", limit=30)
    _validate_file_size(file)
    file_bytes = file.read()
    cache_key = _analyze_file_cache_key(file_bytes, kind)
    cached_analysis = cache.get(cache_key)
    if cached_analysis:
        cached_copy = dict(cached_analysis)
        cached_copy["file_name"] = file.name
        cached_copy["from_cache"] = True
        primary_unit = (cached_copy.get("cnes_summary") or {}).get("primary_unit") or {}
        _assert_unit_access(request, primary_unit.get("cnes"))
        cached_copy["mismatch_detected"] = False
        return cached_copy

    try:
        analysis = analyze_uploaded_file(file.name, file_bytes, kind, quick_preview=True)
    except HttpError as primary_error:
        normalized_kind = _normalize_text(kind).lower()
        opposite_kind = "bpa" if normalized_kind == "apac" else "apac"
        try:
            opposite_analysis = analyze_uploaded_file(file.name, file_bytes, opposite_kind, quick_preview=True)
            # Para evitar falsos positivos de arquivos vazios no parse fixo, 
            # verificamos se o opposite_analysis realmente encontrou registros.
            if opposite_analysis.get("total_registros", 0) > 0:
                return {
                    "status": False,
                    "mismatch_detected": True,
                    "expected_kind": normalized_kind,
                    "detected_kind": opposite_kind,
                    "detail": (
                        f"O arquivo selecionado parece ser do tipo {opposite_kind.upper()} "
                        f"e nao corresponde ao campo {normalized_kind.upper()}."
                    ),
                    "detected_preview": opposite_analysis,
                }
        except Exception:
            pass
        raise primary_error
    except Exception as error:
        raise _sanitize_exception_for_client("Nao foi possivel analisar o arquivo enviado.", error)

    _validate_cnes(analysis.get("cnes_summary") or {})
    primary_unit = (analysis.get("cnes_summary") or {}).get("primary_unit") or {}
    _assert_unit_access(request, primary_unit.get("cnes"))
    analysis["mismatch_detected"] = False
    cache.set(cache_key, analysis, timeout=ANALYZE_FILE_CACHE_TIMEOUT)
    log_integra_oci_audit(
        request=request,
        event_type="file_analyze",
        module_item="bpa_limpo" if kind.lower() == "apac" else "formar_combos" if kind.lower() == "bpa" else kind,
        apac_filename=file.name if kind.lower() == "apac" else "",
        bpa_filename=file.name if kind.lower() == "bpa" else "",
        unit_cnes=_normalize_cnes(primary_unit.get("cnes")),
        unit_name=str(primary_unit.get("nome_unidade") or ""),
        competencias=list(analysis.get("competencias") or []),
        result_summary={
            "total_registros": analysis.get("total_registros"),
            "oci_count": analysis.get("oci_count"),
            "from_cache": False,
        },
        result_message=f"Análise de {kind.upper()}: {analysis.get('total_registros', 0)} registro(s)",
    )
    return analysis


@api_bpa_apac.post("/oci-combos/analyze/")
def analyze_oci_combos(request):
    _enforce_rate_limit(request, "oci-combos-analyze")
    return keep_alive_json_streaming(_analyze_oci_combos_internal, request)

def _analyze_oci_combos_internal(request):
    uploaded_files = _get_oci_bpa_uploaded_files(request)
    procedures_files = _get_oci_procedures_uploaded_files(request)
    _validate_files_size(uploaded_files)
    _validate_files_size(procedures_files)
    _cleanup_expired_temp_exports()
    if not uploaded_files and not procedures_files:
        raise HttpError(400, "Por favor, envie ao menos um arquivo BPA ou uma planilha complementar para validar os combos assistenciais.")

    bpa_analyses: List[Dict[str, object]] = []
    bpa_sources: List[Dict[str, object]] = []
    patient_maps: List[Dict[Tuple[str, str], Dict[str, object]]] = []
    supplemental_analyses: List[Dict[str, object]] = []

    for uploaded_file in uploaded_files:
        bpa_bytes = uploaded_file.read()
        analysis = analyze_uploaded_file(uploaded_file.name, bpa_bytes, "bpa")
        _validate_cnes(analysis.get("cnes_summary") or {})
        bpa_analyses.append(analysis)
        bpa_sources.append(
            {
                "file_name": uploaded_file.name,
                "file_bytes": bpa_bytes,
                "analysis": analysis,
            }
        )
        patient_maps.append(_aggregate_patient_procedures("bpa", uploaded_file.name, bpa_bytes))

    for procedures_file in procedures_files:
        procedures_bytes = procedures_file.read()
        supplemental_analyses.append(_build_cce_procedures_analysis(procedures_file.name, procedures_bytes))
        patient_maps.append(_aggregate_patient_procedures("oci_procedures_sheet", procedures_file.name, procedures_bytes))

    bpa_analysis = _summarize_oci_bpa_analyses(bpa_analyses)
    supplemental_analysis = _summarize_oci_supplemental_analyses(supplemental_analyses)
    resolved_unit = _resolve_oci_consolidated_unit(bpa_analyses)
    merged_patients = _merge_many_patient_maps(patient_maps)
    evaluated = _evaluate_oci_combos(merged_patients)

    summary = evaluated["summary"]
    if uploaded_files and supplemental_analysis:
        summary["analysis_mode"] = "bpa_with_procedures_sheet"
    elif uploaded_files:
        summary["analysis_mode"] = bpa_analysis.get("analysis_mode") or "single_bpa"
    else:
        summary["analysis_mode"] = "supplemental_only"
    summary["file_count"] = int(len(uploaded_files or []) + len(procedures_files or []))
    summary["input_files"] = [
        {
            "file_name": item.get("file_name") or "",
            "detected_format": item.get("detected_format") or "",
            "competencias": item.get("competencias") or [],
            "unit_name": ((item.get("cnes_summary") or {}).get("primary_unit") or {}).get("nome_unidade") or "",
            "unit_cnes": ((item.get("cnes_summary") or {}).get("primary_unit") or {}).get("cnes") or "",
        }
        for item in (bpa_analysis.get("input_files") or [])
    ]
    summary["supplemental_sheet_used"] = bool(supplemental_analysis)
    summary["supplemental_sheet_file_name"] = (supplemental_analysis or {}).get("file_name") or ""
    summary["supplemental_sheet_file_names"] = (supplemental_analysis or {}).get("file_names") or (
        [summary["supplemental_sheet_file_name"]] if summary["supplemental_sheet_file_name"] else []
    )
    summary["supplemental_sheet_file_count"] = int((supplemental_analysis or {}).get("file_count") or len(summary["supplemental_sheet_file_names"]))
    summary["supplemental_sheet_rows"] = int((supplemental_analysis or {}).get("matched_rows") or 0)
    summary["supplemental_sheet_quantity"] = int((supplemental_analysis or {}).get("matched_quantity") or 0)
    _assert_unit_access(request, (resolved_unit or {}).get("cnes"))

    generated_treated_bpas: List[Dict[str, object]] = []
    if bpa_sources:
        targets_to_generate = []
        cce_ccd_cnes = [_normalize_cnes(t.get("cnes")) for t in OCI_TREATED_TARGETS]
        
        has_cce_ccd = False
        for src in bpa_sources:
            units = src.get("analysis", {}).get("cnes_summary", {}).get("units", [])
            for unit in units:
                if _normalize_cnes(unit.get("cnes")) in cce_ccd_cnes:
                    has_cce_ccd = True
                    break
            if has_cce_ccd:
                break
                
        if has_cce_ccd or supplemental_analyses:
            targets_to_generate = list(OCI_TREATED_TARGETS)
        else:
            unique_cnes_map = {}
            for src in bpa_sources:
                units = src.get("analysis", {}).get("cnes_summary", {}).get("units", [])
                for unit in units:
                    cnes = _normalize_cnes(unit.get("cnes"))
                    if cnes and cnes not in unique_cnes_map:
                        unique_cnes_map[cnes] = unit.get("nome_unidade") or cnes
            for cnes, nome in unique_cnes_map.items():
                targets_to_generate.append({
                    "code": cnes,
                    "cnes": cnes,
                    "display_name": nome,
                })

        for target in targets_to_generate:
            target_cnes = _normalize_cnes(target.get("cnes"))
            selected_treated_source = _select_oci_treated_bpa_source(bpa_sources, target_cnes)
            if selected_treated_source:
                generated_payload = _generate_treated_bpa_from_oci_analysis(
                    request,
                    selected_treated_source.get("file_name") or "bpa.txt",
                    selected_treated_source.get("file_bytes") or b"",
                    evaluated["patient_details"],
                    target_cnes=target_cnes,
                )
                generated_payload["target_code"] = target.get("code") or ""
                generated_payload["target_display_name"] = target.get("display_name") or target.get("code") or target_cnes
                generated_treated_bpas.append(generated_payload)
            else:
                generated_treated_bpas.append(
                    {
                        "generated": False,
                        "target_code": target.get("code") or "",
                        "target_cnes": target_cnes,
                        "target_display_name": target.get("display_name") or target.get("code") or target_cnes,
                        "notice": (
                            f"Nenhum BPA com o CNES {target_cnes} foi identificado entre os arquivos enviados, "
                            f"por isso o BPA tratado do {target.get('code') or target_cnes} nao foi gerado nesta analise."
                        ),
                    }
                )

    history_record = OciComboAnalysisHistory.objects.create(
        user=request.user,
        bpa_filename=_build_oci_history_filename_label(uploaded_files, procedures_files),
        unit_name=(resolved_unit or {}).get("nome_unidade") or "",
        unit_cnes=(resolved_unit or {}).get("cnes") or "",
        competencias=sorted(set(bpa_analysis.get("competencias") or [])),
        total_patients_analyzed=summary.get("total_patients_analyzed") or 0,
        patients_with_combos=summary.get("patients_with_combos") or 0,
        combo_occurrences=summary.get("combo_occurrences") or 0,
        combo_types_identified=summary.get("combo_types_identified") or 0,
    )

    details_payload = {
        "bpa_analysis": bpa_analysis,
        "bpa_analyses": bpa_analysis.get("input_files") or [],
        "resolved_unit": resolved_unit,
        "supplemental_analysis": supplemental_analysis,
        "supplemental_analyses": supplemental_analyses,
        "summary": summary,
        "combo_summary": evaluated["combo_summary"],
        "patient_details": evaluated["patient_details"],
        "invalid_cid_combo_patients": evaluated["invalid_cid_combo_patients"],
        "invalid_auth_combo_patients": evaluated["invalid_auth_combo_patients"],
        "almost_combo_patients": evaluated["almost_combo_patients"],
        "generated_treated_bpa": generated_treated_bpas[0] if generated_treated_bpas else None,
        "generated_treated_bpas": generated_treated_bpas,
    }
    try:
        save_oci_details(history_record.id, details_payload)
        maybe_run_retention_cleanup()
    except Exception as error:
        print(f"Erro ao salvar detalhes da validacao Integra OCI {history_record.id}: {error}")

    log_audit_event(
        request=request,
        resource="oci_combos",
        action="validar combos integra oci",
        details=(
            f"Arquivos BPA: {len(uploaded_files)} | Unidade: {history_record.unit_name or 'Nao identificada'} | "
            f"Planilhas complementares: {len(procedures_files) or 0} | "
            f"Pacientes analisados: {summary.get('total_patients_analyzed') or 0} | "
            f"Ocorrencias: {summary.get('combo_occurrences') or 0} | "
            f"BPAs tratados: "
            + " | ".join(
                f"{item.get('target_code') or item.get('target_cnes')}: {'sim' if item.get('generated') else 'nao'}"
                for item in generated_treated_bpas
            )
            + f" | Historico: {history_record.id}"
        ),
    )
    log_integra_oci_audit(
        request=request,
        event_type="combo_validate",
        module_item="formar_combos",
        bpa_filename=history_record.bpa_filename or "",
        extra_files=[item.name for item in procedures_files if getattr(item, "name", None)],
        unit_cnes=history_record.unit_cnes or "",
        unit_name=history_record.unit_name or "",
        competencias=history_record.competencias or [],
        history_id=history_record.id,
        history_type="combo",
        result_summary=summary,
        result_message=(
            f"Pacientes analisados: {summary.get('total_patients_analyzed') or 0} | "
            f"Combos: {summary.get('combo_occurrences') or 0} | "
            f"Validados: {summary.get('patients_with_combos') or 0}"
        ),
    )

    return {
        **details_payload,
        "invalid_cid_combo_patients": evaluated["invalid_cid_combo_patients"],
        "invalid_auth_combo_patients": evaluated["invalid_auth_combo_patients"],
        "almost_combo_patients": evaluated["almost_combo_patients"],
        "generated_treated_bpa": generated_treated_bpas[0] if generated_treated_bpas else None,
        "generated_treated_bpas": generated_treated_bpas,
        "history_id": history_record.id,
    }


@api_bpa_apac.get("/integra-oci/audit/event-types/")
def list_integra_oci_audit_event_types(request):
    require_integra_oci_item(request, "auditoria", "Sem permissão para consultar a auditoria do Integra OCI.")
    return list(
        IntegraOciAuditLog.objects.order_by()
        .values_list("event_type", flat=True)
        .distinct()
    )


@api_bpa_apac.get("/integra-oci/audit/")
def list_integra_oci_audit_logs(
    request,
    event_type: str = "",
    unit_cnes: str = "",
    performed_by: str = "",
    username: str = "",
    start_date: str = "",
    end_date: str = "",
    page: int = 1,
    page_size: int = 20,
):
    require_integra_oci_item(request, "auditoria", "Sem permissão para consultar a auditoria do Integra OCI.")

    queryset = IntegraOciAuditLog.objects.all().order_by("-created_at")
    if event_type:
        queryset = queryset.filter(event_type=event_type.strip())
    if unit_cnes:
        queryset = queryset.filter(unit_cnes=unit_cnes.strip())
    if performed_by:
        queryset = queryset.filter(performed_by__icontains=performed_by.strip())
    if username:
        queryset = queryset.filter(username__icontains=username.strip())
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            queryset = queryset.filter(created_at__gte=start_dt)
        except ValueError as exc:
            raise HttpError(400, "Data inicial inválida.") from exc
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(hour=23, minute=59, second=59)
            queryset = queryset.filter(created_at__lte=end_dt)
        except ValueError as exc:
            raise HttpError(400, "Data final inválida.") from exc

    total = queryset.count()
    page = max(page, 1)
    page_size = max(min(page_size, 100), 1)
    start = (page - 1) * page_size
    items = [serialize_integra_oci_audit_log(entry) for entry in queryset[start : start + page_size]]
    total_pages = (total + page_size - 1) // page_size if total else 1
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@api_bpa_apac.get("/oci-combos/history/")
def get_oci_combo_history(request, period: str = "30d", start_date: str = None, end_date: str = None):
    try:
        queryset = OciComboAnalysisHistory.objects.all()
        user_unit_cnes = _get_request_unit_cnes(request)
        if user_unit_cnes:
            queryset = queryset.filter(unit_cnes=user_unit_cnes)
        
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = datetime.strptime(end_date, "%Y-%m-%d")
                end = end.replace(hour=23, minute=59, second=59)
                queryset = queryset.filter(created_at__gte=start, created_at__lte=end)
                normalized_period = "custom"
            except ValueError:
                normalized_period, resolved_start = _resolve_history_period(period)
                if resolved_start is not None:
                    queryset = queryset.filter(created_at__gte=resolved_start)
        else:
            normalized_period, resolved_start = _resolve_history_period(period)
            if resolved_start is not None:
                queryset = queryset.filter(created_at__gte=resolved_start)

        histories = list(queryset[:50])
        history_data = []
        unit_breakdown: Dict[str, Dict[str, object]] = {}
        series = []
        total_invalid_cid_combo_occurrences = 0
        total_patients_with_invalid_cid_combos = 0
        total_invalid_auth_combo_occurrences = 0
        total_patients_with_invalid_auth_combos = 0

        for item in histories:
            local_created_at = timezone.localtime(item.created_at)
            unit_name = item.unit_name or "Unidade nao identificada"
            unit_cnes = item.unit_cnes or ""
            details = _load_oci_history_details(item.id)
            details_summary = details.get("summary", {}) if isinstance(details, dict) else {}
            invalid_cid_combo_occurrences = int(details_summary.get("invalid_cid_combo_occurrences") or 0)
            patients_with_invalid_cid_combos = int(details_summary.get("patients_with_invalid_cid_combos") or 0)
            invalid_auth_combo_occurrences = int(details_summary.get("invalid_auth_combo_occurrences") or 0)
            patients_with_invalid_auth_combos = int(details_summary.get("patients_with_invalid_auth_combos") or 0)
            
            reasons = []
            if invalid_cid_combo_occurrences:
                reasons.append("CID incompatível")
            if invalid_auth_combo_occurrences:
                reasons.append("Autorização inválida")
            non_formed_reason = " | ".join(reasons) if reasons else ""

            history_data.append({
                "id": item.id,
                "created_at": local_created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "bpa_filename": item.bpa_filename or "N/A",
                "unit_name": unit_name,
                "unit_cnes": unit_cnes,
                "competencias": item.competencias or [],
                "total_patients_analyzed": item.total_patients_analyzed,
                "patients_with_combos": item.patients_with_combos,
                "combo_occurrences": item.combo_occurrences,
                "invalid_cid_combo_occurrences": invalid_cid_combo_occurrences,
                "patients_with_invalid_cid_combos": patients_with_invalid_cid_combos,
                "invalid_auth_combo_occurrences": invalid_auth_combo_occurrences,
                "patients_with_invalid_auth_combos": patients_with_invalid_auth_combos,
                "non_formed_reason": non_formed_reason,
                "combo_types_identified": item.combo_types_identified,
                "user": _display_user_name(item.user),
                "analysis_mode": details_summary.get("analysis_mode") or "single_bpa",
                "supplemental_sheet_file_name": details_summary.get("supplemental_sheet_file_name") or "",
                "supplemental_sheet_file_names": details_summary.get("supplemental_sheet_file_names") or [],
                "supplemental_sheet_file_count": int(details_summary.get("supplemental_sheet_file_count") or 0),
                "supplemental_sheet_used": bool(details_summary.get("supplemental_sheet_used")),
            })

            total_invalid_cid_combo_occurrences += invalid_cid_combo_occurrences
            total_patients_with_invalid_cid_combos += patients_with_invalid_cid_combos
            total_invalid_auth_combo_occurrences += invalid_auth_combo_occurrences
            total_patients_with_invalid_auth_combos += patients_with_invalid_auth_combos

            bucket = unit_breakdown.setdefault(
                unit_name,
                {
                    "unit_name": unit_name,
                    "unit_cnes": unit_cnes,
                    "analyses": 0,
                    "combo_occurrences": 0,
                    "patients_with_combos": 0,
                    "invalid_cid_combo_occurrences": 0,
                    "invalid_auth_combo_occurrences": 0,
                },
            )
            bucket["analyses"] += 1
            bucket["combo_occurrences"] += item.combo_occurrences
            bucket["patients_with_combos"] += item.patients_with_combos
            bucket["invalid_cid_combo_occurrences"] += invalid_cid_combo_occurrences
            bucket["invalid_auth_combo_occurrences"] += invalid_auth_combo_occurrences

            series.append({
                "label": local_created_at.strftime("%d/%m %H:%M"),
                "unit_name": unit_name,
                "combo_occurrences": item.combo_occurrences,
                "patients_with_combos": item.patients_with_combos,
            })

        total_combo_occurrences = sum(item.combo_occurrences for item in histories)
        total_patients_with_combos = sum(item.patients_with_combos for item in histories)
        total_patients_analyzed = sum(item.total_patients_analyzed for item in histories)
        top_unit = None
        if unit_breakdown:
            top_unit = max(unit_breakdown.values(), key=lambda row: (row["combo_occurrences"], row["patients_with_combos"], row["analyses"]))

        return {
            "summary": {
                "period": normalized_period,
                "total_analyses": len(histories),
                "total_combo_occurrences": total_combo_occurrences,
                "total_patients_with_combos": total_patients_with_combos,
                "total_invalid_cid_combo_occurrences": total_invalid_cid_combo_occurrences,
                "total_patients_with_invalid_cid_combos": total_patients_with_invalid_cid_combos,
                "total_invalid_auth_combo_occurrences": total_invalid_auth_combo_occurrences,
                "total_patients_with_invalid_auth_combos": total_patients_with_invalid_auth_combos,
                "total_patients_analyzed": total_patients_analyzed,
                "top_unit": top_unit,
                "unit_breakdown": sorted(
                    unit_breakdown.values(),
                    key=lambda row: (-row["combo_occurrences"], -row["patients_with_combos"], row["unit_name"]),
                ),
                "series": list(reversed(series)),
            },
            "history": history_data,
        }
    except Exception as e:
        raise _sanitize_exception_for_client("Não foi possível buscar o histórico da validação Integra OCI.", e)


@api_bpa_apac.get("/oci-combos/history/{history_id}/details/")
def get_oci_combo_history_details(request, history_id: int, export_type: str = ""):
    history = OciComboAnalysisHistory.objects.filter(id=history_id).first()
    if history:
        _assert_unit_access(request, history.unit_cnes)
    details = _load_oci_history_details(history_id)
    if not details:
        return {"error": "Detalhes da validacao Integra OCI nao encontrados"}
    # Registra auditoria de download quando export_type é informado
    if export_type:
        action_label = {
            "pdf_detailed": "download PDF detalhado historico OCI",
            "pdf_summary": "download PDF resumido historico OCI",
            "csv": "download CSV historico OCI",
        }.get(export_type, f"download historico OCI ({export_type})")
        log_audit_event(
            request=request,
            resource="oci_combos",
            action=action_label,
            resource_id=history_id,
            details=f"Histórico ID: {history_id} | Tipo: {export_type}",
        )
        log_integra_oci_audit(
            request=request,
            event_type="combo_download",
            module_item="historico",
            bpa_filename=history.bpa_filename if history else "",
            unit_cnes=history.unit_cnes if history else "",
            unit_name=history.unit_name if history else "",
            competencias=list(history.competencias or []) if history else [],
            history_id=history_id,
            history_type="combo",
            result_message=f"Exportação {export_type} do histórico #{history_id}",
            result_summary={"export_type": export_type},
        )
    return details

@api_bpa_apac.get("/history/")
def get_history(request, period: str = "30d", start_date: str = None, end_date: str = None):
    try:
        queryset = BpaApacImportHistory.objects.all()
        user_unit_cnes = _get_request_unit_cnes(request)
        
        if start_date and end_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = datetime.strptime(end_date, "%Y-%m-%d")
                end = end.replace(hour=23, minute=59, second=59)
                queryset = queryset.filter(created_at__gte=start, created_at__lte=end)
            except ValueError:
                pass
        else:
            _, resolved_start = _resolve_history_period(period)
            if resolved_start is not None:
                queryset = queryset.filter(created_at__gte=resolved_start)

        histories = list(queryset[:200])
        data = []
        unit_breakdown: Dict[str, Dict[str, object]] = {}
        removal_series = []
        for h in histories:
            details = _load_history_details_raw(h.id)
            unit_cnes = _history_unit_cnes(details)
            if user_unit_cnes and unit_cnes and user_unit_cnes != unit_cnes:
                continue
            local_created_at = timezone.localtime(h.created_at)
            metadata = details.get("metadata", {}) if isinstance(details, dict) else {}
            resolved_unit = metadata.get("resolved_unit") or {}
            unit_label = resolved_unit.get("nome_unidade") or "Unidade não identificada"
            unit_cnes = resolved_unit.get("cnes") or h.unit_cnes or ""

            data.append({
                "id": h.id,
                "created_at": local_created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "apac_filename": h.apac_filename or "N/A",
                "bpa_filename": h.bpa_filename or "N/A",
                "bpa_lines_before": h.bpa_lines_before,
                "bpa_lines_after": h.bpa_lines_after,
                "oci_patients_removed": h.oci_patients_removed,
                "apac_oci_count": h.apac_oci_count,
                "user": _display_user_name(h.user),
                "unit_name": unit_label,
                "unit_cnes": unit_cnes,
                "competencias": metadata.get("competencias", []),
                "apac_analysis": metadata.get("apac_analysis"),
                "bpa_analysis": metadata.get("bpa_analysis"),
            })

            bucket = unit_breakdown.setdefault(
                unit_label,
                {
                    "unit_name": unit_label,
                    "unit_cnes": unit_cnes,
                    "imports": 0,
                    "oci_patients_removed": 0,
                    "apac_oci_count": 0,
                },
            )
            bucket["imports"] += 1
            bucket["oci_patients_removed"] += h.oci_patients_removed
            bucket["apac_oci_count"] += h.apac_oci_count

            removal_series.append({
                "label": local_created_at.strftime('%d/%m %H:%M'),
                "oci_patients_removed": h.oci_patients_removed,
                "apac_oci_count": h.apac_oci_count,
                "unit_name": unit_label,
            })
            if len(data) >= 50:
                break
        
        # Calculate summary
        total_removed = sum(item["oci_patients_removed"] for item in data)
        avg_removed = total_removed / len(data) if data else 0
        top_unit = None
        if unit_breakdown:
            top_unit = max(unit_breakdown.values(), key=lambda item: (item["imports"], item["oci_patients_removed"]))
        
        return {
            "summary": {
                "total_removed_last_10": total_removed,
                "avg_removed_per_import": round(avg_removed, 2),
                "total_imports": len(data),
                "unit_breakdown": sorted(
                    unit_breakdown.values(),
                    key=lambda item: (-item["imports"], -item["oci_patients_removed"], item["unit_name"]),
                ),
                "removal_series": list(reversed(removal_series)),
                "top_unit": top_unit,
            },
            "history": data
        }
    except Exception as e:
        raise _sanitize_exception_for_client("Não foi possível buscar o histórico.", e)
@api_bpa_apac.get("/download/{file_id}/")
def download_file(request, file_id: str, filename: str, kind: str = "treated"):
    _cleanup_expired_temp_exports()
    file_id = _validate_download_file_id(file_id)
    path = _resolve_temp_download_path(file_id) if not file_id.isdigit() else ""
    should_remove_temp = False
    history_details = None
    history_record = None
    if path and os.path.exists(path):
        temp_download_payload = _assert_temp_download_access(request, file_id)
        filename = temp_download_payload.get("file_name") or filename
        should_remove_temp = True
    else:
        history_id = None
        try:
            history_id = int(str(file_id))
        except (TypeError, ValueError):
            history_id = None

        if history_id is not None:
            history_details = _assert_history_access(request, history_id)
            metadata = history_details.get("metadata", {}) if isinstance(history_details, dict) else {}
            if kind == "removed":
                stored_name = metadata.get("removed_only_filename") or filename
            else:
                stored_name = metadata.get("treated_filename") or filename
            history_path = _history_output_path(history_id, stored_name)
            if os.path.exists(history_path):
                path = history_path
                filename = stored_name
            history_record = BpaApacImportHistory.objects.filter(id=history_id).first()

    if not os.path.exists(path):
        raise HttpError(404, "Arquivo não encontrado ou já expirou.")

    with open(path, 'rb') as f:
        data = f.read()

    if should_remove_temp:
        os.remove(path)
        cache.delete(_temp_download_cache_key(file_id))
    
    response = HttpResponse(data, content_type='application/octet-stream')
    safe_filename = _sanitize_download_filename(filename)
    response['Content-Disposition'] = f'attachment; filename="{safe_filename}"'
    log_audit_event(
        request=request,
        resource="bpa_apac",
        action="baixar arquivo processado",
        details=f"Arquivo: {safe_filename} | Origem: {file_id}",
    )
    log_integra_oci_audit(
        request=request,
        event_type="bpa_limpo_download",
        module_item="historico",
        apac_filename=getattr(history_record, "apac_filename", "") or "",
        bpa_filename=safe_filename,
        unit_cnes=_normalize_cnes(
            (history_details or {}).get("metadata", {}).get("resolved_unit", {}).get("cnes")
            if isinstance(history_details, dict)
            else getattr(history_record, "unit_cnes", "")
        ),
        unit_name=str(
            ((history_details or {}).get("metadata", {}) or {}).get("resolved_unit", {}).get("nome_unidade")
            if isinstance(history_details, dict)
            else ""
        ),
        history_id=int(file_id) if str(file_id).isdigit() else None,
        history_type="bpa" if history_record else "",
        result_message=f"Download do arquivo {safe_filename}",
        result_summary={"file_id": file_id, "kind": kind},
    )
    return response

@api_bpa_apac.post("/process/")
def process_files(request, apac_file: UploadedFile = File(...), bpa_file: UploadedFile = File(...)):
    _enforce_rate_limit(request, "process")
    return keep_alive_json_streaming(_process_files_internal, request, apac_file, bpa_file)

def _process_files_internal(request, apac_file: UploadedFile, bpa_file: UploadedFile):
    try:
        _validate_file_size(apac_file)
        _validate_file_size(bpa_file)
        apac_bytes = apac_file.read()
        bpa_bytes = bpa_file.read()
        apac_analysis = analyze_uploaded_file(apac_file.name, apac_bytes, "apac")
        bpa_analysis = analyze_uploaded_file(bpa_file.name, bpa_bytes, "bpa")
        _validate_cnes(apac_analysis.get("cnes_summary") or {})
        _validate_cnes(bpa_analysis.get("cnes_summary") or {})
        resolved_unit = _resolve_import_unit(apac_analysis, bpa_analysis)
        _assert_unit_access(request, (resolved_unit or {}).get("cnes"))
        _cleanup_expired_temp_exports()
        
        is_apac_excel = apac_file.name.lower().endswith(('.xlsx', '.xls'))
        is_bpa_excel = bpa_file.name.lower().endswith(('.xlsx', '.xls'))
        
        # Determine engine for Pandas if Excel
        apac_engine = 'openpyxl' if apac_file.name.lower().endswith('.xlsx') else None
        
        oci_by_dob = {}
        oci_by_cpf = {}
        oci_by_cns = {}
        oci_patient_registry = {}
        oci_combo_map = {}
        patient_match_counts = {
            "cpf": 0,
            "cns": 0,
            "name_dob": 0,
        }
        identifier_availability = {
            "apac_with_cpf": 0,
            "apac_with_cns": 0,
            "bpa_with_cpf": 0,
            "bpa_with_cns": 0,
        }
        
        # We need to map which procedures a patient ACTUALLY DID in the APAC
        # to ensure we ONLY remove those specific procedures from the BPA.
        # But wait, the user's print shows "REGISTRO DE PROCEDIMENTOS" in APAC, which means
        # we need to read APAC_PROC (aba PROCEDIMENTOS) if it's Excel, or ident '13' if it's TXT.
        
        # To make it simpler and follow the user's rule exactly:
        # "está listado para excluir apenas 0301010072, 0211060020, 0211060127 e 0211060259"
        # We need to collect the specific procedures from APAC for that patient.
        
        oci_patients_procs = {} # Map (name, dob) -> dict {procedure_code: quantity}
        
        # 1. READ APAC
        if is_apac_excel:
            # We need to read BOTH CORPO and PROCEDIMENTOS to link patient to their procedures
            df_apac_corpo = pd.read_excel(io.BytesIO(apac_bytes), sheet_name="CORPO", header=3, dtype=str, engine=apac_engine)
            corpo_proc_col = _extract_excel_column_name(df_apac_corpo.columns, ["apa_codprinc", "cod_proc_princ"])
            corpo_name_col = _extract_excel_column_name(df_apac_corpo.columns, ["apa_nomepcnte", "nome_paciente"])
            corpo_dob_col = _extract_excel_column_name(df_apac_corpo.columns, ["apa_datanascim", "data_nasc"])
            corpo_apac_num_col = _extract_excel_column_name(df_apac_corpo.columns, ["apa_num", "numero_apac"])
            corpo_cns_col = _extract_excel_column_name(df_apac_corpo.columns, ["apa_cns_paciente", "apa-cns-paciente", "apa cns paciente", "cns_paciente", "cns-paciente", "cns paciente"])
            corpo_cpf_col = _extract_excel_column_name(df_apac_corpo.columns, ["apa_cpf_paciente", "apa-cpf-paciente", "apa cpf paciente", "cpf_paciente", "cpf-paciente", "cpf paciente", "cpf"])
            if not corpo_proc_col:
                raise HttpError(400, "Coluna do procedimento principal não encontrada na aba CORPO do arquivo APAC.")
            if not corpo_name_col or not corpo_dob_col:
                raise HttpError(400, "Colunas do paciente não encontradas na aba CORPO do arquivo APAC.")
            
            try:
                df_apac_proc = pd.read_excel(io.BytesIO(apac_bytes), sheet_name="PROCEDIMENTOS", header=3, dtype=str, engine=apac_engine)
            except Exception:
                raise HttpError(400, "Aba 'PROCEDIMENTOS' não encontrada no arquivo APAC. Ela é necessária para listar os procedimentos exatos.")

            apac_proc_map = _build_apac_linked_proc_map_from_excel(df_apac_proc)

            for _, row in df_apac_corpo.iterrows():
                name = normalize_name(row.get(corpo_name_col))
                dob = normalize_date(row.get(corpo_dob_col))
                apac_num = _normalize_text(row.get(corpo_apac_num_col)) if corpo_apac_num_col else ""
                principal_proc = _normalize_proc_code(row.get(corpo_proc_col))
                cns_paciente = normalize_cns(row.get(corpo_cns_col)) if corpo_cns_col else ""
                cpf_paciente = normalize_cpf(row.get(corpo_cpf_col)) if corpo_cpf_col else ""
                if cpf_paciente:
                    identifier_availability["apac_with_cpf"] += 1
                if cns_paciente:
                    identifier_availability["apac_with_cns"] += 1
                linked_procedures = (apac_proc_map.get(apac_num) or {}).keys()
                if not _is_oci_candidate(principal_proc, linked_procedures):
                    continue
                
                if name and dob:
                    patient_key = _register_oci_patient_candidate(
                        oci_by_dob,
                        oci_by_cpf,
                        oci_by_cns,
                        oci_patient_registry,
                        name,
                        dob,
                        apac_num=apac_num,
                        principal_proc=principal_proc,
                        cpf=cpf_paciente,
                        cns=cns_paciente,
                    )
                    if not patient_key:
                        continue
                    if patient_key not in oci_patients_procs:
                        oci_patients_procs[patient_key] = {}
                    if patient_key not in oci_combo_map:
                        oci_combo_map[patient_key] = {
                            'name': name.upper(),
                            'dob': dob,
                            'apac_num': apac_num,
                            'principal_proc': principal_proc,
                            'procedures': {},
                            'removed_procedures': {},
                            'remaining_procedures': {},
                            'found_in_bpa': False,
                            'total_procedures': 0,
                            'total_removed': 0,
                            'total_remaining': 0,
                        }
                        
                    if apac_num:
                        for p_code, p_qtd in (apac_proc_map.get(apac_num) or {}).items():
                            oci_patients_procs[patient_key][p_code] = oci_patients_procs[patient_key].get(p_code, 0) + p_qtd
                            if not p_code.startswith(OCI_PREFIXES):
                                combo = oci_combo_map[patient_key]
                                combo['procedures'][p_code] = combo['procedures'].get(p_code, 0) + p_qtd
        else:
            # Parse TXT APAC
            apac_body_records = _get_parsed_fixed_width_records(apac_bytes, APAC_CORPO_LAYOUT, "14")
            apac_proc_records = _get_parsed_fixed_width_records(apac_bytes, APAC_PROC_LAYOUT, "13")
            apac_num_to_patient = {} # Map numero_apac -> (name, dob)
            apac_proc_map = {}

            for rec in apac_proc_records:
                apac_num = _normalize_text(rec.get("numero_apac"))
                cod_proc = _normalize_proc_code(rec.get("cod_proc"))
                if apac_num and cod_proc:
                    apac_proc_map.setdefault(apac_num, {})
                    apac_proc_map[apac_num][cod_proc] = apac_proc_map[apac_num].get(cod_proc, 0) + _parse_quantity(rec.get("quantidade"), default=1)

            for rec in apac_body_records:
                cod_proc_princ = _normalize_proc_code(rec.get("cod_proc_princ"))
                name = normalize_name(rec.get("nome_paciente"))
                dob = normalize_date(rec.get("data_nasc"))
                apac_num = _normalize_text(rec.get("numero_apac"))
                cns_paciente = normalize_cns(rec.get("cns_paciente"))
                cpf_paciente = normalize_cpf(rec.get("cpf_paciente"))
                if cpf_paciente:
                    identifier_availability["apac_with_cpf"] += 1
                if cns_paciente:
                    identifier_availability["apac_with_cns"] += 1
                linked_procedures = (apac_proc_map.get(apac_num) or {}).keys()
                if not _is_oci_candidate(cod_proc_princ, linked_procedures):
                    continue

                if name and dob:
                    patient_key = _register_oci_patient_candidate(
                        oci_by_dob,
                        oci_by_cpf,
                        oci_by_cns,
                        oci_patient_registry,
                        name,
                        dob,
                        apac_num=apac_num,
                        principal_proc=cod_proc_princ,
                        cpf=cpf_paciente,
                        cns=cns_paciente,
                    )
                    if not patient_key:
                        continue
                    if patient_key not in oci_patients_procs:
                        oci_patients_procs[patient_key] = {}
                    if patient_key not in oci_combo_map:
                        oci_combo_map[patient_key] = {
                            'name': name.upper(),
                            'dob': dob,
                            'apac_num': apac_num,
                            'principal_proc': cod_proc_princ,
                            'procedures': {},
                            'removed_procedures': {},
                            'remaining_procedures': {},
                            'found_in_bpa': False,
                            'total_procedures': 0,
                            'total_removed': 0,
                            'total_remaining': 0,
                        }

                    if apac_num:
                        apac_num_to_patient[apac_num] = patient_key
                        for cod_proc, qtd_apac in (apac_proc_map.get(apac_num) or {}).items():
                            oci_patients_procs[patient_key][cod_proc] = oci_patients_procs[patient_key].get(cod_proc, 0) + qtd_apac
                            if not cod_proc.startswith(OCI_PREFIXES):
                                combo = oci_combo_map[patient_key]
                                combo['procedures'][cod_proc] = combo['procedures'].get(cod_proc, 0) + qtd_apac

        # 2. READ BPA
        bpa_lines_before = 0
        bpa_lines_after = 0
        oci_patients_removed = 0
        affected_rows = []
        status_counts = {
            "removed": 0,
            "altered": 0,
            "kept": 0,
        }
        
        file_id = str(uuid.uuid4())
        path = os.path.join(tempfile.gettempdir(), file_id)
        qtd_header_name = ""
        
        if is_bpa_excel:
            wb = openpyxl.load_workbook(io.BytesIO(bpa_bytes), read_only=True, data_only=True)
            sheet_name = "bpa original"
            if sheet_name not in wb.sheetnames:
                raise HttpError(400, f"Aba '{sheet_name}' não encontrada no arquivo BPA.")

            ws = wb[sheet_name]
            name_col_idx = None
            dob_col_idx = None
            proc_col_idx = None
            qtd_col_idx = None
            
            for idx, cell in enumerate(ws[1], 1):
                val = str(cell.value).strip().lower() if cell.value else ""
                if val == "prd-nmpac":
                    name_col_idx = idx
                elif val == "prd-dtnasc":
                    dob_col_idx = idx
                elif val == "prd-pa" or val == "prd_pa":
                    proc_col_idx = idx
                elif val == "prd-qt" or val == "prd_qt" or val == "qtd":
                    qtd_col_idx = idx
                    
            if not name_col_idx or not dob_col_idx or not proc_col_idx or not qtd_col_idx:
                raise HttpError(400, "Colunas 'prd-nmpac', 'prd-dtnasc', 'prd-qt' e/ou 'prd-pa' não encontradas na aba 'bpa original'.")

            normalized_headers = {
                normalize_header_name(cell.value): idx
                for idx, cell in enumerate(ws[1], 1)
                if cell.value is not None
            }

            def _find_excel_header_index(aliases):
                for alias in aliases:
                    if normalize_header_name(alias) in normalized_headers:
                        return normalized_headers[normalize_header_name(alias)]
                return None

            cns_col_idx = _find_excel_header_index(BPA_I_EXCEL_ALIASES.get("cns_paciente", []))
            cpf_col_idx = _find_excel_header_index(BPA_I_EXCEL_ALIASES.get("cpf_paciente", []))

            rows_to_delete = []
            excel_rows = []
            
            # Count how many data rows roughly
            bpa_lines_before = ws.max_row - 1 if ws.max_row > 1 else 0
            
            headers = [str(cell.value) if cell.value else f"Col{i}" for i, cell in enumerate(ws[1], 1)]
            qtd_header_name = headers[qtd_col_idx - 1] if qtd_col_idx else ""
            for row_idx in range(2, ws.max_row + 1):
                row_data = {}
                for c_idx in range(1, ws.max_column + 1):
                    val = ws.cell(row=row_idx, column=c_idx).value
                    row_data[headers[c_idx - 1]] = str(val) if val is not None else ""
                excel_rows.append({"row_idx": row_idx, "row_data": row_data, "include": True})
            
            for excel_row in reversed(excel_rows):
                row_idx = excel_row["row_idx"]
                name_val = ws.cell(row=row_idx, column=name_col_idx).value
                dob_val = ws.cell(row=row_idx, column=dob_col_idx).value
                proc_val = ws.cell(row=row_idx, column=proc_col_idx).value
                qtd_val = ws.cell(row=row_idx, column=qtd_col_idx).value
                
                name = normalize_name(name_val)
                dob = normalize_date(dob_val)
                proc = _normalize_proc_code(proc_val)
                qtd_str = str(qtd_val).strip() if qtd_val else ""
                cns_val = ws.cell(row=row_idx, column=cns_col_idx).value if cns_col_idx else ""
                cpf_val = ws.cell(row=row_idx, column=cpf_col_idx).value if cpf_col_idx else ""
                normalized_bpa_cns = normalize_cns(cns_val)
                normalized_bpa_cpf = normalize_cpf(cpf_val)
                if normalized_bpa_cpf:
                    identifier_availability["bpa_with_cpf"] += 1
                if normalized_bpa_cns:
                    identifier_availability["bpa_with_cns"] += 1
                
                matched_oci = False
                matched_patient_key = None
                matched_criterion = ""

                matched_patient_key, matched_criterion = _resolve_oci_patient_match(
                    name,
                    dob,
                    normalized_bpa_cpf,
                    normalized_bpa_cns,
                    oci_by_dob,
                    oci_by_cpf,
                    oci_by_cns,
                )
                if matched_patient_key:
                    matched_oci = True
                    patient_meta = oci_patient_registry.get(matched_patient_key)
                    if patient_meta:
                        patient_meta['found'] = True
                        if not patient_meta.get('match_criterion'):
                            patient_meta['match_criterion'] = matched_criterion
                            patient_match_counts[matched_criterion] = patient_match_counts.get(matched_criterion, 0) + 1
                    if matched_patient_key in oci_combo_map:
                        oci_combo_map[matched_patient_key]['found_in_bpa'] = True
                            
                if matched_oci:
                    row_data = dict(excel_row["row_data"])
                        
                    # Check if this procedure is actually listed for this patient in the APAC
                    # If it's an OCI proc (starts with 09, 05, 01) OR it was NOT in the APAC list, we keep/modify it
                    is_oci_prefix = proc.startswith(OCI_PREFIXES)
                    
                    patient_procs = oci_patients_procs.get(matched_patient_key, {})
                    qtd_to_remove = patient_procs.get(proc, 0)
                    
                    # Rule: if it is NOT 09, 05, 01 AND we still have quantity to remove for this proc -> remove/alter
                    if not is_oci_prefix and qtd_to_remove > 0:
                        # Before removing, check quantity
                        qtd_bpa = 1
                        try:
                            qtd_bpa = int(qtd_str)
                        except:
                            pass
                            
                        if qtd_bpa == 0:
                            qtd_bpa = 1
                            
                        if qtd_bpa <= qtd_to_remove:
                            # We can remove the entire row
                            rows_to_delete.append(row_idx)
                            excel_row["include"] = False
                            patient_procs[proc] -= qtd_bpa
                            if matched_patient_key in oci_combo_map:
                                combo = oci_combo_map[matched_patient_key]
                                combo['removed_procedures'][proc] = combo['removed_procedures'].get(proc, 0) + qtd_bpa
                            
                            row_data['_status'] = 'removed'
                            row_data['_removed_qty'] = qtd_bpa
                            status_counts["removed"] += 1
                            affected_rows.append(row_data)
                        else:
                            # We only remove part of it
                            new_qtd = qtd_bpa - qtd_to_remove
                            patient_procs[proc] = 0 # Budget exhausted
                            
                            new_qtd_str = str(new_qtd).zfill(len(qtd_str) if len(qtd_str) > 1 else 1)
                            if len(qtd_str) > 1 and new_qtd_str == str(new_qtd):
                                new_qtd_str = str(new_qtd).zfill(6) # standard
                            removed_qty = qtd_to_remove
                            if matched_patient_key in oci_combo_map and removed_qty > 0:
                                combo = oci_combo_map[matched_patient_key]
                                combo['removed_procedures'][proc] = combo['removed_procedures'].get(proc, 0) + removed_qty
                                
                            row_data[headers[qtd_col_idx-1]] = new_qtd_str
                            excel_row["row_data"][headers[qtd_col_idx-1]] = new_qtd_str
                            row_data['_status'] = 'altered'
                            row_data['_removed_qty'] = removed_qty
                            status_counts["altered"] += 1
                            affected_rows.append(row_data)
                    else:
                        status_counts["kept"] += 1
                    
            oci_patients_removed = len(rows_to_delete)
            kept_excel_rows = [item for item in excel_rows if item["include"]]
            bpa_lines_after = len(kept_excel_rows)

            output_records = [
                build_bpa_i_record_from_excel_row(item["row_data"], output_index)
                for output_index, item in enumerate(kept_excel_rows, start=1)
            ]
            header_record = build_bpa_header_record(output_records)
            output_lines = [format_fixed_width_record(header_record, BPA_HEADER_LAYOUT)]
            output_lines.extend(format_bpa_i_record(record) for record in output_records)

            with open(path, "w", encoding="iso-8859-1", newline="") as f:
                for out_line in output_lines:
                    f.write(out_line + "\r\n")

            wb.close()
            
            affected_rows.reverse()
            
            orig_name = os.path.splitext(bpa_file.name)[0]
            new_filename = f"{orig_name}_tratado.txt"
            
        else:
            # Process BPA as TXT
            bpa_text = bpa_bytes.decode('iso-8859-1')
            lines = bpa_text.splitlines()
            output_lines = []
            
            for line in lines:
                if not line.strip():
                    continue
                ident = line[0:2]
                if ident == "03":  # BPA-I
                    bpa_lines_before += 1
                    rec = parse_fixed_width(line, BPA_I_LAYOUT)
                    name = normalize_name(rec.get("nome_paciente"))
                    dob = normalize_date(rec.get("data_nasc"))
                    proc = _normalize_proc_code(rec.get("procedimento"))
                    qtd_str = str(rec.get("quantidade", "")).strip()
                    cns_val = rec.get("cns_paciente")
                    cpf_val = rec.get("cpf_paciente")
                    normalized_bpa_cns = normalize_cns(cns_val)
                    normalized_bpa_cpf = normalize_cpf(cpf_val)
                    if normalized_bpa_cpf:
                        identifier_availability["bpa_with_cpf"] += 1
                    if normalized_bpa_cns:
                        identifier_availability["bpa_with_cns"] += 1
                    
                    matched_oci = False
                    matched_patient_key = None
                    matched_criterion = ""
                    matched_patient_key, matched_criterion = _resolve_oci_patient_match(
                        name,
                        dob,
                        normalized_bpa_cpf,
                        normalized_bpa_cns,
                        oci_by_dob,
                        oci_by_cpf,
                        oci_by_cns,
                    )
                    if matched_patient_key:
                        matched_oci = True
                        patient_meta = oci_patient_registry.get(matched_patient_key)
                        if patient_meta:
                            patient_meta['found'] = True
                            if not patient_meta.get('match_criterion'):
                                patient_meta['match_criterion'] = matched_criterion
                                patient_match_counts[matched_criterion] = patient_match_counts.get(matched_criterion, 0) + 1
                        if matched_patient_key in oci_combo_map:
                            oci_combo_map[matched_patient_key]['found_in_bpa'] = True
                    
                    rewritten = False
                    if matched_oci:
                        row_data = rec.copy()
                        
                        is_oci_prefix = proc.startswith(OCI_PREFIXES)
                        patient_procs = oci_patients_procs.get(matched_patient_key, {})
                        qtd_to_remove = patient_procs.get(proc, 0)
                        
                        if not is_oci_prefix and qtd_to_remove > 0:
                            # Before removing, check quantity
                            qtd_bpa = 1
                            try:
                                qtd_bpa = int(qtd_str)
                            except:
                                pass
                                
                            if qtd_bpa == 0:
                                qtd_bpa = 1
                                
                            if qtd_bpa <= qtd_to_remove:
                                # Skip this line
                                patient_procs[proc] -= qtd_bpa
                                oci_patients_removed += 1
                                if matched_patient_key in oci_combo_map:
                                    combo = oci_combo_map[matched_patient_key]
                                    combo['removed_procedures'][proc] = combo['removed_procedures'].get(proc, 0) + qtd_bpa
                                row_data['_status'] = 'removed'
                                row_data['_removed_qty'] = qtd_bpa
                                status_counts["removed"] += 1
                                affected_rows.append(row_data)
                                continue
                            else:
                                # We only remove part of it
                                new_qtd = qtd_bpa - qtd_to_remove
                                patient_procs[proc] = 0
                                removed_qty = qtd_to_remove
                                if matched_patient_key in oci_combo_map and removed_qty > 0:
                                    combo = oci_combo_map[matched_patient_key]
                                    combo['removed_procedures'][proc] = combo['removed_procedures'].get(proc, 0) + removed_qty
                                
                                new_qtd_str = str(new_qtd).zfill(len(qtd_str) if len(qtd_str) > 1 else 6)
                                rec['quantidade'] = new_qtd_str
                                row_data['quantidade'] = new_qtd_str
                                row_data['_status'] = 'altered'
                                row_data['_removed_qty'] = removed_qty
                                status_counts["altered"] += 1
                                affected_rows.append(row_data)
                                rewritten = True
                        else:
                            status_counts["kept"] += 1

                    output_lines.append(format_bpa_i_record(rec) if rewritten else line)
                else:
                    output_lines.append(line)
                
            bpa_lines_after = bpa_lines_before - oci_patients_removed
            
            ext = os.path.splitext(bpa_file.name)[1]
            if not ext:
                ext = ".txt"
            
            with open(path, "w", encoding="iso-8859-1", newline="") as f:
                for out_line in output_lines:
                    f.write(out_line + "\r\n")
            
            # Format the filename correctly based on the original name
            orig_name = os.path.splitext(bpa_file.name)[0]
            new_filename = f"{orig_name}_tratado{ext}"
            
        # 3. IDENTIFY NOT FOUND PATIENTS AND LEFTOVER PROCEDURES
        not_found_patients = []
        procs_not_found_patients = []
        apac_total_count = 0
        
        for dob, patients in oci_by_dob.items():
            for p in patients:
                apac_total_count += 1
                patient_key = (p['name'], dob)
                if not p['found']:
                    # Calculate total quantity of procedures for this patient in APAC (excluding OCI prefixes)
                    total_qtd = 0
                    pending_procedures = {}
                    if patient_key in oci_patients_procs:
                        pending_procedures = {
                            proc: qty
                            for proc, qty in oci_patients_procs[patient_key].items()
                            if not str(proc).startswith(OCI_PREFIXES)
                        }
                        total_qtd = sum(pending_procedures.values())

                    not_found_patients.append({
                        'name': p['name'].upper(),
                        'dob': dob,
                        'total_procs': total_qtd,
                        'procedures': pending_procedures,
                        'procedure_details': _build_procedure_detail_list(pending_procedures),
                    })
                else:
                    # Patient found, check if there are leftover procedures
                    leftovers = {}
                    if patient_key in oci_patients_procs:
                        for proc, qty in oci_patients_procs[patient_key].items():
                            if qty > 0 and not str(proc).startswith(OCI_PREFIXES):
                                leftovers[proc] = qty
                    if leftovers:
                        procs_not_found_patients.append({
                            'name': p['name'].upper(),
                            'dob': dob,
                            'leftovers': leftovers,
                            'leftover_details': _build_procedure_detail_list(leftovers),
                            'total_leftover': sum(leftovers.values())
                        })

        oci_combo_details = []
        for patient_key, combo in oci_combo_map.items():
            remaining_procedures = {}
            for proc, qty in oci_patients_procs.get(patient_key, {}).items():
                if qty > 0 and not str(proc).startswith(OCI_PREFIXES):
                    remaining_procedures[proc] = qty

            combo['remaining_procedures'] = remaining_procedures
            combo['total_procedures'] = sum(combo['procedures'].values())
            combo['total_removed'] = sum(combo['removed_procedures'].values())
            combo['total_remaining'] = sum(remaining_procedures.values())

            oci_combo_details.append({
                'name': combo['name'],
                'dob': combo['dob'],
                'apac_num': combo['apac_num'],
                'principal_proc': combo['principal_proc'],
                'principal_proc_name': _get_procedure_name(combo['principal_proc']),
                'procedures': combo['procedures'],
                'procedure_details': _build_procedure_detail_list(combo['procedures']),
                'removed_procedures': combo['removed_procedures'],
                'removed_procedure_details': _build_procedure_detail_list(combo['removed_procedures']),
                'remaining_procedures': combo['remaining_procedures'],
                'remaining_procedure_details': _build_procedure_detail_list(combo['remaining_procedures']),
                'found_in_bpa': combo['found_in_bpa'],
                'total_procedures': combo['total_procedures'],
                'total_removed': combo['total_removed'],
                'total_remaining': combo['total_remaining'],
            })
        oci_combo_details.sort(key=lambda item: (item['name'], item['dob']))
              
        # Register history
        stats = {
            "apac_oci_count": apac_total_count,
            "bpa_lines_before": bpa_lines_before,
            "bpa_lines_after": bpa_lines_after,
            "oci_patients_removed": oci_patients_removed,
            "matched_by_cpf": patient_match_counts.get("cpf", 0),
            "matched_by_cns": patient_match_counts.get("cns", 0),
            "matched_by_name_dob": patient_match_counts.get("name_dob", 0),
            "apac_with_cpf": identifier_availability.get("apac_with_cpf", 0),
            "apac_with_cns": identifier_availability.get("apac_with_cns", 0),
            "bpa_with_cpf": identifier_availability.get("bpa_with_cpf", 0),
            "bpa_with_cns": identifier_availability.get("bpa_with_cns", 0),
            "status_counts": status_counts,
        }
        
        history_record = BpaApacImportHistory.objects.create(
            user=request.user,
            apac_filename=apac_file.name,
            bpa_filename=bpa_file.name,
            unit_cnes=_normalize_cnes((resolved_unit or {}).get("cnes")),
            apac_oci_count=stats["apac_oci_count"],
            bpa_lines_before=stats["bpa_lines_before"],
            bpa_lines_after=stats["bpa_lines_after"],
            oci_patients_removed=stats["oci_patients_removed"]
        )
        
        persistent_output_path = _history_output_path(history_record.id, new_filename)
        with open(path, "rb") as source_handle, open(persistent_output_path, "wb") as target_handle:
            target_handle.write(source_handle.read())
        _register_temp_download_access(
            request,
            file_id,
            new_filename,
            (resolved_unit or {}).get("cnes"),
        )
        removed_export = _register_removed_only_bpa_file(
            request,
            affected_rows,
            new_filename,
            (resolved_unit or {}).get("cnes"),
            qtd_header=qtd_header_name,
        )
        removed_only_file_id = None
        removed_only_filename = None
        if removed_export:
            removed_only_file_id = removed_export["file_id"]
            removed_only_filename = removed_export["file_name"]
            persistent_removed_path = _history_output_path(history_record.id, removed_only_filename)
            with open(removed_export["path"], "rb") as source_handle, open(persistent_removed_path, "wb") as target_handle:
                target_handle.write(source_handle.read())
        metadata = {
            "apac_analysis": apac_analysis,
            "bpa_analysis": bpa_analysis,
            "resolved_unit": resolved_unit,
            "competencias": sorted(set((apac_analysis.get("competencias") or []) + (bpa_analysis.get("competencias") or []))),
            "treated_filename": new_filename,
        }
        if removed_only_filename:
            metadata["removed_only_filename"] = removed_only_filename
        try:
            save_bpa_details(
                history_record.id,
                {
                    "affected_rows": affected_rows,
                    "not_found_patients": not_found_patients,
                    "procs_not_found_patients": procs_not_found_patients,
                    "oci_combo_details": oci_combo_details,
                    "stats": stats,
                    "metadata": metadata,
                },
            )
            maybe_run_retention_cleanup()
        except Exception as e:
            print(f"Error saving details JSON: {e}")

        result = {
            "stats": stats,
            "not_found": not_found_patients,
            "procs_not_found_patients": procs_not_found_patients,
            "oci_combo_details": oci_combo_details,
            "affected_rows": affected_rows,
            "file_id": file_id,
            "filename": new_filename,
            "apac_analysis": apac_analysis,
            "bpa_analysis": bpa_analysis,
            "resolved_unit": resolved_unit,
        }
        if removed_only_file_id:
            result["removed_only_file_id"] = removed_only_file_id
            result["removed_only_filename"] = removed_only_filename
        log_audit_event(
            request=request,
            resource="bpa_apac",
            action="processar bpa apac",
            details=(
                f"APAC: {apac_file.name} | BPA: {bpa_file.name} | "
                f"Linhas BPA antes: {bpa_lines_before} | Linhas depois: {bpa_lines_after} | "
                f"Pacientes OCI removidos: {oci_patients_removed} | Historico: {history_record.id}"
            ),
        )
        log_integra_oci_audit(
            request=request,
            event_type="bpa_limpo_process",
            module_item="bpa_limpo",
            apac_filename=apac_file.name,
            bpa_filename=bpa_file.name,
            unit_cnes=_normalize_cnes((resolved_unit or {}).get("cnes")),
            unit_name=(resolved_unit or {}).get("nome_unidade") or "",
            competencias=sorted(set((apac_analysis.get("competencias") or []) + (bpa_analysis.get("competencias") or []))),
            history_id=history_record.id,
            history_type="bpa",
            result_summary=stats,
            result_message=(
                f"Linhas BPA: {stats.get('bpa_lines_before')} -> {stats.get('bpa_lines_after')} | "
                f"Pacientes OCI removidos: {stats.get('oci_patients_removed')} | "
                f"Arquivo gerado: {new_filename}"
            ),
        )
        return result

    except Exception as e:
        log_integra_oci_audit(
            request=request,
            event_type="bpa_limpo_process",
            module_item="bpa_limpo",
            apac_filename=getattr(apac_file, "name", ""),
            bpa_filename=getattr(bpa_file, "name", ""),
            success=False,
            error_message=str(e),
            result_message="Falha ao processar BPA Inteligente.",
        )
        raise _sanitize_exception_for_client("Não foi possível processar os arquivos.", e)
