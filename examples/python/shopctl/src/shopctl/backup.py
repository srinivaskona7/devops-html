from __future__ import annotations

import hashlib
import tarfile
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


def make_archive(src: Path, workdir: Path) -> Path:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    out = workdir / f"{src.name}-{stamp}.tar.gz"
    with tarfile.open(out, "w:gz") as tar:
        tar.add(src, arcname=src.name)
    return out


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def upload(s3: S3Client, bucket: str, src: Path, keep: int = 7) -> str:
    """Archive `src`, upload with a checksum tag, prune old archives. Returns the key."""
    with tempfile.TemporaryDirectory() as tmp:
        archive = make_archive(src, Path(tmp))
        key = f"backups/{archive.name}"
        s3.upload_file(
            str(archive), bucket, key, ExtraArgs={"Metadata": {"sha256": sha256(archive)}}
        )
    prune(s3, bucket, keep)
    return key


def prune(s3: S3Client, bucket: str, keep: int) -> list[str]:
    paginator = s3.get_paginator("list_objects_v2")
    keys = sorted(
        obj["Key"]
        for page in paginator.paginate(Bucket=bucket, Prefix="backups/")
        for obj in page.get("Contents", [])
    )
    doomed = keys[:-keep] if keep > 0 else keys
    for key in doomed:
        s3.delete_object(Bucket=bucket, Key=key)
    return doomed
