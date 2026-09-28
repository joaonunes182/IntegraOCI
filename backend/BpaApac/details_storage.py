"""Persistência compactada dos detalhes BPA/APAC/OCI."""

from __future__ import annotations

import gzip
import json
import os
from datetime import timedelta
from pathlib import Path
from typing import Dict, Iterable, Optional

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone


def _details_root() -> Path:
    media_root = getattr(settings, "MEDIA_ROOT", "") or ""
    base = Path(media_root) if media_root else Path(settings.BASE_DIR)
    details_dir = base / "bpa_apac_details"
    details_dir.mkdir(parents=True, exist_ok=True)
    return details_dir


def _outputs_root() -> Path:
    media_root = getattr(settings, "MEDIA_ROOT", "") or ""
    base = Path(media_root) if media_root else Path(settings.BASE_DIR)
    output_dir = base / "bpa_apac_outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def bpa_details_path(history_id: int) -> Path:
    return _details_root() / f"{history_id}_details.json.gz"


def oci_details_path(history_id: int) -> Path:
    return _details_root() / f"oci_{history_id}_details.json.gz"


def _legacy_paths(stem: str) -> Iterable[Path]:
    root = _details_root()
    yield root / f"{stem}.json.gz"
    yield root / f"{stem}.json"


def save_bpa_details(history_id: int, payload: Dict[str, object]) -> None:
    _save_payload(bpa_details_path(history_id), payload)


def save_oci_details(history_id: int, payload: Dict[str, object]) -> None:
    _save_payload(oci_details_path(history_id), payload)


def load_bpa_details(history_id: int) -> Dict[str, object]:
    return _load_payload(f"{history_id}_details")


def load_oci_details(history_id: int) -> Dict[str, object]:
    return _load_payload(f"oci_{history_id}_details")


def _save_payload(path: Path, payload: Dict[str, object]) -> None:
    encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with gzip.open(tmp_path, "wb", compresslevel=6) as handle:
        handle.write(encoded)
    tmp_path.replace(path)
    legacy_plain = path.with_suffix("").with_suffix(".json")
    if legacy_plain.exists():
        legacy_plain.unlink(missing_ok=True)


def _load_payload(stem: str) -> Dict[str, object]:
    for candidate in _legacy_paths(stem):
        if not candidate.exists():
            continue
        try:
            if candidate.suffix == ".gz":
                with gzip.open(candidate, "rt", encoding="utf-8") as handle:
                    data = json.load(handle)
            else:
                with candidate.open("r", encoding="utf-8") as handle:
                    data = json.load(handle)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}
    return {}


def cleanup_artifacts(retention_days: Optional[int] = None) -> Dict[str, int]:
    days = retention_days
    if days is None:
        days = int(getattr(settings, "BPA_APAC_ARTIFACT_RETENTION_DAYS", 90))
    if days <= 0:
        return {"details_removed": 0, "outputs_removed": 0, "compressed_legacy": 0}

    cutoff = timezone.now() - timedelta(days=days)
    cutoff_ts = cutoff.timestamp()

    details_removed = 0
    outputs_removed = 0
    compressed_legacy = 0

    details_root = _details_root()
    for path in details_root.glob("*"):
        if not path.is_file():
            continue
        if path.stat().st_mtime >= cutoff_ts:
            continue
        if path.suffix == ".json" and path.with_name(path.stem + ".json.gz").exists():
            path.unlink(missing_ok=True)
            details_removed += 1
            continue
        path.unlink(missing_ok=True)
        details_removed += 1

    outputs_root = _outputs_root()
    for path in outputs_root.glob("*"):
        if path.is_file() and path.stat().st_mtime < cutoff_ts:
            path.unlink(missing_ok=True)
            outputs_removed += 1

    compressed_legacy += compress_legacy_plain_json()

    return {
        "details_removed": details_removed,
        "outputs_removed": outputs_removed,
        "compressed_legacy": compressed_legacy,
        "retention_days": days,
    }


def compress_legacy_plain_json() -> int:
    converted = 0
    details_root = _details_root()
    for path in details_root.glob("*.json"):
        gz_path = path.with_suffix(".json.gz")
        if gz_path.exists():
            path.unlink(missing_ok=True)
            converted += 1
            continue
        try:
            with path.open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
            if isinstance(payload, dict):
                _save_payload(gz_path, payload)
                path.unlink(missing_ok=True)
                converted += 1
        except Exception:
            continue
    return converted


def maybe_run_retention_cleanup() -> None:
    if not getattr(settings, "BPA_APAC_AUTO_CLEANUP", True):
        return
    cache_key = "bpa_apac:last_retention_cleanup"
    if cache.get(cache_key):
        return
    cleanup_artifacts()
    cache.set(cache_key, timezone.now().isoformat(), timeout=24 * 60 * 60)
