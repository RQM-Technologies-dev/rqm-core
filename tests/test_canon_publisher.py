from __future__ import annotations

import json
import stat
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from rqm_core.canon_publisher import (
    CANON_RELATIVE_PATHS,
    CanonPublishError,
    artifact_summary,
    committed_snapshot,
    publish_snapshot,
)


class FakeFiles:
    def __init__(self) -> None:
        self.uploaded: list[tuple[str, bytes, str]] = []

    def create(self, *, file, purpose):
        filename, stream = file
        self.uploaded.append((filename, stream.read(), purpose))
        return SimpleNamespace(id=f"file-{len(self.uploaded)}")


class FakeFileBatches:
    def __init__(self, *, status: str = "completed", failed: int = 0) -> None:
        self.status = status
        self.failed = failed
        self.request = None

    def create_and_poll(self, **kwargs):
        self.request = kwargs
        return SimpleNamespace(
            status=self.status,
            file_counts=SimpleNamespace(
                completed=len(kwargs["files"]) - self.failed,
                failed=self.failed,
            ),
        )


class FakeVectorStores:
    def __init__(
        self,
        *,
        status: str = "completed",
        failed: int = 0,
        search_filenames: tuple[str, ...] = ("RQM_Foundations.md",),
    ) -> None:
        self.file_batches = FakeFileBatches(status=status, failed=failed)
        self.search_filenames = search_filenames
        self.created = None

    def create(self, **kwargs):
        self.created = kwargs
        return SimpleNamespace(id="vs-private-test")

    def search(self, **_kwargs):
        return SimpleNamespace(
            data=[SimpleNamespace(filename=name) for name in self.search_filenames]
        )


class FakeClient:
    def __init__(self, **kwargs) -> None:
        self.files = FakeFiles()
        self.vector_stores = FakeVectorStores(**kwargs)


def test_committed_snapshot_reads_only_the_exact_canon_files() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    snapshot = committed_snapshot(repo_root)

    assert [item.path for item in snapshot.files] == list(CANON_RELATIVE_PATHS)
    assert len(snapshot.commit) == 40
    assert len(snapshot.manifest_sha256) == 64
    assert all(len(item.sha256) == 64 and item.content for item in snapshot.files)


def test_committed_snapshot_ignores_uncommitted_worktree_content(tmp_path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=repo_root, check=True)
    subprocess.run(
        ["git", "config", "user.email", "canon-test@example.com"],
        cwd=repo_root,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Canon Test"],
        cwd=repo_root,
        check=True,
    )
    for relative_path in CANON_RELATIVE_PATHS:
        path = repo_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"committed:{relative_path}\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=repo_root, check=True)
    subprocess.run(["git", "commit", "-qm", "Canon snapshot"], cwd=repo_root, check=True)
    changed_path = repo_root / CANON_RELATIVE_PATHS[0]
    changed_path.write_text("uncommitted material\n", encoding="utf-8")

    snapshot = committed_snapshot(repo_root)

    assert snapshot.files[0].content.startswith(b"committed:")
    assert b"uncommitted material" not in snapshot.files[0].content


def test_publish_snapshot_uploads_attributes_and_writes_private_artifact(tmp_path) -> None:
    snapshot = committed_snapshot(Path(__file__).resolve().parents[1])
    client = FakeClient()
    output = tmp_path / "operator" / "publish.json"

    artifact = publish_snapshot(client, snapshot, output_path=output)

    assert len(client.files.uploaded) == 5
    assert all(purpose == "assistants" for _, _, purpose in client.files.uploaded)
    batch_files = client.vector_stores.file_batches.request["files"]
    assert [item["attributes"]["source_path"] for item in batch_files] == list(
        CANON_RELATIVE_PATHS
    )
    assert stat.S_IMODE(output.stat().st_mode) == 0o600
    assert json.loads(output.read_text())["vector_store_id"] == "vs-private-test"
    assert "vector_store_id" not in artifact_summary(artifact)


@pytest.mark.parametrize(
    ("client", "message"),
    [
        (FakeClient(status="failed"), "did not complete"),
        (FakeClient(failed=1), "indexing completed"),
        (FakeClient(search_filenames=()), "sanity check"),
    ],
)
def test_publish_snapshot_fails_closed(client, message, tmp_path) -> None:
    snapshot = committed_snapshot(Path(__file__).resolve().parents[1])

    with pytest.raises(CanonPublishError, match=message):
        publish_snapshot(client, snapshot, output_path=tmp_path / "publish.json")
