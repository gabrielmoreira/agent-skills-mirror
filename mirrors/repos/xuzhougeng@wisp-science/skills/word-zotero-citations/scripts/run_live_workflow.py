#!/usr/bin/env python3
"""Parameterized live-run tools for the word-zotero-citations Skill.

Every script in this directory is a thin, parameterized wrapper around the
generic ``zotero_mcp.word_citations`` package. None of them contains machine
paths or hard-coded user identity; all inputs come from ``--run-root``,
``--task-id``, ``--source``, ``--collection-name``, ``--style-id``, and the
environment variables ``ZOTERO_LIBRARY_ID`` / ``ZOTERO_API_KEY`` (the same
ones zotero-mcp reads).

Execution model:
- Phase A (offline): ``run_live_workflow.py candidate-build`` scans, reviews
  clusters, freezes manifest + pre-Refresh static audit, and writes the candidate.
- Phase B (authorized one-shot): ``run_live_workflow.py authorize`` freezes the
  Refresh authorization and verifies Local API visibility, then the operator
  invokes ``refresh_word_zotero.ps1`` exactly once with that authorization.
- Phase C (offline): ``run_live_workflow.py post-refresh-audit`` validates the
  wrapper report and freezes the post-Refresh static audit.
- Phase D (authorized disposable): ``validate_word_zotero_ui.ps1`` collects
  cancelled citation/bibliography dialog evidence.
- Phase E (offline): ``run_live_workflow.py finalize`` freezes UI evidence and
  the write-once finalization record.
"""

from __future__ import annotations

import argparse
import copy
import dataclasses
import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any

from zotero_mcp.cli import apply_environment_variables, load_standalone_env_vars
from zotero_mcp.client import get_web_zotero_client
from zotero_mcp.word_citations.audit import (
    audit_static_docx,
    freeze_static_audit,
    load_static_audit,
)
from zotero_mcp.word_citations.clustering import infer_citation_clusters
from zotero_mcp.word_citations.docx_build import build_candidate_docx
from zotero_mcp.word_citations.docx_scan import scan_docx
from zotero_mcp.word_citations.finalize import (
    UiEvidenceMode,
    UiFieldSnapshot,
    assemble_finalization,
    assemble_ui_evidence,
    freeze_finalization,
    freeze_ui_evidence,
    load_finalization,
    load_refresh_report,
)
from zotero_mcp.word_citations.manifest import (
    ContractPhase,
    assemble_manifest,
    freeze_manifest,
    load_manifest,
)
from zotero_mcp.word_citations.models import (
    ClusterInferenceReport,
    ClusterStatus,
    IdentifierKind,
)
from zotero_mcp.word_citations.ooxml_fields import (
    ProvisionalCitation,
    ProvisionalCitationFormat,
    ZoteroDocumentPreferences,
)
from zotero_mcp.word_citations.refresh import (
    authorize_refresh,
    freeze_refresh_authorization,
    load_refresh_authorization,
    verify_zotero_local_visibility,
)
from zotero_mcp.word_citations.zotero_stage import (
    IdentifierResolution,
    MatchStatus,
    PlanningStatus,
    StageResult,
    StageStatus,
    VisibilityReport,
    VisibleItem,
    ZoteroAuthority,
    ZoteroCollection,
    ZoteroItem,
    ZoteroLibraryIdentity,
    plan_zotero_staging,
)


def _out(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def _require_file(path: Path, label: str) -> Path:
    resolved = path.expanduser().resolve(strict=True)
    if not resolved.is_file():
        raise SystemExit(f"{label} is not a file: {resolved}")
    return resolved


def _freeze_json(path: Path, value: Any) -> None:
    payload = (json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
    if path.exists():
        if path.read_bytes() != payload:
            raise FileExistsError(f"refusing to overwrite conflicting frozen JSON: {path}")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
    hashlib.sha256(payload).hexdigest()


def _library() -> ZoteroLibraryIdentity:
    apply_environment_variables(load_standalone_env_vars())
    library_id = os.environ.get("ZOTERO_LIBRARY_ID", "").strip()
    if not library_id:
        raise SystemExit("ZOTERO_LIBRARY_ID is not configured (set it in the zotero-mcp config or environment)")
    return ZoteroLibraryIdentity("user", library_id, 1, int(library_id), None)


class _PinnedReader:
    def __init__(
        self,
        library: ZoteroLibraryIdentity,
        items: tuple[ZoteroItem, ...],
        collection_name: str,
        collection_key: str,
    ):
        self.library = library
        self.items = {item.key: item for item in items}
        self.by_doi = {item.doi: item for item in items if item.doi}
        self.collection_name = collection_name
        self.collection_key = collection_key
        self.collection = ZoteroCollection(collection_key, collection_name)

    def authority(self, *, style_id: str) -> ZoteroAuthority:
        return ZoteroAuthority(
            self.library,
            "zotero-web-api-read:user:" + self.library.library_id,
            "zotero-web-api-write:user:" + self.library.library_id,
            style_id,
        )

    def find_items(self, kind: IdentifierKind, normalized: str):
        if kind is not IdentifierKind.DOI:
            return ()
        item = self.by_doi.get(normalized)
        return (item,) if item is not None else ()

    def find_collections(self, name: str):
        return (self.collection,) if name == self.collection_name else ()

    def get_collection(self, key: str):
        return self.collection if key == self.collection_key else None

    def get_item(self, key: str):
        return self.items.get(key)


def cmd_candidate_build(args: argparse.Namespace) -> int:
    run_root = args.run_root.expanduser().resolve(strict=False)
    source = _require_file(args.source, "source")
    task_id = args.task_id
    style_id = args.style_id
    collection_name = args.collection_name
    library = _library()
    zot = get_web_zotero_client()
    if zot is None:
        raise SystemExit("configured Zotero Web API client is unavailable")

    (run_root / "input").mkdir(parents=True, exist_ok=True)
    (run_root / "output" / "documents").mkdir(parents=True, exist_ok=True)
    (run_root / "output" / "tables").mkdir(parents=True, exist_ok=True)
    protected_source = run_root / "input" / "source.docx"
    if not protected_source.exists():
        shutil.copyfile(source, protected_source)
    if protected_source.read_bytes() != source.read_bytes():
        raise SystemExit("protected source copy differs from the supplied source")

    scan = scan_docx(protected_source)
    inferred = infer_citation_clusters(scan)
    reviewed = ClusterInferenceReport.assemble(
        status=ClusterStatus.READY,
        source_sha256=inferred.source_sha256,
        clusters=tuple(dataclasses.replace(cluster, manual_review_required=False) for cluster in inferred.clusters),
        boundary_decisions=tuple(
            dataclasses.replace(decision, manual_review_required=False) for decision in inferred.boundary_decisions
        ),
    )
    if args.selection is None:
        raise SystemExit("--selection (zotero-item-selection.json) is required for candidate build")
    selection = json.loads(_require_file(args.selection, "selection").read_text(encoding="utf-8"))
    if collection_name is None:
        collection_name = selection.get("collection_name")
    collection_key = selection.get("collection_key")
    if not collection_name or not collection_key:
        raise SystemExit("selection JSON must carry collection_name and collection_key")

    items: list[ZoteroItem] = []
    evidence: list[dict[str, Any]] = []
    for row in selection["selections"]:
        key = row["selected_item_key"]
        doi = row["doi"]
        full = zot.item(key)
        data = full.get("data") or {}
        actual_key = str(full.get("key") or data.get("key") or "")
        actual_doi = str(data.get("DOI") or "").strip().casefold()
        collections = tuple(sorted(str(v) for v in data.get("collections") or ()))
        if actual_key != key or actual_doi != doi or collection_key not in collections:
            raise SystemExit(f"selected Zotero item is not visible as authorized: {doi} / {key}")
        response = zot._retrieve_data(f"users/{library.library_id}/items/{key}", {"format": "csljson"})
        payload = response.json()
        csl_rows = payload.get("items") if isinstance(payload, dict) else None
        if not isinstance(csl_rows, list) or len(csl_rows) != 1:
            raise SystemExit(f"unexpected CSL JSON response for {key}")
        item_data = copy.deepcopy(csl_rows[0])
        if str(item_data.get("DOI") or "").strip().casefold() != doi:
            raise SystemExit(f"CSL JSON DOI mismatch for {key}")
        item_data["id"] = key
        items.append(
            ZoteroItem(
                key=key,
                uri=f"http://zotero.org/users/{library.library_id}/items/{key}",
                library_id=library.library_id,
                item_type=str(data.get("itemType") or "journalArticle"),
                doi=doi,
                pmid=None,
                collections=collections,
                item_data=item_data,
            )
        )
        evidence.append(
            {
                "doi": doi,
                "item_key": key,
                "uri": items[-1].uri,
                "collections": list(collections),
                "item_data": item_data,
            }
        )
    _freeze_json(
        run_root / "output" / "tables" / "zotero-selected-item-metadata.json",
        {
            "schema_version": 1,
            "library_type": "user",
            "library_id": library.library_id,
            "collection_name": collection_name,
            "collection_key": collection_key,
            "items": evidence,
        },
    )

    reader = _PinnedReader(library, tuple(items), collection_name, collection_key)
    plan = plan_zotero_staging(scan, reviewed, reader, style_id=style_id, collection_name=collection_name)
    if plan.status is not PlanningStatus.READY:
        raise SystemExit(f"pinned stage plan did not close all gates: {plan.manual_gates} {plan.blocking_issues}")
    visible = tuple(
        VisibleItem(
            kind=res.request.kind,
            normalized=res.request.normalized,
            item_key=res.matches[0].key,
            uri=res.matches[0].uri,
        )
        for res in plan.resolutions
        if isinstance(res, IdentifierResolution) and res.status is MatchStatus.EXACT_REUSE
    )
    stage = StageResult(
        schema_version=1,
        status=StageStatus.ALREADY_VISIBLE,
        plan_sha256=plan.plan_sha256,
        collection_key=collection_key,
        visibility=VisibilityReport(True, collection_key, visible, ()),
        side_effects_performed=(),
    )
    _freeze_json(run_root / "output" / "tables" / "zotero-stage-plan-pinned.json", plan.to_dict())
    _freeze_json(run_root / "output" / "tables" / "zotero-visibility-pinned.json", stage.to_dict())

    manifest = assemble_manifest(
        task_id=task_id,
        source=protected_source,
        source_path="input/source.docx",
        scan=scan,
        clusters=reviewed,
        plan=plan,
        stage=stage,
        item_metadata=tuple(items),
    )
    manifest_path = run_root / "input" / "citation-manifest.json"
    freeze_manifest(manifest, manifest_path)
    candidate = run_root / "output" / "documents" / "candidate-pre-refresh.docx"
    provisional = tuple(
        ProvisionalCitation(
            placement.placement_id,
            f"[{index}]",
            format=ProvisionalCitationFormat.SUPERSCRIPT,
        )
        for index, placement in enumerate(manifest.placements, start=1)
    )
    build = build_candidate_docx(
        source=protected_source,
        destination=candidate,
        manifest=manifest,
        provisional_citations=provisional,
        preferences=ZoteroDocumentPreferences(
            session_id="LIVE" + task_id[-12:].replace("-", "").upper()[:12],
            zotero_version="9.0",
            style_id=style_id,
            locale="en-US",
        ),
    )
    audit = audit_static_docx(candidate, manifest, source=protected_source)
    frozen_audit = freeze_static_audit(audit, manifest, run_root / "output" / "tables" / "pre-refresh-static-audit.json")
    if not audit.passed:
        raise SystemExit(f"candidate static audit failed: {audit.acceptance.failed_checks} {audit.additional_failed_checks}")
    _out(
        {
            "task_id": task_id,
            "manifest_path": str(manifest_path),
            "manifest_sha256": manifest.manifest_sha256,
            "candidate_path": build.candidate_path,
            "candidate_size": build.candidate_size,
            "candidate_sha256": build.candidate_sha256,
            "static_audit_path": frozen_audit.path,
            "static_audit_sha256": audit.audit_sha256,
            "static_audit_passed": audit.passed,
            "citation_field_count": manifest.acceptance.citation_field_count,
            "citation_item_occurrence_count": manifest.acceptance.citation_item_occurrence_count,
            "unique_item_key_count": manifest.acceptance.unique_item_key_count,
            "bibliography_field_count": manifest.acceptance.bibliography_field_count,
        }
    )
    return 0


def cmd_authorize(args: argparse.Namespace) -> int:
    run_root = args.run_root.expanduser().resolve(strict=False)
    manifest = load_manifest(_require_file(run_root / "input" / "citation-manifest.json", "manifest"))
    audit_path = _require_file(run_root / "output" / "tables" / "pre-refresh-static-audit.json", "pre-Refresh audit")
    audit = load_static_audit(audit_path, manifest)
    authorization = authorize_refresh(
        manifest=manifest,
        manifest_path=run_root / "input" / "citation-manifest.json",
        static_audit=audit,
        static_audit_path=audit_path,
        candidate=_require_file(run_root / "output" / "documents" / "candidate-pre-refresh.docx", "candidate"),
        destination=run_root / "output" / "documents" / "refreshed-final.docx",
        report=run_root / "output" / "tables" / "refresh-report.json",
        diagnostic=run_root / "output" / "documents" / "refresh-failure-diagnostic.docx",
        run_root=run_root,
        attempt_id=args.attempt_id,
    )
    auth_path = run_root / "output" / "tables" / "refresh-authorization.json"
    frozen = freeze_refresh_authorization(authorization, auth_path)
    on_disk = load_refresh_authorization(auth_path)
    visibility = verify_zotero_local_visibility(on_disk)
    _out(
        {
            "authorization_path": frozen.path,
            "authorization_sha256": authorization.authorization_sha256,
            "visibility_ready": visibility.ready,
            "visible_item_count": len(visibility.visible_item_keys),
            "macro_name": authorization.macro_name,
            "expected_formal_refresh_count": authorization.expected_formal_refresh_count,
        }
    )
    return 0


def cmd_post_refresh_audit(args: argparse.Namespace) -> int:
    run_root = args.run_root.expanduser().resolve(strict=False)
    manifest = load_manifest(_require_file(run_root / "input" / "citation-manifest.json", "manifest"))
    auth_path = _require_file(run_root / "output" / "tables" / "refresh-authorization.json", "authorization")
    authorization = load_refresh_authorization(auth_path, require_outputs_absent=False)
    report = load_refresh_report(
        _require_file(run_root / "output" / "tables" / "refresh-report.json", "Refresh report"),
        authorization,
        authorization_path=auth_path,
    )
    if report["macro_call_count"] != 1:
        raise SystemExit("Refresh report did not record exactly one macro call")
    audit = audit_static_docx(
        _require_file(run_root / "output" / "documents" / "refreshed-final.docx", "destination"),
        manifest,
        source=Path(authorization.source_path),
        phase=ContractPhase.POST_REFRESH,
        formal_refresh_count=1,
    )
    frozen = freeze_static_audit(
        audit,
        manifest,
        run_root / "output" / "tables" / "post-refresh-static-audit.json",
        expected_phase=ContractPhase.POST_REFRESH,
    )
    if not audit.passed:
        raise SystemExit(f"post-Refresh audit failed: {audit.acceptance.failed_checks} {audit.additional_failed_checks}")
    _out(
        {
            "post_refresh_audit_path": frozen.path,
            "post_refresh_audit_sha256": audit.audit_sha256,
            "post_refresh_audit_passed": audit.passed,
            "destination_sha256": audit.document_sha256,
            "citation_field_count": audit.observation.citation_field_count,
            "citation_item_occurrence_count": audit.observation.citation_item_occurrence_count,
            "unique_item_key_count": audit.observation.unique_item_key_count,
            "bibliography_field_count": audit.observation.bibliography_field_count,
        }
    )
    return 0


def _snapshot(report: dict, key: str) -> UiFieldSnapshot:
    value = report[key]
    return UiFieldSnapshot(
        citation_field_count=int(value["citation_count"]),
        citation_item_occurrence_count=int(value["citation_item_occurrence_count"]),
        bibliography_field_count=int(value["bibliography_count"]),
        unique_citation_id_count=int(value["unique_citation_id_count"]),
        unique_item_key_count=int(value["unique_item_key_count"]),
    )


def cmd_finalize(args: argparse.Namespace) -> int:
    run_root = args.run_root.expanduser().resolve(strict=False)
    manifest = load_manifest(_require_file(run_root / "input" / "citation-manifest.json", "manifest"))
    auth_path = _require_file(run_root / "output" / "tables" / "refresh-authorization.json", "authorization")
    authorization = load_refresh_authorization(auth_path, require_outputs_absent=False)
    destination = Path(authorization.destination_path)
    source = Path(authorization.source_path)

    def _evidence(mode: UiEvidenceMode, report_path: Path, evidence_path: Path):
        report = json.loads(_require_file(report_path, f"{mode.value} UI report").read_text(encoding="utf-8"))
        if report["status"] != "pass":
            raise SystemExit(f"{mode.value} UI validation did not pass: {report.get('error')}")
        dialog = report["dialog"]
        evidence = assemble_ui_evidence(
            mode=mode,
            manifest=manifest,
            authorization=authorization,
            destination=destination,
            working_copy=Path(report["working_copy"]),
            source=source,
            macro_name=str(report["macro"]),
            dialog_process_name=str(dialog["process_name"]),
            dialog_class_name=str(dialog["class_name"]),
            recognition_signal=str(report["recognition_signal"]),
            field_snapshot_before=_snapshot(report, "field_snapshot_before"),
            field_snapshot_while_dialog_open=_snapshot(report, "field_snapshot_while_dialog_open"),
            field_snapshot_after_cancel=_snapshot(report, "field_snapshot_after_cancel"),
            destination_sha256_before=str(report["destination_sha256_before"]),
            destination_sha256_after=str(report["destination_sha256_after"]),
            working_copy_sha256_before=str(report["working_copy_sha256_before"]),
            working_copy_sha256_after=str(report["working_copy_sha256_after"]),
            source_sha256_before=str(report["source_sha256_before"]),
            source_sha256_after=str(report["source_sha256_after"]),
        )
        frozen = freeze_ui_evidence(evidence, manifest, authorization, evidence_path)
        return evidence, frozen

    _citation_evidence, frozen_citation = _evidence(
        UiEvidenceMode.CITATION,
        run_root / "output" / "tables" / "ui-citation-report.json",
        run_root / "output" / "tables" / "ui-citation-evidence.json",
    )
    _bibliography_evidence, frozen_bibliography = _evidence(
        UiEvidenceMode.BIBLIOGRAPHY,
        run_root / "output" / "tables" / "ui-bibliography-report.json",
        run_root / "output" / "tables" / "ui-bibliography-evidence.json",
    )
    finalization = assemble_finalization(
        manifest_path=run_root / "input" / "citation-manifest.json",
        authorization_path=run_root / "output" / "tables" / "refresh-authorization.json",
        refresh_report_path=run_root / "output" / "tables" / "refresh-report.json",
        post_refresh_audit_path=run_root / "output" / "tables" / "post-refresh-static-audit.json",
        citation_ui_evidence_path=run_root / "output" / "tables" / "ui-citation-evidence.json",
        bibliography_ui_evidence_path=run_root / "output" / "tables" / "ui-bibliography-evidence.json",
    )
    frozen = freeze_finalization(finalization, run_root / "output" / "tables" / "finalization.json")
    load_finalization(run_root / "output" / "tables" / "finalization.json")
    _out(
        {
            "citation_ui_evidence_path": frozen_citation.path,
            "bibliography_ui_evidence_path": frozen_bibliography.path,
            "finalization_path": frozen.path,
            "finalization_sha256": finalization.finalization_sha256,
            "created": frozen.created,
            "status": finalization.status,
            "attempt_id": finalization.attempt_id,
            "destination_sha256": finalization.destination_sha256,
        }
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("candidate-build")
    p.add_argument("--run-root", type=Path, required=True)
    p.add_argument("--task-id", required=True)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--style-id", default="http://www.zotero.org/styles/apa")
    p.add_argument("--collection-name", default=None)
    p.add_argument("--selection", type=Path, required=True)
    p.set_defaults(func=cmd_candidate_build)

    p = sub.add_parser("authorize")
    p.add_argument("--run-root", type=Path, required=True)
    p.add_argument("--attempt-id", required=True)
    p.set_defaults(func=cmd_authorize)

    p = sub.add_parser("post-refresh-audit")
    p.add_argument("--run-root", type=Path, required=True)
    p.set_defaults(func=cmd_post_refresh_audit)

    p = sub.add_parser("finalize")
    p.add_argument("--run-root", type=Path, required=True)
    p.set_defaults(func=cmd_finalize)

    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
