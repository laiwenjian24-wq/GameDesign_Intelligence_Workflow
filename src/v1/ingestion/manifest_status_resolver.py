"""Resolve source status metadata from import_manifest without mutating it."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path, PureWindowsPath
from typing import Any, Dict, Iterable, List, Tuple

from src.v1.ingestion.status_policy import normalize_status


MANIFEST_PATH_FIELDS = ("file_path", "path", "file", "original_path", "source_file")
MOJIBAKE_MARKERS = ("鍒", "绔", "瑙", "娓", "鏁", "粎", "绱", "绗", "犳", "€")


@dataclass
class ManifestStatusResolution:
    status: str
    method: str
    reason: str
    manifest_entry: Dict[str, Any] | None = None
    manifest_matched_path: str = ""
    ambiguous_entries: List[Dict[str, Any]] = field(default_factory=list)

    def to_metadata(self) -> Dict[str, Any]:
        payload = {
            "status_resolution_method": self.method,
            "status_resolution_reason": self.reason,
        }
        if self.manifest_entry:
            payload["manifest_entry"] = self.manifest_entry
        if self.manifest_matched_path:
            payload["manifest_matched_path"] = self.manifest_matched_path
        if self.ambiguous_entries:
            payload["manifest_ambiguous_entries"] = self.ambiguous_entries
        return payload


@dataclass
class ManifestStatusDiagnostics:
    manifest_path: str = ""
    manifest_entries_loaded: int = 0
    matched_file_count: int = 0
    unmatched_file_count: int = 0
    ambiguous_file_count: int = 0
    invalid_status_count: int = 0
    matched_files: List[Dict[str, Any]] = field(default_factory=list)
    unmatched_files: List[Dict[str, Any]] = field(default_factory=list)
    ambiguous_files: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ManifestLoadResult:
    entries: List[Dict[str, Any]]
    encoding_used: str = ""
    warning: str = ""


class ManifestStatusResolver:
    """Match loaded files to manifest entries using path-safe fallbacks."""

    def __init__(
        self,
        manifest_path: str | Path | None = None,
        project_root: str | Path | None = None,
    ) -> None:
        self.manifest_path = Path(manifest_path) if manifest_path else None
        self.project_root = Path(project_root).resolve() if project_root else Path.cwd().resolve()
        self.manifest_parent = (
            self.manifest_path.parent.resolve()
            if self.manifest_path and self.manifest_path.exists()
            else self.project_root
        )
        self.load_result = load_manifest_entries(self.manifest_path)
        self.entries = self.load_result.entries
        self._exact_index: Dict[str, List[Dict[str, Any]]] = {}
        self._basename_index: Dict[str, List[Dict[str, Any]]] = {}
        self._build_indexes()

    def resolve(self, original_path: str | Path, source_file: str = "") -> ManifestStatusResolution:
        candidates = self._candidate_keys(original_path, source_file)
        for key in candidates:
            matches = self._exact_index.get(key, [])
            if len(matches) == 1:
                return self._resolution_from_entry(matches[0], "path_match", f"matched path key: {key}")
            if len(matches) > 1:
                return ManifestStatusResolution(
                    status="unknown",
                    method="ambiguous",
                    reason=f"multiple manifest entries matched path key: {key}",
                    ambiguous_entries=[self._public_entry(match) for match in matches],
                )

        basename = _normalize_basename(source_file or str(original_path))
        basename_matches = self._basename_index.get(basename, [])
        if len(basename_matches) == 1:
            return self._resolution_from_entry(
                basename_matches[0],
                "basename_match",
                f"matched basename: {basename}",
            )
        if len(basename_matches) > 1:
            return ManifestStatusResolution(
                status="unknown",
                method="ambiguous",
                reason=f"multiple manifest entries matched basename: {basename}",
                ambiguous_entries=[self._public_entry(match) for match in basename_matches],
            )

        return ManifestStatusResolution(
            status="unknown",
            method="unmatched",
            reason="no manifest path or basename matched loaded file",
        )

    def empty_diagnostics(self) -> ManifestStatusDiagnostics:
        return ManifestStatusDiagnostics(
            manifest_path=str(self.manifest_path) if self.manifest_path else "",
            manifest_entries_loaded=len(self.entries),
        )

    def _load_entries(self) -> List[Dict[str, Any]]:
        if not self.manifest_path or not self.manifest_path.exists():
            return []
        try:
            payload = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        if isinstance(payload, dict):
            items = payload.get("items") or payload.get("files") or payload.get("documents") or []
            return [item for item in items if isinstance(item, dict)]
        return []

    def _build_indexes(self) -> None:
        for entry in self.entries:
            for raw_path in _entry_paths(entry):
                for key in self._manifest_entry_keys(raw_path):
                    self._exact_index.setdefault(key, []).append(entry)
                basename = _normalize_basename(raw_path)
                if basename:
                    self._basename_index.setdefault(basename, []).append(entry)

    def _manifest_entry_keys(self, raw_path: str) -> List[str]:
        keys = {_normalize_path_key(raw_path)}
        path = Path(raw_path)
        if not path.is_absolute():
            keys.add(_normalize_path_key(self.project_root / raw_path))
            keys.add(_normalize_path_key(self.manifest_parent / raw_path))
        return sorted(key for key in keys if key)

    def _candidate_keys(self, original_path: str | Path, source_file: str) -> List[str]:
        raw_path = str(original_path)
        keys = {
            _normalize_path_key(raw_path),
            _normalize_path_key(Path(raw_path).absolute()),
            _relative_key(raw_path, self.project_root),
            _relative_key(raw_path, self.manifest_parent),
        }
        if source_file:
            keys.add(_normalize_path_key(source_file))
        return sorted(key for key in keys if key)

    def _resolution_from_entry(
        self,
        entry: Dict[str, Any],
        method: str,
        reason: str,
    ) -> ManifestStatusResolution:
        raw_status = str(entry.get("status", "unknown"))
        status = normalize_status(raw_status)
        if status == "unknown" and raw_status.strip().lower() != "unknown":
            return ManifestStatusResolution(
                status="unknown",
                method="invalid_status",
                reason=f"manifest status is not allowed: {raw_status}",
                manifest_entry=self._public_entry(entry),
                manifest_matched_path=_first_entry_path(entry),
            )
        return ManifestStatusResolution(
            status=status,
            method=method,
            reason=reason,
            manifest_entry=self._public_entry(entry),
            manifest_matched_path=_first_entry_path(entry),
        )

    def resolution_from_manifest_entry_direct(
        self,
        entry: Dict[str, Any],
    ) -> ManifestStatusResolution:
        resolution = self._resolution_from_entry(
            entry,
            "manifest_entry_direct",
            "status came directly from selected manifest entry",
        )
        if resolution.method == "invalid_status":
            return resolution
        return ManifestStatusResolution(
            status=resolution.status,
            method="manifest_entry_direct",
            reason="status came directly from selected manifest entry",
            manifest_entry=resolution.manifest_entry,
            manifest_matched_path=resolution.manifest_matched_path,
        )

    def _public_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        return {
            key: value
            for key, value in entry.items()
            if key in {*MANIFEST_PATH_FIELDS, "status", "asset_type", "confidence", "tags"}
        }


def load_manifest_entries(manifest_path: str | Path | None) -> ManifestLoadResult:
    if not manifest_path:
        return ManifestLoadResult(entries=[], warning="manifest_path_not_provided")
    path = Path(manifest_path)
    if not path.exists():
        return ManifestLoadResult(entries=[], warning=f"manifest_not_found: {path}")
    last_error = ""
    for encoding in ("utf-8-sig", "utf-8", "gb18030", "cp936"):
        try:
            raw = path.read_text(encoding=encoding)
            payload = json.loads(raw)
            return ManifestLoadResult(
                entries=_manifest_payload_items(payload),
                encoding_used=encoding,
            )
        except UnicodeDecodeError as exc:
            last_error = str(exc)
        except json.JSONDecodeError as exc:
            last_error = str(exc)
            break
        except OSError as exc:
            return ManifestLoadResult(entries=[], warning=f"manifest_read_failed: {exc}")
    return ManifestLoadResult(entries=[], warning=f"manifest_parse_failed: {last_error}")


def inspect_manifest(manifest_path: str | Path) -> Dict[str, Any]:
    path = Path(manifest_path)
    load_result = load_manifest_entries(path)
    entries = load_result.entries
    rows: List[Dict[str, Any]] = []
    status_counts: Dict[str, int] = {}
    extension_counts: Dict[str, int] = {}
    field_counts: Dict[str, int] = {field: 0 for field in MANIFEST_PATH_FIELDS}
    existing_paths: List[str] = []
    missing_paths: List[str] = []
    common_parent_counts: Dict[str, int] = {}
    suspected_mojibake_count = 0

    for index, entry in enumerate(entries):
        status = normalize_status(str(entry.get("status", "unknown")))
        status_counts[status] = status_counts.get(status, 0) + 1
        field = _first_present_path_field(entry)
        if field:
            field_counts[field] += 1
        raw_path = _first_entry_path(entry)
        resolved_path = _resolve_entry_path(raw_path, path.parent)
        exists = _path_exists(resolved_path)
        extension = resolved_path.suffix.lower() if raw_path else ""
        if extension:
            extension_counts[extension] = extension_counts.get(extension, 0) + 1
        suspected_mojibake = has_suspected_mojibake(raw_path)
        if suspected_mojibake:
            suspected_mojibake_count += 1
        display_path = raw_path
        row = {
            "index": index,
            "status": status,
            "raw_path_repr": repr(raw_path),
            "display_path": display_path,
            "resolved_absolute_path": str(resolved_path),
            "exists": exists,
            "extension": extension,
            "path_field": field,
            "suspected_mojibake": suspected_mojibake,
        }
        rows.append(row)
        if exists:
            existing_paths.append(str(resolved_path))
        else:
            missing_paths.append(str(resolved_path))
        if raw_path:
            parent = str(resolved_path.parent)
            common_parent_counts[parent] = common_parent_counts.get(parent, 0) + 1

    return {
        "manifest_path": str(path),
        "manifest_entries_loaded": len(entries),
        "encoding_used": load_result.encoding_used,
        "warning": load_result.warning,
        "status_counts": status_counts,
        "extension_counts": extension_counts,
        "path_fields_detected": {key: value for key, value in field_counts.items() if value},
        "entries": rows,
        "existing_path_count": len(existing_paths),
        "missing_path_count": len(missing_paths),
        "sample_existing_paths": existing_paths[:10],
        "sample_missing_paths": missing_paths[:10],
        "common_parent_directory_candidates": [
            {"parent": parent, "count": count}
            for parent, count in sorted(
                common_parent_counts.items(),
                key=lambda item: item[1],
                reverse=True,
            )[:10]
        ],
        "suspected_mojibake_count": suspected_mojibake_count,
    }


def build_manifest_status_diagnostics(
    resolver: ManifestStatusResolver,
    resolutions: Iterable[tuple[str, ManifestStatusResolution]],
    sample_limit: int = 10,
) -> ManifestStatusDiagnostics:
    diagnostics = resolver.empty_diagnostics()
    for source_file, resolution in resolutions:
        item = {
            "source_file": source_file,
            "status": resolution.status,
            "method": resolution.method,
            "reason": resolution.reason,
            "manifest_matched_path": resolution.manifest_matched_path,
        }
        if resolution.method == "ambiguous":
            diagnostics.ambiguous_file_count += 1
            if len(diagnostics.ambiguous_files) < sample_limit:
                diagnostics.ambiguous_files.append(item)
            continue
        if resolution.method in {"unmatched", "invalid_status"} or resolution.status == "unknown":
            diagnostics.unmatched_file_count += 1
            if resolution.method == "invalid_status":
                diagnostics.invalid_status_count += 1
            if len(diagnostics.unmatched_files) < sample_limit:
                diagnostics.unmatched_files.append(item)
            continue
        diagnostics.matched_file_count += 1
        if len(diagnostics.matched_files) < sample_limit:
            diagnostics.matched_files.append(item)
    return diagnostics


def _entry_paths(entry: Dict[str, Any]) -> List[str]:
    values: List[str] = []
    for field in MANIFEST_PATH_FIELDS:
        value = entry.get(field)
        if isinstance(value, str) and value.strip():
            values.append(value.strip())
    return values


def _first_entry_path(entry: Dict[str, Any]) -> str:
    paths = _entry_paths(entry)
    return paths[0] if paths else ""


def first_entry_path(entry: Dict[str, Any]) -> str:
    return _first_entry_path(entry)


def resolve_entry_path(entry: Dict[str, Any], manifest_parent: str | Path) -> Path:
    return _resolve_entry_path(_first_entry_path(entry), Path(manifest_parent))


def has_suspected_mojibake(value: str) -> bool:
    return any(marker in value for marker in MOJIBAKE_MARKERS)


def public_manifest_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    return {
        key: value
        for key, value in entry.items()
        if key in {*MANIFEST_PATH_FIELDS, "status", "asset_type", "confidence", "tags"}
    }


def _normalize_path_key(value: str | Path) -> str:
    raw = str(value).strip()
    if not raw:
        return ""
    normalized = raw.replace("\\", "/").strip()
    try:
        win = PureWindowsPath(normalized)
        if win.drive:
            normalized = f"{win.drive.lower()}/{('/'.join(win.parts[1:]))}"
    except ValueError:
        pass
    normalized = normalized.replace("\\", "/")
    while "//" in normalized:
        normalized = normalized.replace("//", "/")
    return normalized.rstrip("/").casefold()


def _normalize_basename(value: str | Path) -> str:
    raw = str(value).replace("\\", "/").rstrip("/")
    return raw.rsplit("/", 1)[-1].casefold()


def _relative_key(raw_path: str, base: Path) -> str:
    try:
        path = Path(raw_path).absolute()
        return _normalize_path_key(path.relative_to(base))
    except (OSError, ValueError):
        return ""


def _manifest_payload_items(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        items = payload.get("items") or payload.get("files") or payload.get("documents") or []
        return [item for item in items if isinstance(item, dict)]
    return []


def _first_present_path_field(entry: Dict[str, Any]) -> str:
    for field in MANIFEST_PATH_FIELDS:
        value = entry.get(field)
        if isinstance(value, str) and value.strip():
            return field
    return ""


def _resolve_entry_path(raw_path: str, manifest_parent: Path) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return (manifest_parent / raw_path).resolve()


def _path_exists(path: Path) -> bool:
    try:
        return path.exists() and path.is_file()
    except OSError:
        return False
