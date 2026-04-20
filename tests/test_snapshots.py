import shutil
import tempfile
import unittest
from pathlib import Path

from digital_analysis.execution.snapshots import RecordingHttpClient, ReplayHttpClient, SnapshotMissError


class FakeClient:
    def get_json(self, url, *, params=None):
        return {"ok": True, "url": url, "params": params}

    def post_json(self, url, *, body=None, params=None, headers=None):
        return {"ok": True, "url": url, "body": body, "params": params}

    def get_text(self, url, *, params=None):
        return "hello world"


class SnapshotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = Path(tempfile.mkdtemp(prefix="digital_analysis_snapshots_"))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_record_and_replay_get_json(self) -> None:
        client = RecordingHttpClient(self.tmpdir, json_client=FakeClient(), text_client=FakeClient())
        payload = client.get_json("https://example.com/test", params={"a": 1})
        self.assertTrue(payload["ok"])

        replay = ReplayHttpClient(self.tmpdir)
        restored = replay.get_json("https://example.com/test", params={"a": 1})
        self.assertEqual(restored["url"], "https://example.com/test")

    def test_record_and_replay_post_json(self) -> None:
        client = RecordingHttpClient(self.tmpdir, json_client=FakeClient(), text_client=FakeClient())
        payload = client.post_json("https://example.com/post", body={"x": 1})
        self.assertTrue(payload["ok"])

        replay = ReplayHttpClient(self.tmpdir)
        restored = replay.post_json("https://example.com/post", body={"x": 1})
        self.assertEqual(restored["body"], {"x": 1})

    def test_missing_snapshot_raises(self) -> None:
        replay = ReplayHttpClient(self.tmpdir)
        with self.assertRaises(SnapshotMissError):
            replay.get_json("https://example.com/missing")


if __name__ == "__main__":
    unittest.main()
