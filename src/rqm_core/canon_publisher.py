"""Deterministic publishing support for the public RQM Canon."""

from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

CANON_RELATIVE_PATHS = (
    "docs/knowledge/RQM_Compiler_and_SU2_Geometry.md",
    "docs/knowledge/RQM_Foundations.md",
    "docs/knowledge/RQM_Glossary.md",
    "docs/knowledge/RQM_Studio_Product_Context.md",
    "docs/knowledge/RQM_vs_Standard_QM.md",
)
SANITY_QUERY = "What is Resonant Quantum Mechanics in the RQM Technologies ecosystem?"


class CanonPublishError(RuntimeError):
    """Raised when a Canon snapshot cannot be published safely."""


class OpenAIClient(Protocol):
    files: Any
    vector_stores: Any


@dataclass(frozen=True)
class CanonFile:
    path: str
    filename: str
    sha256: str
    size_bytes: int
    content: bytes

    def manifest_entry(self) -> dict[str, str | int]:
        return {
            "path": self.path,
            "filename": self.filename,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
        }


@dataclass(frozen=True)
class CanonSnapshot:
    commit: str
    manifest_sha256: str
    files: tuple[CanonFile, ...]


def committed_snapshot(repo_root: Path, ref: str = "HEAD") -> CanonSnapshot:
    """Read the exact Canon bytes stored in a Git commit."""
    root = repo_root.resolve()
    commit = _git(root, "rev-parse", "--verify", f"{ref}^{{commit}}").strip()
    files: list[CanonFile] = []
    for relative_path in CANON_RELATIVE_PATHS:
        content = _git_bytes(root, "show", f"{commit}:{relative_path}")
        files.append(
            CanonFile(
                path=relative_path,
                filename=Path(relative_path).name,
                sha256=hashlib.sha256(content).hexdigest(),
                size_bytes=len(content),
                content=content,
            )
        )
    manifest_payload = {
        "canon_version": commit,
        "files": [item.manifest_entry() for item in files],
    }
    manifest_bytes = json.dumps(
        manifest_payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return CanonSnapshot(
        commit=commit,
        manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),
        files=tuple(files),
    )


def publish_snapshot(
    client: OpenAIClient,
    snapshot: CanonSnapshot,
    *,
    output_path: Path,
) -> dict[str, Any]:
    """Create and verify a new immutable vector store for a committed snapshot."""
    short_commit = snapshot.commit[:12]
    short_manifest = snapshot.manifest_sha256[:12]
    store_name = f"rqm-canon-{short_commit}-{short_manifest}"
    vector_store = client.vector_stores.create(
        name=store_name,
        metadata={
            "rqm_canon_version": snapshot.commit,
            "manifest_sha256": snapshot.manifest_sha256,
        },
    )
    vector_store_id = _required_string(vector_store, "id")

    uploaded_files: list[dict[str, Any]] = []
    uploaded_file_ids: list[str] = []
    for canon_file in snapshot.files:
        upload = client.files.create(
            file=(canon_file.filename, io.BytesIO(canon_file.content)),
            purpose="assistants",
        )
        file_id = _required_string(upload, "id")
        uploaded_file_ids.append(file_id)
        uploaded_files.append(
            {
                "file_id": file_id,
                "attributes": {
                    "source_path": canon_file.path,
                    "source_sha256": canon_file.sha256,
                    "rqm_canon_version": snapshot.commit,
                },
            }
        )

    batch = client.vector_stores.file_batches.create_and_poll(
        vector_store_id=vector_store_id,
        files=uploaded_files,
    )
    if _value(batch, "status") != "completed":
        raise CanonPublishError("OpenAI did not complete the Canon file batch.")
    file_counts = _value(batch, "file_counts")
    failed = int(_value(file_counts, "failed") or 0)
    completed = int(_value(file_counts, "completed") or 0)
    if failed or completed != len(snapshot.files):
        raise CanonPublishError(
            f"Canon indexing completed={completed}, failed={failed}; "
            f"expected completed={len(snapshot.files)}."
        )

    search = client.vector_stores.search(
        vector_store_id=vector_store_id,
        query=SANITY_QUERY,
        max_num_results=5,
    )
    result_filenames = {
        str(_value(item, "filename"))
        for item in (_value(search, "data") or [])
        if _value(item, "filename")
    }
    expected_filenames = {item.filename for item in snapshot.files}
    if not result_filenames.intersection(expected_filenames):
        raise CanonPublishError("The published vector store failed the RQM retrieval sanity check.")

    artifact = {
        "vector_store_id": vector_store_id,
        "vector_store_name": store_name,
        "canon_version": snapshot.commit,
        "manifest_sha256": snapshot.manifest_sha256,
        "files": [
            {
                **canon_file.manifest_entry(),
                "openai_file_id": file_id,
            }
            for canon_file, file_id in zip(snapshot.files, uploaded_file_ids, strict=True)
        ],
        "sanity_query": SANITY_QUERY,
        "sanity_result_filenames": sorted(result_filenames),
    }
    _write_private_json(output_path, artifact)
    return artifact


def _write_private_json(path: Path, payload: dict[str, Any]) -> None:
    resolved = path.resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(resolved, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
    finally:
        try:
            os.chmod(resolved, 0o600)
        except OSError:
            pass


def _git(repo_root: Path, *args: str) -> str:
    return _git_bytes(repo_root, *args).decode("utf-8")


def _git_bytes(repo_root: Path, *args: str) -> bytes:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=repo_root,
            check=True,
            capture_output=True,
        ).stdout
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.decode("utf-8", errors="replace").strip()
        raise CanonPublishError(message or f"Git command failed: {' '.join(args)}") from exc


def _value(value: Any, key: str) -> Any:
    if isinstance(value, dict):
        return value.get(key)
    return getattr(value, key, None)


def _required_string(value: Any, key: str) -> str:
    result = _value(value, key)
    if not isinstance(result, str) or not result:
        raise CanonPublishError(f"OpenAI returned no {key}.")
    return result


def artifact_summary(artifact: dict[str, Any]) -> dict[str, Any]:
    """Return a log-safe publication summary without OpenAI resource IDs."""
    return {
        "vector_store_name": artifact["vector_store_name"],
        "canon_version": artifact["canon_version"],
        "manifest_sha256": artifact["manifest_sha256"],
        "file_count": len(artifact["files"]),
        "sanity_result_filenames": artifact["sanity_result_filenames"],
    }
