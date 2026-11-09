import boto3
import pytest
from moto import mock_aws

from shopctl import backup


@pytest.fixture
def s3(monkeypatch):
    for k in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"):
        monkeypatch.setenv(k, "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "eu-west-1")
    with mock_aws():
        c = boto3.client("s3")
        c.create_bucket(
            Bucket="shop-backups", CreateBucketConfiguration={"LocationConstraint": "eu-west-1"}
        )
        yield c


def test_archive_and_checksum(tmp_path):
    d = tmp_path / "data"
    d.mkdir()
    (d / "a.txt").write_text("hello")
    arc = backup.make_archive(d, tmp_path)
    assert arc.name.startswith("data-") and arc.suffix == ".gz"
    assert len(backup.sha256(arc)) == 64


def test_upload_stores_checksum_metadata(s3, tmp_path):
    d = tmp_path / "data"
    d.mkdir()
    (d / "a.txt").write_text("hello")
    key = backup.upload(s3, "shop-backups", d)
    head = s3.head_object(Bucket="shop-backups", Key=key)
    assert len(head["Metadata"]["sha256"]) == 64


def test_prune_keeps_newest(s3):
    for i in range(5):
        s3.put_object(Bucket="shop-backups", Key=f"backups/data-2026010{i}.tar.gz", Body=b"x")
    gone = backup.prune(s3, "shop-backups", keep=2)
    left = [
        o["Key"] for o in s3.list_objects_v2(Bucket="shop-backups", Prefix="backups/")["Contents"]
    ]
    assert left == ["backups/data-20260103.tar.gz", "backups/data-20260104.tar.gz"]
    assert len(gone) == 3


def test_prune_handles_empty_bucket(s3):
    assert backup.prune(s3, "shop-backups", keep=3) == []
