#!/usr/bin/env python3
"""Publish the committed public RQM Canon to an immutable OpenAI vector store."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from rqm_core.canon_publisher import artifact_summary, committed_snapshot, publish_snapshot


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--ref", default="HEAD")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(".artifacts/rqm-canon-publish.json"),
        help="Private operator artifact containing the vector store ID.",
    )
    args = parser.parse_args()

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        parser.error("OPENAI_API_KEY is required.")
    try:
        from openai import OpenAI
    except ImportError:
        parser.error("Install the publisher dependency with: pip install -e '.[canon]'")

    snapshot = committed_snapshot(args.repo_root, args.ref)
    artifact = publish_snapshot(OpenAI(api_key=api_key), snapshot, output_path=args.output)
    print(json.dumps(artifact_summary(artifact), sort_keys=True))
    print(f"Private configuration artifact written to {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
