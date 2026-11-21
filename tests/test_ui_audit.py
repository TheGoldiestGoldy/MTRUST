import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from ui_binary_audit import EXPECTED_SHA256, sha256
from ui_frame_stats import nearest_rank, summarize
from prepare_pollymc_client import validate_polly_executable
from prepare_isolated_client import validate_destination, validate_artifact


def frames(count=120, period=0.02, start=0):
    return [{"timestamp_s": str(start + i * period), "frame_ms": "20"} for i in range(count)]


class TestUiEvidenceTools(unittest.TestCase):
    def test_nearest_rank_not_interpolation(self):
        self.assertEqual(nearest_rank([40, 10, 20, 30], .95), 40)
        self.assertEqual(nearest_rank([40, 10, 20, 30], .50), 20)

    def test_frame_time_summary_and_one_percent_low(self):
        rows = frames(101)
        rows[99]["frame_ms"] = "100"
        rows[100]["frame_ms"] = "50"
        result = summarize(rows, 0)
        self.assertEqual(result["samples"], 101)
        self.assertEqual(result["frame_ms_median"], 20)
        self.assertEqual(result["frame_ms_p95"], 20)
        self.assertEqual(result["frame_ms_p99"], 50)
        self.assertEqual(result["one_percent_low_frames"], 2)
        self.assertAlmostEqual(result["one_percent_low_fps"], 1000 / 75)
        self.assertGreater(result["capture_duration_seconds"], 1)

    def test_requires_100_post_warmup_frames(self):
        with self.assertRaisesRegex(ValueError, "100 post-warmup"):
            summarize(frames(), 1)

    def test_warmup_is_relative_to_first_timestamp(self):
        r = summarize(frames(220, start=100000), warmup_s=1)
        self.assertEqual(r["samples"], 170)

    def test_rejects_invalid_frame_duration(self):
        for bad in ("0", "-10", "NaN", "Inf", "", "nope"):
            with self.subTest(bad=bad):
                rows = frames()
                rows[99]["frame_ms"] = bad
                with self.assertRaises(ValueError):
                    summarize(rows)

    def test_rejects_invalid_timestamp(self):
        for bad in ("NaN", "Inf", "-Inf", "", "nope", "-2"):
            with self.subTest(bad=bad):
                rows = frames()
                rows[80]["timestamp_s"] = bad
                with self.assertRaises(ValueError):
                    summarize(rows)

    def test_rejects_duplicate_reverse_and_disordered_timestamps(self):
        for bad in ("0.0", "0.1", "1.58"):
            with self.subTest(bad=bad):
                rows = frames()
                rows[80]["timestamp_s"] = bad
                with self.assertRaisesRegex(ValueError, "strictly increasing"):
                    summarize(rows)

    def test_rejects_capture_gaps(self):
        rows = frames()
        for i in range(80, len(rows)):
            rows[i]["timestamp_s"] = str(float(rows[i]["timestamp_s"]) + 4)
        with self.assertRaisesRegex(ValueError, "timestamp gap"):
            summarize(rows)

    def test_rejects_short_capture_even_with_100_frames(self):
        with self.assertRaisesRegex(ValueError, "Post-warmup duration"):
            summarize(frames(150, period=0.001))
        with self.assertRaisesRegex(ValueError, "Post-warmup duration"):
            summarize(frames(150, period=0.02), min_duration_s=30)

    def test_rejects_bad_warmup_gap_and_duration_settings(self):
        for kw in ({"warmup_s": -1}, {"warmup_s": float("nan")},
                   {"max_gap_s": 0}, {"max_gap_s": float("inf")},
                   {"min_duration_s": -1}, {"min_duration_s": float("nan")}):
            with self.subTest(kwargs=kw), self.assertRaises(ValueError):
                summarize(frames(), **kw)

    def test_rejects_missing_csv_columns_and_bad_optional_metrics(self):
        for mutation in ({"timestamp_s": None}, {"frame_ms": None},
                         {"gpu_pct": "inf"}, {"cpu_pct": "-1"}, {None: "extra"}):
            rows = frames()
            rows[90].update(mutation)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                summarize(rows)

    def test_accepts_realistic_clock_offset_and_long_frame(self):
        rows = frames(200, start=3600)
        # Real 1200ms hitch counts if capture timer and duration both account for it.
        for i in range(100, len(rows)):
            rows[i]["timestamp_s"] = str(float(rows[i]["timestamp_s"]) + 1.2)
        rows[100]["frame_ms"] = "1200"
        s = summarize(rows, warmup_s=0)
        self.assertEqual(s["samples"], 200)

    def test_sha256_chunked_reader(self):
        with tempfile.TemporaryDirectory() as temp:
            f = Path(temp) / "fixture.bin"
            f.write_bytes(b"abc")
            self.assertEqual(sha256(f), "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
        self.assertEqual(len(EXPECTED_SHA256), 64)

    def test_polly_launcher_identification_rejects_fake(self):
        with tempfile.TemporaryDirectory() as temp:
            executable = Path(temp) / "AppRun"
            executable.write_text("#!/bin/sh\necho 'Not a real Minecraft launcher'\n")
            executable.chmod(0o755)
            with self.assertRaisesRegex(ValueError, "required isolated"):
                validate_polly_executable(executable)
            executable.write_text("#!/bin/sh\necho 'PollyMC --dir --launch --offline'\n")
            self.assertTrue(validate_polly_executable(executable))

    def test_client_lab_path_guard_and_hash(self):
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp) / "isolated-client"
            parent.mkdir()
            root = parent / "new"
            self.assertEqual(validate_destination(root, parent), root)
            root.mkdir()
            with self.assertRaises(FileExistsError):
                validate_destination(root, parent)
            with self.assertRaises(ValueError):
                validate_destination(Path(temp) / "outside", parent)
            f = parent / "artifact.jar"
            f.write_bytes(b"abc")
            self.assertEqual(validate_artifact(f, "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"), 3)
            with self.assertRaises(ValueError):
                validate_artifact(f, "0" * 64)


if __name__ == "__main__":
    unittest.main()
